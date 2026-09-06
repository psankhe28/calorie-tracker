from datetime import datetime

from pydantic import BaseModel

from app.schemas.food_entry import FoodEntryResponse


class SkippedRow(BaseModel):
    row: dict | str
    reason: str


class ImportResult(BaseModel):
    id: int
    imported_count: int
    entries: list[FoodEntryResponse]
    skipped_rows: list[SkippedRow]


class PdfImportSummary(BaseModel):
    id: int
    file_name: str
    imported_count: int
    skipped_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PdfImportDetail(BaseModel):
    id: int
    file_name: str
    imported_count: int
    entries: list[FoodEntryResponse]
    skipped_rows: list[SkippedRow]
    created_at: datetime
