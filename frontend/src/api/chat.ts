import { apiClient } from "./client";
import type { ChatMessage } from "./types";

export interface ChatResponse {
  reply: string;
  history: ChatMessage[];
}

export async function sendChatMessage(message: string, history: ChatMessage[]): Promise<ChatResponse> {
  const { data } = await apiClient.post<ChatResponse>("/api/chat", { message, history });
  return data;
}
