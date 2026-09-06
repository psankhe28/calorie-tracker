import hashlib
import io
import re
import uuid
from datetime import datetime

import pdfplumber
from pydantic import ValidationError
from supabase import Client

from app.core.config import get_settings
from app.core.errors import ConflictError, ExternalServiceError, InvalidFileError, NotFoundError
from app.schemas.food_entry import FoodEntryCreate, MealType
from app.schemas.imports import ImportResult, PdfImportDetail, PdfImportSummary, SkippedRow
from app.services import food_service
from app.services.openai_client import extract_json_array, get_client

settings = get_settings()

_BUCKET = "pdf-imports"
_bucket_ready = False


def _ensure_bucket(supabase: Client) -> None:
    """Create the storage bucket on first use. Idempotent -- if it already exists this just
    swallows the resulting error, since supabase-py has no clean "create if not exists"."""
    global _bucket_ready
    if _bucket_ready:
        return
    try:
        supabase.storage.create_bucket(_BUCKET, options={"public": False})
    except Exception:
        pass
    _bucket_ready = True

# Maps canonical field -> header keywords we'll match against (case-insensitive, substring).
_HEADER_ALIASES: dict[str, list[str]] = {
    "logged_at": ["date", "time"],
    "meal_type": ["meal"],
    "food_name": ["food", "item", "name", "description"],
    "quantity": ["qty", "quantity", "amount"],
    "unit": ["unit"],
    "calories": ["calorie", "kcal"],
    "protein_g": ["protein"],
    "carbs_g": ["carb"],
    "fat_g": ["fat"],
}

_LLM_PROMPT = """The following text was extracted from a user's exported food diary / nutrition \
history PDF. Extract every food entry you can find as a JSON array. Each element must have exactly \
this shape:
{{"logged_at": "YYYY-MM-DD or ISO datetime", "meal_type": "breakfast|lunch|dinner|snack", \
"food_name": string, "quantity": number, "unit": string, "calories": number, "protein_g": number, \
"carbs_g": number, "fat_g": number}}
If meal type isn't stated, use your best guess from context or default to "snack". If a numeric \
field is missing, use 0. Respond with ONLY the JSON array, no prose, no markdown fences.

TEXT:
{text}"""

# A random PDF (resume, invoice, ebook, ...) is very unlikely to hit several of these; a real
# food/nutrition diary export almost always mentions calories/macros plus meal-related terms.
_FOOD_DIARY_KEYWORDS = [
    "calorie",
    "kcal",
    "protein",
    "carb",
    "fat",
    "fiber",
    "sugar",
    "breakfast",
    "lunch",
    "dinner",
    "snack",
    "meal",
    "nutrition",
    "diet",
    "macros",
    "serving",
    "food diary",
    "food log",
]
_MIN_FOOD_DIARY_KEYWORD_MATCHES = 3


def _looks_like_food_diary(text: str) -> bool:
    lowered = text.lower()
    matches = sum(1 for keyword in _FOOD_DIARY_KEYWORDS if keyword in lowered)
    return matches >= _MIN_FOOD_DIARY_KEYWORD_MATCHES


def _match_header(header: str) -> str | None:
    header_lower = header.strip().lower()
    for canonical, keywords in _HEADER_ALIASES.items():
        if any(keyword in header_lower for keyword in keywords):
            return canonical
    return None


def _extract_tables(pdf_bytes: bytes) -> list[dict]:
    rows: list[dict] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                if not table or len(table) < 2:
                    continue
                header_map = {i: _match_header(h or "") for i, h in enumerate(table[0])}
                if "food_name" not in header_map.values() or "calories" not in header_map.values():
                    continue  # not a recognizable food-diary table
                for raw_row in table[1:]:
                    row = {header_map[i]: value for i, value in enumerate(raw_row) if header_map.get(i)}
                    if row:
                        rows.append(row)
    return rows


