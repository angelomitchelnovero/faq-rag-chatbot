"use client";

import { useState } from "react";
import { ChatSource, getDownloadUrl } from "@/lib/api";

export interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
  isError?: boolean;
}

// Chroma's cosine distance is 0 (identical) to 2 (opposite). Convert to a
// friendlier 0-100% "match" score for display, clamped to a sane range.
function matchPercent(distance: number): number {
  const similarity = 1 - distance / 2;
  return Math.round(Math.max(0, Math.min(1, similarity)) * 100);
}

export default function ChatMessage({ message }: { message: Message }) {
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const isUser = message.role === "user";
  const sortedSources = message.sources
    ? [...message.sources].sort((a, b) => a.distance - b.distance)
    : [];

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`flex max-w-[85%] flex-col gap-1.5 ${isUser ? "items-end" : "items-start"}`}>
        <div
          className={`rounded-lg px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${
            isUser
              ? "bg-[var(--color-signal)] text-[var(--color-ink)]"
              : message.isError
              ? "border border-[var(--color-danger)]/40 bg-[var(--color-danger)]/10 text-[var(--color-danger)]"
              : "border border-[var(--color-border)] bg-[var(--color-surface)] text-[var(--color-text)]"
          }`}
        >
          {message.content}
        </div>

        {!isUser && sortedSources.length > 0 && (
          <div className="w-full">
            <button
              onClick={() => setSourcesOpen((v) => !v)}
              className="focus-ring flex items-center gap-1.5 rounded px-1 font-mono text-[11px] tracking-wider text-[var(--color-muted)] hover:text-[var(--color-signal)]"
            >
              <span>{sourcesOpen ? "▾" : "▸"}</span>
              {sortedSources.length} SOURCE
              {sortedSources.length > 1 ? "S" : ""}
            </button>

            {sourcesOpen && (
              <div className="mt-2 flex flex-col gap-2">
                {sortedSources.map((s, i) => (
                  <div
                    key={i}
                    className="rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <p className="truncate font-mono text-[11px] text-[var(--color-signal)]">
                        {s.filename}
                      </p>
                      <span className="shrink-0 font-mono text-[10px] text-[var(--color-muted)]">
                        {matchPercent(s.distance)}% match
                      </span>
                    </div>
                    <p className="mt-1 line-clamp-3 text-xs text-[var(--color-muted)]">
                      {s.text}
                    </p>
                    {s.document_id && (
                      <a
                        href={getDownloadUrl(s.document_id)}
                        download={s.filename}
                        className="focus-ring mt-2 inline-flex items-center gap-1 font-mono text-[10px] tracking-wider text-[var(--color-signal)] hover:underline"
                      >
                        ↓ DOWNLOAD PDF
                      </a>
                    )}
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
