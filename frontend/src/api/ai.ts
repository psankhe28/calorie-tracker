import { apiClient } from "./client";
import type { NutritionExtraction } from "./types";

export async function extractNutritionFromImage(file: File): Promise<NutritionExtraction> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await apiClient.post<NutritionExtraction>("/api/ai/extract-nutrition", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}