def _extract_text(pdf_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def _rows_via_llm(text: str) -> list[dict]:
    client = get_client()
    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            max_tokens=4096,
            messages=[{"role": "user", "content": _LLM_PROMPT.format(text=text[:15000])}],
        )
    except Exception as exc:
        raise ExternalServiceError(f"AI-assisted PDF parsing failed: {exc}") from exc

    reply = response.choices[0].message.content or ""
    return extract_json_array(reply)


# Matches a leading number (optionally decimal) followed by whatever descriptive text remains,
# e.g. "1 bowl (200g)" -> ("1", "bowl (200g)"), "150g" -> ("150", "g"), "1.5 cup" -> ("1.5", "cup").
_LEADING_NUMBER = re.compile(r"^\s*([\d]+(?:\.\d+)?)\s*(.*)$")


def _parse_quantity(raw: str) -> tuple[float, str]:
    """Real food-diary exports often describe quantity in natural units ("1 bowl (200g)",
    "2 pcs", "1 scoop + water") rather than a bare number. Pull out the leading number as the
    quantity and keep the rest as the unit description; fall back to quantity=1 with the whole
    string as the unit when there's no leading number at all."""
    text = raw.strip()
    match = _LEADING_NUMBER.match(text)
    if match:
        return float(match.group(1)), (match.group(2).strip() or "serving")
    return 1.0, (text or "serving")


def _num(row: dict, key: str, default: float = 0) -> float:
    value = row.get(key, default)
    if value in (None, ""):
        return default
    text = str(value).replace(",", "").strip()
    try:
        return float(text)
    except ValueError:
        match = _LEADING_NUMBER.match(text)
        if match:
            return float(match.group(1))
        return default


def _coerce_row(row: dict) -> FoodEntryCreate:
    logged_at_raw = str(row.get("logged_at") or datetime.now().isoformat())
    try:
        logged_at = datetime.fromisoformat(logged_at_raw)
    except ValueError:
        logged_at = datetime.strptime(logged_at_raw, "%Y-%m-%d")

    meal_type_raw = str(row.get("meal_type") or "snack").strip().lower()
    meal_type = MealType(meal_type_raw) if meal_type_raw in MealType._value2member_map_ else MealType.snack

    unit_raw = row.get("unit")
    quantity_raw = row.get("quantity")
    if quantity_raw not in (None, ""):
        quantity, inferred_unit = _parse_quantity(str(quantity_raw))
    else:
        quantity, inferred_unit = 1.0, "serving"
    unit = str(unit_raw).strip() if unit_raw not in (None, "") else inferred_unit

    return FoodEntryCreate(
        meal_type=meal_type,
        food_name=str(row.get("food_name") or "Unknown item").strip(),
        quantity=quantity,
        unit=unit or "serving",
        calories=_num(row, "calories"),
        protein_g=_num(row, "protein_g"),
        carbs_g=_num(row, "carbs_g"),
        fat_g=_num(row, "fat_g"),
        logged_at=logged_at,
    )


