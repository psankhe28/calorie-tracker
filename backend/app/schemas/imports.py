from pydantic import BaseModel

from app.schemas.food_entry import FoodEntryResponse


class SkippedRow(BaseModel):
    row: dict | str
    reason: str


class ImportResult(BaseModel):
    imported_count: int
    entries: list[FoodEntryResponse]
    skipped_rows: list[SkippedRow]
