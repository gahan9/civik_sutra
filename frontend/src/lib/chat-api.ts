import type { ChatRequest, ChatResponse } from "../types/chat";

export type ElectionTimelineEvent = {
  id: string;
  title: string;
  stage: string;
  starts_on: string;
  ends_on: string;
  description: string;
  source: string;
  source_url: string;
};

export type ElectionTimelineResponse = {
  events: ElectionTimelineEvent[];
  count: number;
};

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
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

export async function getQuickQuestions(language: string = "en"): Promise<string[]> {
  const response = await fetch(
    `/assistant/questions?language=${encodeURIComponent(language)}`
  );

  if (!response.ok) {
    return [];
  }

  const data = (await response.json()) as { questions: string[] };
  return data.questions;
}

export async function getElectionTimeline(
  stage?: string
): Promise<ElectionTimelineEvent[]> {
  const url = stage
    ? `/assistant/timeline?stage=${encodeURIComponent(stage)}`
    : "/assistant/timeline";
  const response = await fetch(url);

  if (!response.ok) {
    return [];
  }

  const data = (await response.json()) as ElectionTimelineResponse;
  return data.events ?? [];
}

export type SupportedLanguage = "en" | "hi" | "ta" | "te" | "bn" | "mr" | "gu" | "kn";

export type TranslateRequestBody = {
  text: string;
  target_language: SupportedLanguage;
  source_language?: SupportedLanguage;
};

export type TranslateResponseBody = {
  text: string;
  target_language: SupportedLanguage;
  source_language?: SupportedLanguage | null;
};

export async function translateDynamicContent(
  request: TranslateRequestBody
): Promise<string> {
  if (!request.text.trim()) {
    return request.text;
  }
  if (request.source_language && request.source_language === request.target_language) {
    return request.text;
  }

  try {
    const response = await fetch("/assistant/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      return request.text;
    }

    const data = (await response.json()) as TranslateResponseBody;
    return data.text || request.text;
  } catch {
    return request.text;
  }
}