def _find_duplicate_import(supabase: Client, user_id: int, file_hash: str) -> dict | None:
    result = (
        supabase.table("pdf_imports")
        .select("id, file_name, created_at")
        .eq("user_id", user_id)
        .eq("file_hash", file_hash)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def _row_signature(payload: FoodEntryCreate) -> tuple:
    return (
        payload.food_name.strip().lower(),
        payload.meal_type,
        round(payload.calories, 1),
        payload.logged_at.isoformat(),
    )


def import_food_diary_pdf(supabase: Client, user_id: int, file_name: str, pdf_bytes: bytes) -> ImportResult:
    file_hash = hashlib.sha256(pdf_bytes).hexdigest()
    duplicate = _find_duplicate_import(supabase, user_id, file_hash)
    if duplicate is not None:
        raise ConflictError(
            f"This exact PDF was already imported as '{duplicate['file_name']}' on "
            f"{duplicate['created_at']}. Re-upload only if you meant to import it again."
        )

    rows = _extract_tables(pdf_bytes)
    if not rows:
        # No recognizable food table -- before burning an LLM call (and storing the file), make
        # sure this is actually a food/nutrition diary and not an arbitrary PDF.
        text = _extract_text(pdf_bytes).strip()
        if not text:
            raise InvalidFileError(
                "Couldn't read any text from this PDF. Please upload a text-based food diary "
                "export rather than a scanned image."
            )
        if not _looks_like_food_diary(text):
            raise InvalidFileError(
                "This PDF doesn't look like a food diary or nutrition log. Please upload a "
                "food/calorie tracking export."
            )
        rows = _rows_via_llm(text)

    imported = []
    skipped = []
    seen_signatures: set[tuple] = set()
    for row in rows:
        try:
            payload = _coerce_row(row)
        except (ValueError, ValidationError) as exc:
            skipped.append(SkippedRow(row=row, reason=str(exc)))
            continue
        signature = _row_signature(payload)
        if signature in seen_signatures:
            skipped.append(SkippedRow(row=row, reason="Duplicate entry: identical to another row in this PDF"))
            continue
        seen_signatures.add(signature)
        entry = food_service.create_entry(supabase, user_id, payload)
        imported.append(entry)

    _ensure_bucket(supabase)
    storage_path = f"{user_id}/{uuid.uuid4()}_{file_name}"
    try:
        supabase.storage.from_(_BUCKET).upload(
            storage_path, pdf_bytes, {"content-type": "application/pdf"}
        )
    except Exception as exc:
        raise ExternalServiceError(f"Failed to store the uploaded PDF: {exc}") from exc

    record = (
        supabase.table("pdf_imports")
        .insert(
            {
                "user_id": user_id,
                "file_name": file_name,
                "storage_path": storage_path,
                "file_hash": file_hash,
                "imported_count": len(imported),
                "extracted_entries": imported,
                "skipped_rows": [s.model_dump() for s in skipped],
            }
        )
        .execute()
    )

    return ImportResult(
        id=record.data[0]["id"],
        imported_count=len(imported),
        entries=imported,
        skipped_rows=skipped,
    )


def list_pdf_imports(supabase: Client, user_id: int) -> list[PdfImportSummary]:
    result = (
        supabase.table("pdf_imports")
        .select("id, file_name, imported_count, skipped_rows, created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return [
        PdfImportSummary(
            id=row["id"],
            file_name=row["file_name"],
            imported_count=row["imported_count"],
            skipped_count=len(row["skipped_rows"] or []),
            created_at=row["created_at"],
        )
        for row in result.data
    ]


def _get_pdf_import_row(supabase: Client, user_id: int, import_id: int) -> dict:
    result = (
        supabase.table("pdf_imports")
        .select("*")
        .eq("id", import_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise NotFoundError("PDF import not found")
    return result.data[0]


def get_pdf_import_detail(supabase: Client, user_id: int, import_id: int) -> PdfImportDetail:
    row = _get_pdf_import_row(supabase, user_id, import_id)
    return PdfImportDetail(
        id=row["id"],
        file_name=row["file_name"],
        imported_count=row["imported_count"],
        entries=row["extracted_entries"],
        skipped_rows=row["skipped_rows"],
        created_at=row["created_at"],
    )


def get_pdf_import_file(supabase: Client, user_id: int, import_id: int) -> tuple[bytes, str]:
    """Returns (pdf_bytes, file_name) for the original upload, after verifying ownership."""
    row = _get_pdf_import_row(supabase, user_id, import_id)
    try:
        pdf_bytes = supabase.storage.from_(_BUCKET).download(row["storage_path"])
    except Exception as exc:
        raise ExternalServiceError(f"Failed to retrieve the stored PDF: {exc}") from exc
    return pdf_bytes, row["file_name"]
