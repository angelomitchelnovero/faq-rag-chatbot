"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import Link from "next/link";
import * as api from "@/lib/api";
import { ApiError } from "@/lib/api";
import ChatMessage, { Message } from "@/components/ChatMessage";
import TypingIndicator from "@/components/TypingIndicator";

const SUGGESTED_QUESTIONS = [
  "What are your business hours?",
  "How do I reset my password?",
  "Do you offer refunds?",
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage(question: string) {
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setInput("");
    setLoading(true);

    try {
      const res = await api.askQuestion(trimmed);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.answer, sources: res.sources },
      ]);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Something went wrong reaching the assistant. Please try again.";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: message, isError: true },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    sendMessage(input);
  }

  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="border-b border-[var(--color-border)] bg-[var(--color-surface)]">
        <div className="mx-auto flex max-w-2xl items-center justify-between px-6 py-4">
          <div className="flex items-baseline gap-2.5">
            <h1 className="font-[family-name:var(--font-display)] text-lg font-semibold">
              Knowledge Index
            </h1>
            <span className="font-mono text-[11px] tracking-wider text-[var(--color-muted)]">
              ASK ANYTHING
            </span>
          </div>
          <Link
            href="/login"
            className="focus-ring font-mono text-[11px] tracking-wider text-[var(--color-muted)] hover:text-[var(--color-signal)]"
          >
            ADMIN →
          </Link>
        </div>
      </header>

      {/* Message list */}
      <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col px-6 py-8">
        {messages.length === 0 ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-6 text-center">
            <div>
              <p className="font-mono text-[11px] tracking-widest text-[var(--color-signal)]">
                READY
              </p>
              <h2 className="mt-2 font-[family-name:var(--font-display)] text-2xl font-semibold text-[var(--color-text)]">
                What can I help you find?
              </h2>
              <p className="mt-2 text-sm text-[var(--color-muted)]">
                Answers are pulled directly from our knowledge base.
              </p>
            </div>
            <div className="flex flex-wrap justify-center gap-2">
              {SUGGESTED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="focus-ring rounded-full border border-[var(--color-border)] bg-[var(--color-surface)] px-3.5 py-1.5 text-xs text-[var(--color-muted)] transition hover:border-[var(--color-signal)]/40 hover:text-[var(--color-text)]"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex flex-1 flex-col gap-4">
            {messages.map((m, i) => (
              <ChatMessage key={i} message={m} />
            ))}
            {loading && <TypingIndicator />}
            <div ref={bottomRef} />
          </div>
        )}
      </main>

      {/* Input bar */}
      <form
        onSubmit={handleSubmit}
        className="border-t border-[var(--color-border)] bg-[var(--color-surface)]"
      >
        <div className="mx-auto flex max-w-2xl items-center gap-3 px-6 py-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question…"
            disabled={loading}
            className="focus-ring flex-1 rounded-md border border-[var(--color-border)] bg-[var(--color-surface-raised)] px-4 py-2.5 text-sm text-[var(--color-text)] placeholder:text-[var(--color-muted)] disabled:opacity-60"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="focus-ring rounded-md bg-[var(--color-signal)] px-4 py-2.5 font-[family-name:var(--font-display)] text-sm font-semibold text-[var(--color-ink)] transition hover:brightness-110 disabled:opacity-40"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}