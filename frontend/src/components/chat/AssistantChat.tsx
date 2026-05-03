import { useCallback, useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import {
  getQuickQuestions,
  sendChatMessage,
  translateDynamicContent,
} from "../../lib/chat-api";
import type { SupportedLanguage } from "../../lib/chat-api";
import type { ChatMessage, SourceCitation, ToolCallRecord } from "../../types/chat";

function generateSessionId(): string {
  return `sess_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export function AssistantChat() {
  const { t, i18n } = useTranslation();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(generateSessionId);
  const [quickQuestions, setQuickQuestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getQuickQuestions(i18n.language)
      .then(setQuickQuestions)
      .catch(() => {});
  }, [i18n.language]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || loading) return;

      const userMessage: ChatMessage = { role: "user", content: trimmed };
      setMessages((prev) => [...prev, userMessage]);
      setInput("");
      setLoading(true);

      try {
        const response = await sendChatMessage({
          message: trimmed,
          session_id: sessionId,
          language: i18n.language,
        });

        const SUPPORTED_LANGS = new Set([
          "en",
          "hi",
          "ta",
          "te",
          "bn",
          "mr",
          "gu",
          "kn",
        ]);
        let displayContent = response.response;
        const lang = i18n.language;
        if (SUPPORTED_LANGS.has(lang) && lang !== "en") {
          displayContent = await translateDynamicContent({
            text: response.response,
            target_language: lang as SupportedLanguage,
            source_language: "en",
          });
        }

        const assistantMessage: ChatMessage = {
          role: "assistant",
          content: displayContent,
          originalContent: response.response,
          citations: response.citations,
          tool_calls: response.tool_calls,
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } catch {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: t("chat.errorResponse"),
          },
        ]);
      } finally {
        setLoading(false);
      }
    },
    [loading, sessionId, i18n.language, t]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend(input);
      }
    },
    [handleSend, input]
  );

  return (
    <div className="shell">
      <section className="hero">
        <p className="eyebrow">{t("nav.chat")}</p>
        <h1>{t("chat.title")}</h1>
        <p>{t("chat.subtitle")}</p>
      </section>

      <section className="chat-container">
        {messages.length === 0 && quickQuestions.length > 0 && (
          <div className="quick-questions">
            <p className="quick-questions-label">{t("chat.quickQuestions")}</p>
            <div className="quick-questions-grid">
              {quickQuestions.slice(0, 6).map((q, idx) => (
                <button
                  key={idx}
                  type="button"
                  className="quick-question-btn"
                  onClick={() => handleSend(q)}
                  disabled={loading}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={
                msg.role === "user"
                  ? "chat-msg chat-msg--user"
                  : "chat-msg chat-msg--assistant"
              }
            >
              <div className="chat-msg-role">
                {msg.role === "user" ? "You" : "CivikSutra"}
              </div>
              <div className="chat-msg-content">
                {msg.content.split("\n").map((line, i) => (
                  <p key={i}>{line}</p>
                ))}
              </div>
              {msg.role === "assistant" &&
                (!msg.citations || msg.citations.length === 0) &&
                (!msg.tool_calls || msg.tool_calls.length === 0) && (
                  <p className="chat-msg-no-sources" role="note">
                    {t("chat.noWebCitations")}
                  </p>
                )}
              {msg.citations && msg.citations.length > 0 && (
                <CitationList citations={msg.citations} />
              )}
              {msg.tool_calls && msg.tool_calls.length > 0 && (
                <ToolCallList toolCalls={msg.tool_calls} />
              )}
            </div>
          ))}

          {loading && (
            <div className="chat-msg chat-msg--assistant">
              <div className="chat-msg-role">CivikSutra</div>
              <div className="chat-msg-content chat-typing">{t("chat.thinking")}</div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-bar">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={t("chat.placeholder")}
            disabled={loading}
            aria-label="Chat message input"
          />
          <button
            type="button"
            onClick={() => handleSend(input)}
            disabled={!input.trim() || loading}
          >
            {t("chat.send")}
          </button>
        </div>
      </section>
    </div>
  );
}

function CitationList({ citations }: { citations: SourceCitation[] }) {
  return (
    <div className="chat-citations">
      {citations.map((c, idx) => (
        <span key={idx} className="chat-citation">
          {c.url ? (
            <a href={c.url} target="_blank" rel="noopener noreferrer">
              {c.source}
            </a>
          ) : (
            c.source
          )}
        </span>
      ))}
    </div>
  );
}

function ToolCallList({ toolCalls }: { toolCalls: ToolCallRecord[] }) {
  return (
    <div className="chat-tool-calls">
      {toolCalls.map((tc, idx) => (
        <div key={idx} className="chat-tool-call">
          <span className="chat-tool-label">{tc.tool_name}</span>
          <span className="chat-tool-summary">{tc.result_summary}</span>
        </div>
      ))}
    </div>
  );
}
