import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 px-4 text-center">
      <p className="font-mono text-[11px] tracking-widest text-[var(--color-signal)]">
        KNOWLEDGE INDEX
      </p>
      <h1 className="font-[family-name:var(--font-display)] text-3xl font-semibold text-[var(--color-text)]">
        The chat assistant lives here next.
      </h1>
      <p className="max-w-sm text-sm text-[var(--color-muted)]">
        The public FAQ chat interface is built in the next step. For now, admins
        can sign in to manage the document catalog.
      </p>
      <Link
        href="/login"
        className="focus-ring mt-2 rounded-md bg-[var(--color-signal)] px-4 py-2.5 font-[family-name:var(--font-display)] text-sm font-semibold text-[var(--color-ink)] transition hover:brightness-110"
      >
        Admin sign in
      </Link>
    </main>
  );
}
