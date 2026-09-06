import io
import re
from datetime import datetime

import pdfplumber
from pydantic import ValidationError
from supabase import Client

from app.core.config import get_settings
from app.core.errors import ExternalServiceError
from app.schemas.food_entry import FoodEntryCreate, MealType
from app.schemas.imports import ImportResult, SkippedRow
from app.services import food_service
from app.services.openai_client import extract_json_array, get_client

settings = get_settings()

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


def _rows_via_llm(pdf_bytes: bytes) -> list[dict]:
    text = _extract_text(pdf_bytes).strip()
    if not text:
        return []
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


def import_food_diary_pdf(supabase: Client, user_id: int, pdf_bytes: bytes) -> ImportResult:
    rows = _extract_tables(pdf_bytes)
    if not rows:
        rows = _rows_via_llm(pdf_bytes)

    imported = []
    skipped = []
    for row in rows:
        try:
            payload = _coerce_row(row)
        except (ValueError, ValidationError) as exc:
            skipped.append(SkippedRow(row=row, reason=str(exc)))
            continue
        entry = food_service.create_entry(supabase, user_id, payload)
        imported.append(entry)

    return ImportResult(
        imported_count=len(imported),
        entries=imported,
        skipped_rows=skipped,
    )
