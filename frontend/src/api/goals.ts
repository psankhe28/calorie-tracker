import { apiClient } from "./client";
import type { Goal, GoalInput } from "./types";

export async function getGoal(): Promise<Goal> {
  const { data } = await apiClient.get<Goal>("/api/goals");
  return data;
}

export async function upsertGoal(input: GoalInput): Promise<Goal> {
  const { data } = await apiClient.put<Goal>("/api/goals", input);
  return data;
}

export async function getGoalHistory(): Promise<Goal[]> {
  const { data } = await apiClient.get<Goal[]>("/api/goals/history");
  return data;
}
