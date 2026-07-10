"use client";

import { ReactNode, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function AdminLayout({ children }: { children: ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && (!user || user.role !== "admin")) {
      router.replace("/login");
    }
  }, [loading, user, router]);

  if (loading || !user || user.role !== "admin") {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="font-mono text-sm text-[var(--color-muted)]">
          Checking credentials…
        </p>
      </main>
    );
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-[var(--color-border)] bg-[var(--color-surface)]">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <div className="flex items-baseline gap-2.5">
            <h1 className="font-[family-name:var(--font-display)] text-lg font-semibold">
              Knowledge Index
            </h1>
            <span className="font-mono text-[11px] tracking-wider text-[var(--color-signal)]">
              ADMIN
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span className="font-mono text-xs text-[var(--color-muted)]">
              {user.email}
            </span>
            <button
              onClick={() => {
                logout();
                router.push("/login");
              }}
              className="focus-ring rounded-md border border-[var(--color-border)] px-3 py-1.5 text-xs text-[var(--color-muted)] transition hover:border-[var(--color-danger)]/50 hover:text-[var(--color-danger)]"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>
      <div className="mx-auto max-w-5xl px-6 py-10">{children}</div>
    </div>
  );
}
