import { DocumentStatus } from "@/lib/api";

const STYLES: Record<DocumentStatus, { label: string; className: string }> = {
  processing: {
    label: "INDEXING",
    className: "text-[var(--color-pending)] border-[var(--color-pending)]",
  },
  ready: {
    label: "INDEXED",
    className: "text-[var(--color-ready)] border-[var(--color-ready)]",
  },
  failed: {
    label: "FAILED",
    className: "text-[var(--color-danger)] border-[var(--color-danger)]",
  },
};

export default function StatusBadge({ status }: { status: DocumentStatus }) {
  const s = STYLES[status];
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 font-mono text-[11px] tracking-wider ${s.className}`}
    >
      {status === "processing" && (
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-current" />
      )}
      {s.label}
    </span>
  );
}
