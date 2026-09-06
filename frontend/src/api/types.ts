export type MealType = "breakfast" | "lunch" | "dinner" | "snack";

export interface FoodEntry {
  id: number;
  user_id: number;
  meal_type: MealType;
  food_name: string;
  quantity: number;
  unit: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  micros: Record<string, number>;
  logged_at: string;
}

export interface FoodEntryInput {
  meal_type: MealType;
  food_name: string;
  quantity: number;
  unit: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  micros: Record<string, number>;
  logged_at: string;
}

export interface Page<T> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
}

export interface Goal {
  id: number;
  user_id: number;
  calorie_target: number;
  protein_target_g: number;
  carb_target_g: number;
  fat_target_g: number;
  weight_goal_kg: number | null;
  created_at: string;
}

export interface GoalInput {
  calorie_target: number;
  protein_target_g: number;
  carb_target_g: number;
  fat_target_g: number;
  weight_goal_kg: number | null;
}

export interface DailyCalories {
  date: string;
  calories: number;
}

export interface MacroBreakdownDay {
  date: string;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
}

export interface MicroNutrient {
  nutrient: string;
  total: number;
}

export interface GoalVsActualMetric {
  metric: string;
  goal: number;
  actual: number;
}

export interface NutritionExtraction {
  food_name: string;
  quantity: number;
  unit: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  micros: Record<string, number>;
  confidence_note: string | null;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface SkippedRow {
  row: unknown;
  reason: string;
}

export interface ImportResult {
  id: number;
  imported_count: number;
  entries: FoodEntry[];
  skipped_rows: SkippedRow[];
}

export interface PdfImportSummary {
  id: number;
  file_name: string;
  imported_count: number;
  skipped_count: number;
  created_at: string;
}

export interface PdfImportDetail {
  id: number;
  file_name: string;
  imported_count: number;
  entries: FoodEntry[];
  skipped_rows: SkippedRow[];
  created_at: string;
}
