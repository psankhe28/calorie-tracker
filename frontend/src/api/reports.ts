import { apiClient } from "./client";
import type { DailyCalories, GoalVsActualMetric, MacroBreakdownDay, MicroNutrient } from "./types";

export interface ReportRangeParams {
  startDate?: string;
  endDate?: string;
}

function toParams(range: ReportRangeParams) {
  return { start_date: range.startDate, end_date: range.endDate };
}

export async function getWeeklyCalories(range: ReportRangeParams): Promise<DailyCalories[]> {
  const { data } = await apiClient.get<{ days: DailyCalories[] }>("/api/reports/weekly-calories", {
    params: toParams(range),
  });
  return data.days;
}

export async function getMacroBreakdown(range: ReportRangeParams): Promise<MacroBreakdownDay[]> {
  const { data } = await apiClient.get<{ days: MacroBreakdownDay[] }>("/api/reports/macros", {
    params: toParams(range),
  });
  return data.days;
}

export async function getMicroSummary(range: ReportRangeParams): Promise<MicroNutrient[]> {
  const { data } = await apiClient.get<{ nutrients: MicroNutrient[] }>("/api/reports/micros", {
    params: toParams(range),
  });
  return data.nutrients;
}

export async function getGoalVsActual(range: ReportRangeParams): Promise<GoalVsActualMetric[]> {
  const { data } = await apiClient.get<{ metrics: GoalVsActualMetric[] }>("/api/reports/goal-vs-actual", {
    params: toParams(range),
  });
  return data.metrics;
}
