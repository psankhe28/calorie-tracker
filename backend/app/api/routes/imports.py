from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import Response
from supabase import Client

from app.api.deps import get_current_user
from app.core.auth_user import AuthUser
from app.core.supabase import get_supabase
from app.schemas.imports import ImportResult, PdfImportDetail, PdfImportSummary
from app.services.pdf_import import (
    get_pdf_import_detail,
    get_pdf_import_file,
    import_food_diary_pdf,
    list_pdf_imports,
)

router = APIRouter(prefix="/api/import", tags=["import"])

_MAX_PDF_BYTES = 15 * 1024 * 1024


@router.post("/pdf", response_model=ImportResult)
async def import_pdf(
    file: UploadFile,
    supabase: Client = Depends(get_supabase),
    current_user: AuthUser = Depends(get_current_user),
) -> ImportResult:
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Expected a PDF file, got '{file.content_type}'",
        )

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")
    if len(pdf_bytes) > _MAX_PDF_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="PDF exceeds 15MB limit")

    return import_food_diary_pdf(supabase, current_user.id, file.filename or "upload.pdf", pdf_bytes)


@router.get("/pdf", response_model=list[PdfImportSummary])
def get_pdf_imports(
    supabase: Client = Depends(get_supabase),
    current_user: AuthUser = Depends(get_current_user),
) -> list[PdfImportSummary]:
    return list_pdf_imports(supabase, current_user.id)


@router.get("/pdf/{import_id}", response_model=PdfImportDetail)
def get_pdf_import(
    import_id: int,
    supabase: Client = Depends(get_supabase),
    current_user: AuthUser = Depends(get_current_user),
) -> PdfImportDetail:
    return get_pdf_import_detail(supabase, current_user.id, import_id)


@router.get("/pdf/{import_id}/file")
def get_pdf_import_original_file(
    import_id: int,
    supabase: Client = Depends(get_supabase),
    current_user: AuthUser = Depends(get_current_user),
) -> Response:
    pdf_bytes, file_name = get_pdf_import_file(supabase, current_user.id, import_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{file_name}"'},
    )
