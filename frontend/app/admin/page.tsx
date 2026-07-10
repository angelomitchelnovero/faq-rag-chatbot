"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import * as api from "@/lib/api";
import { ApiError, Document } from "@/lib/api";
import StatusBadge from "@/components/StatusBadge";

export default function AdminDashboard() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadDocuments = useCallback(async () => {
    try {
      const docs = await api.listDocuments();
      setDocuments(docs);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load documents.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  // Only poll while something is actively being indexed - no need to hammer
  // the API once everything has settled into "ready" or "failed".
  const hasProcessing = documents.some((d) => d.status === "processing");
  useEffect(() => {
    if (!hasProcessing) return;
    const interval = setInterval(loadDocuments, 3000);
    return () => clearInterval(interval);
  }, [hasProcessing, loadDocuments]);

  async function handleFiles(files: FileList | null) {
    if (!files || files.length === 0) return;
    const file = files[0];
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are supported right now.");
      return;
    }
    setUploading(true);
    setError(null);
    try {
      await api.uploadDocument(file);
      await loadDocuments();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function handleDelete(doc: Document) {
    if (!confirm(`Remove "${doc.filename}" from the index? This cannot be undone.`)) {
      return;
    }
    setDeletingId(doc.id);
    setError(null);
    try {
      await api.deleteDocument(doc.id);
      setDocuments((prev) => prev.filter((d) => d.id !== doc.id));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Delete failed.");
    } finally {
      setDeletingId(null);
    }
  }

  const totalChunks = documents.reduce((sum, d) => sum + d.num_chunks, 0);

  return (
    <div className="flex flex-col gap-8">
      {/* Header / stats row */}
      <div className="flex items-end justify-between">
        <div>
          <h2 className="font-[family-name:var(--font-display)] text-xl font-semibold">
            Document catalog
          </h2>
          <p className="mt-1 text-sm text-[var(--color-muted)]">
            Files here are chunked, embedded, and used to answer questions.
          </p>
        </div>
        <div className="flex gap-6 font-mono text-xs text-[var(--color-muted)]">
          <Stat label="DOCS" value={documents.length} />
          <Stat label="CHUNKS" value={totalChunks} />
        </div>
      </div>

      {/* Upload dropzone */}
      <label
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          handleFiles(e.dataTransfer.files);
        }}
        className={`focus-ring flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border border-dashed px-6 py-10 text-center transition ${
          dragOver
            ? "border-[var(--color-signal)] bg-[var(--color-signal)]/5"
            : "border-[var(--color-border)] bg-[var(--color-surface)] hover:border-[var(--color-signal)]/40"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          className="sr-only"
          onChange={(e) => handleFiles(e.target.files)}
          disabled={uploading}
        />
        <span className="font-mono text-[11px] tracking-wider text-[var(--color-signal)]">
          {uploading ? "UPLOADING…" : "DROP A PDF OR CLICK TO BROWSE"}
        </span>
        <span className="text-sm text-[var(--color-muted)]">
          It will be indexed automatically — usually takes a few seconds.
        </span>
      </label>

      {error && (
        <p
          role="alert"
          className="rounded-md border border-[var(--color-danger)]/40 bg-[var(--color-danger)]/10 px-3 py-2 text-sm text-[var(--color-danger)]"
        >
          {error}
        </p>
      )}

      {/* Document list */}
      {loading ? (
        <p className="font-mono text-sm text-[var(--color-muted)]">Loading catalog…</p>
      ) : documents.length === 0 ? (
        <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-6 py-10 text-center">
          <p className="text-sm text-[var(--color-muted)]">
            The catalog is empty. Upload a PDF above to give the assistant something to answer from.
          </p>
        </div>
      ) : (
        <ul className="flex flex-col gap-2.5">
          {documents.map((doc) => (
            <DocumentRow
              key={doc.id}
              doc={doc}
              onDelete={() => handleDelete(doc)}
              isDeleting={deletingId === doc.id}
            />
          ))}
        </ul>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex flex-col items-end">
      <span className="text-lg text-[var(--color-text)]">{value}</span>
      <span className="tracking-wider">{label}</span>
    </div>
  );
}

function DocumentRow({
  doc,
  onDelete,
  isDeleting,
}: {
  doc: Document;
  onDelete: () => void;
  isDeleting: boolean;
}) {
  const stripeColor =
    doc.status === "ready"
      ? "bg-[var(--color-ready)]"
      : doc.status === "failed"
      ? "bg-[var(--color-danger)]"
      : "bg-[var(--color-pending)]";

  return (
    <li
      className={`flex items-center gap-4 overflow-hidden rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] transition ${
        isDeleting ? "opacity-50" : ""
      }`}
    >
      <span className={`h-full w-1 self-stretch ${stripeColor}`} aria-hidden />
      <div className="flex flex-1 items-center justify-between gap-4 py-3.5 pr-4">
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-[var(--color-text)]">
            {doc.filename}
          </p>
          <p className="mt-0.5 font-mono text-[11px] text-[var(--color-muted)]">
            {doc.status === "ready"
              ? `${doc.num_chunks} chunks · `
              : ""}
            {new Date(doc.uploaded_at).toLocaleString()}
            {doc.status === "failed" && doc.error_message
              ? ` · ${doc.error_message}`
              : ""}
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-3">
          <StatusBadge status={doc.status} />
          <button
            onClick={onDelete}
            disabled={isDeleting}
            className="focus-ring rounded-md px-2 py-1 text-xs text-[var(--color-muted)] transition hover:text-[var(--color-danger)] disabled:cursor-not-allowed"
            aria-label={`Remove ${doc.filename}`}
          >
            {isDeleting ? "Removing…" : "Remove"}
          </button>
        </div>
      </div>
    </li>
  );
}
