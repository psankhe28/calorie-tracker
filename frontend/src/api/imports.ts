import { apiClient } from "./client";
import type { ImportResult } from "./types";

export async function importFoodDiaryPdf(file: File): Promise<ImportResult> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await apiClient.post<ImportResult>("/api/import/pdf", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}
