import { useCallback, useEffect, useRef, useState } from "react";

import { getQuickQuestions, sendChatMessage } from "../../lib/chat-api";
import type { ChatMessage, SourceCitation, ToolCallRecord } from "../../types/chat";


function generateSessionId(): string {
  return `sess_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export function AssistantChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(generateSessionId);
  const [quickQuestions, setQuickQuestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getQuickQuestions("en").then(setQuickQuestions).catch(() => {});
  }, []);

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
          language: "en",
        });

        const assistantMessage: ChatMessage = {
          role: "assistant",
          content: response.response,
          citations: response.citations,
          tool_calls: response.tool_calls,
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } catch {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content:
              "I'm sorry, I couldn't process your question right now. " +
              "Please try again or visit eci.gov.in for official information.",
          },
        ]);
      } finally {
        setLoading(false);
      }
    },
    [loading, sessionId],
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend(input);
      }
    },
    [handleSend, input],
  );

  return (
    <div className="shell">
      <section className="hero">
        <p className="eyebrow">Election Assistant</p>
        <h1>Ask CivikSutra</h1>
        <p>
          Your AI-powered guide to the Indian election process. Ask about
          voting procedures, documents, candidates, and more.
        </p>
      </section>

      <section className="chat-container">
        {messages.length === 0 && quickQuestions.length > 0 && (
          <div className="quick-questions">
            <p className="quick-questions-label">Quick Questions:</p>
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
                msg.role === "user" ? "chat-msg chat-msg--user" : "chat-msg chat-msg--assistant"
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
              <div className="chat-msg-content chat-typing">
                Thinking...
              </div>
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
            placeholder="Type your question..."
            disabled={loading}
            aria-label="Chat message input"
          />
          <button
            type="button"
            onClick={() => handleSend(input)}
            disabled={!input.trim() || loading}
          >
            Send
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
          <span className="chat-tool-icon">🔧</span>
          <span>{tc.result_summary}</span>
        </div>
      ))}
    </div>
  );
}
