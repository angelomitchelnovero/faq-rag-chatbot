"use client";

import { useState } from "react";
import { ChatSource } from "@/lib/api";

export interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
  isError?: boolean;
}

export default function ChatMessage({ message }: { message: Message }) {
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`flex max-w-[85%] flex-col gap-1.5 ${isUser ? "items-end" : "items-start"}`}>
        <div
          className={`rounded-lg px-4 py-2.5 text-sm leading-relaxed ${
            isUser
              ? "bg-[var(--color-signal)] text-[var(--color-ink)]"
              : message.isError
              ? "border border-[var(--color-danger)]/40 bg-[var(--color-danger)]/10 text-[var(--color-danger)]"
              : "border border-[var(--color-border)] bg-[var(--color-surface)] text-[var(--color-text)]"
          }`}
        >
          {message.content}
        </div>

        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="w-full">
            <button
              onClick={() => setSourcesOpen((v) => !v)}
              className="focus-ring flex items-center gap-1.5 rounded px-1 font-mono text-[11px] tracking-wider text-[var(--color-muted)] hover:text-[var(--color-signal)]"
            >
              <span>{sourcesOpen ? "▾" : "▸"}</span>
              {message.sources.length} SOURCE
              {message.sources.length > 1 ? "S" : ""}
            </button>

            {sourcesOpen && (
              <div className="mt-2 flex flex-col gap-2">
                {message.sources.map((s, i) => (
                  <div
                    key={i}
                    className="rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2"
                  >
                    <p className="font-mono text-[11px] text-[var(--color-signal)]">
                      {s.filename}
                    </p>
                    <p className="mt-1 line-clamp-3 text-xs text-[var(--color-muted)]">
                      {s.text}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
