import type { ChatRequest, ChatResponse } from "../types/chat";


export async function sendChatMessage(
  request: ChatRequest,
): Promise<ChatResponse> {
  const response = await fetch("/assistant/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Chat request failed with status ${response.status}`);
  }

  return response.json() as Promise<ChatResponse>;
}

export async function getQuickQuestions(
  language: string = "en",
): Promise<string[]> {
  const response = await fetch(
    `/assistant/questions?language=${encodeURIComponent(language)}`,
  );

  if (!response.ok) {
    return [];
  }

  const data = (await response.json()) as { questions: string[] };
  return data.questions;
}
