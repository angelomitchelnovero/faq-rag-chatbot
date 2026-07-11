"use client";

import { useEffect, useState } from "react";
import * as api from "@/lib/api";
import { ApiError, Document } from "@/lib/api";

export default function EditDocumentModal({
  doc,
  onClose,
  onSaved,
}: {
  doc: Document;
  onClose: () => void;
  onSaved: (updated: Document) => void;
}) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getRawText(doc.id)
      .then((res) => setText(res.text))
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "Failed to load text.")
      )
      .finally(() => setLoading(false));
  }, [doc.id]);

  async function handleSave() {
    setSaving(true);
    setError(null);
    try {
      const updated = await api.updateRawText(doc.id, text);
      onSaved(updated);
      onClose();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to save changes.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="flex max-h-[85vh] w-full max-w-2xl flex-col overflow-hidden rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)]"
      >
        <div className="flex items-center justify-between border-b border-[var(--color-border)] px-5 py-4">
          <div>
            <h3 className="font-[family-name:var(--font-display)] text-base font-semibold text-[var(--color-text)]">
              Edit source text
            </h3>
            <p className="mt-0.5 truncate font-mono text-[11px] text-[var(--color-muted)]">
              {doc.filename}
            </p>
          </div>
          <button
            onClick={onClose}
            className="focus-ring rounded px-2 py-1 text-[var(--color-muted)] hover:text-[var(--color-text)]"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4">
          <p className="mb-3 text-xs text-[var(--color-muted)]">
            Editing this text re-indexes the document and regenerates its PDF.
            The new PDF will be a clean, plain reflow of this text — not a
            copy of the original file&apos;s layout, fonts, or images.
          </p>

          {loading ? (
            <p className="font-mono text-sm text-[var(--color-muted)]">Loading…</p>
          ) : (
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              disabled={saving}
              rows={16}
              className="focus-ring w-full resize-y rounded-md border border-[var(--color-border)] bg-[var(--color-surface-raised)] px-3 py-2.5 font-mono text-sm leading-relaxed text-[var(--color-text)] disabled:opacity-60"
            />
          )}

          {error && (
            <p
              role="alert"
              className="mt-3 rounded-md border border-[var(--color-danger)]/40 bg-[var(--color-danger)]/10 px-3 py-2 text-sm text-[var(--color-danger)]"
            >
              {error}
            </p>
          )}
        </div>

        <div className="flex items-center justify-end gap-3 border-t border-[var(--color-border)] px-5 py-4">
          <button
            onClick={onClose}
            disabled={saving}
            className="focus-ring rounded-md px-3 py-2 text-sm text-[var(--color-muted)] hover:text-[var(--color-text)] disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={loading || saving || !text.trim()}
            className="focus-ring rounded-md bg-[var(--color-signal)] px-4 py-2 font-[family-name:var(--font-display)] text-sm font-semibold text-[var(--color-ink)] transition hover:brightness-110 disabled:opacity-40"
          >
            {saving ? "Saving…" : "Save & re-index"}
          </button>
        </div>
      </div>
    </div>
  );
}
