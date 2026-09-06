from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.api.deps import get_current_user
from app.core.auth_user import AuthUser
from app.schemas.ai import NutritionExtraction
from app.services import ai_vision

router = APIRouter(prefix="/api/ai", tags=["ai"])

_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
_MAX_IMAGE_BYTES = 10 * 1024 * 1024


@router.post("/extract-nutrition", response_model=NutritionExtraction)
def extract_nutrition(
    file: UploadFile,
    current_user: AuthUser = Depends(get_current_user),
) -> NutritionExtraction:
    if file.content_type not in _ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported image type '{file.content_type}'. Allowed: {', '.join(sorted(_ALLOWED_TYPES))}",
        )

    image_bytes = file.file.read()
    if not image_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")
    if len(image_bytes) > _MAX_IMAGE_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Image exceeds 10MB limit")

    return ai_vision.extract_nutrition_from_image(image_bytes, file.content_type)
