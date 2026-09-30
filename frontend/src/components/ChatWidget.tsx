import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from "react";
import { sendChatMessage } from "../api/chat";
import { getApiErrorMessage } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { ChatMessage } from "../api/types";
import { AI_FEATURES_ENABLED } from "../config";
import { ChatIcon } from "./icons";
import { MarkdownLite } from "./MarkdownLite";

const SUGGESTIONS = ["Summarize my week", "What are my goals?", "Log a banana, 105 calories"];
// Mirrors _MAX_USER_MESSAGES in backend/app/services/chat_agent.py; assistant replies don't count.
const MAX_USER_MESSAGES = 5;

export function ChatWidget() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const windowRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = windowRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [history, isSending, isOpen]);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
  }, [input]);

  if (!user || !AI_FEATURES_ENABLED) return null;

  const limitReached = history.filter((m) => m.role === "user").length >= MAX_USER_MESSAGES;

  async function submitMessage(message: string) {
    if (!message || isSending || limitReached) return;
    setError(null);
    setInput("");
    setHistory((prev) => [...prev, { role: "user", content: message }]);
    setIsSending(true);
    try {
      const response = await sendChatMessage(message, history);
      setHistory(response.history);
    } catch (err) {
      setError(getApiErrorMessage(err));
      setHistory((prev) => prev.slice(0, -1));
      setInput(message);
    } finally {
      setIsSending(false);
    }
  }

  function startNewChat() {
    setHistory([]);
    setError(null);
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    void submitMessage(input.trim());
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void submitMessage(input.trim());
    }
  }

  return (
    <div className="chat-widget">
      {isOpen && (
        <div className="chat-widget-panel card">
          <div className="chat-widget-header">
            <div className="chat-widget-header-info">
              <span className="chat-widget-avatar">
                <ChatIcon />
              </span>
              <div>
                <div className="chat-widget-title">Nutrition Assistant</div>
                <div className="chat-widget-subtitle">
                  <span className="chat-widget-status-dot" />
                  Online
                </div>
              </div>
            </div>
            <button type="button" className="icon-btn" aria-label="Close chat" onClick={() => setIsOpen(false)}>
              ×
            </button>
          </div>
          {error && <div className="error-banner">{error}</div>}
          <div className="chat-window" ref={windowRef}>
            {history.length === 0 && (
              <div className="chat-empty-state">
                <p className="muted">
                  Ask about your meals, goals, or nutrition — or try one of these:
                </p>
                <div className="chat-suggestions">
                  {SUGGESTIONS.map((suggestion) => (
                    <button
                      key={suggestion}
                      type="button"
                      className="chat-suggestion-chip"
                      onClick={() => void submitMessage(suggestion)}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}
            {history.map((message, index) => (
              <div key={index} className={`chat-row ${message.role}`}>
                {message.role === "assistant" && <span className="chat-avatar">AI</span>}
                <div className={`chat-message ${message.role}`}>
                  {message.role === "assistant" ? (
                    <MarkdownLite content={message.content} />
                  ) : (
                    message.content
                  )}
                </div>
              </div>
            ))}
            {isSending && (
              <div className="chat-row assistant">
                <span className="chat-avatar">AI</span>
                <div className="chat-message assistant chat-typing">
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            )}
          </div>
          {limitReached && !isSending ? (
            <div className="chat-limit-notice">
              <span className="muted">This chat has reached its {MAX_USER_MESSAGES}-message limit.</span>
              <button type="button" className="btn" onClick={startNewChat}>
                New chat
              </button>
            </div>
          ) : (
            <form className="chat-input-row" onSubmit={handleSubmit}>
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about your meals, goals, or log something..."
                disabled={isSending}
                rows={1}
              />
              <button
                className="btn chat-send-btn"
                type="submit"
                disabled={isSending || !input.trim()}
                aria-label="Send message"
              >
                <SendIcon />
              </button>
            </form>
          )}
        </div>
      )}

      <button
        type="button"
        className="chat-widget-fab"
        aria-label={isOpen ? "Close chat" : "Open chat"}
        onClick={() => setIsOpen((prev) => !prev)}
      >
        {isOpen ? "×" : <ChatIcon />}
      </button>
    </div>
  );
}

function SendIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 2 11 13" />
      <path d="M22 2 15 22l-4-9-9-4 20-7Z" />
    </svg>
  );
}
