import { apiClient } from "./client";
import type { FoodEntry, FoodEntryInput, MealType, Page } from "./types";

export interface ListFoodEntriesParams {
  startDate?: string;
  endDate?: string;
  mealType?: MealType;
  page?: number;
  pageSize?: number;
}

export async function listFoodEntries(params: ListFoodEntriesParams): Promise<Page<FoodEntry>> {
  const { data } = await apiClient.get<Page<FoodEntry>>("/api/food-entries", {
    params: {
      start_date: params.startDate,
      end_date: params.endDate,
      meal_type: params.mealType,
      page: params.page ?? 1,
      page_size: params.pageSize ?? 20,
    },
  });
  return data;
}

export async function createFoodEntry(input: FoodEntryInput): Promise<FoodEntry> {
  const { data } = await apiClient.post<FoodEntry>("/api/food-entries", input);
  return data;
}

export async function updateFoodEntry(id: number, input: FoodEntryInput): Promise<FoodEntry> {
  const { data } = await apiClient.put<FoodEntry>(`/api/food-entries/${id}`, input);
  return data;
}

export async function deleteFoodEntry(id: number): Promise<void> {
  await apiClient.delete(`/api/food-entries/${id}`);
}
