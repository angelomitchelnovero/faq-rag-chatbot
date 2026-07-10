"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { ApiError } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const { login, register } = useAuth();

  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [adminCode, setAdminCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const user =
        mode === "login"
          ? await login(email, password)
          : await register(email, password, adminCode);

      router.push(user.role === "admin" ? "/admin" : "/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-sm">
        {/* Signature: index-card tab above the form */}
        <div className="mb-0 ml-4 inline-block rounded-t-md border border-b-0 border-[var(--color-border)] bg-[var(--color-surface-raised)] px-3 py-1">
          <span className="font-mono text-[11px] tracking-widest text-[var(--color-signal)]">
            {mode === "login" ? "ACCESS · 01" : "ENROLL · 01"}
          </span>
        </div>

        <div className="rounded-lg rounded-tl-none border border-[var(--color-border)] bg-[var(--color-surface)] p-8 shadow-[0_0_0_1px_rgba(94,234,212,0.04)]">
          <h1 className="font-[family-name:var(--font-display)] text-2xl font-semibold text-[var(--color-text)]">
            Knowledge Index
          </h1>
          <p className="mt-1.5 text-sm text-[var(--color-muted)]">
            {mode === "login"
              ? "Sign in to manage the document catalog."
              : "Create an account to access the catalog."}
          </p>

          <form onSubmit={handleSubmit} className="mt-7 flex flex-col gap-4">
            <Field
              label="Email"
              type="email"
              value={email}
              onChange={setEmail}
              autoComplete="email"
              required
            />
            <Field
              label="Password"
              type="password"
              value={password}
              onChange={setPassword}
              autoComplete={mode === "login" ? "current-password" : "new-password"}
              required
            />

            {mode === "register" && (
              <Field
                label="Admin code (optional)"
                type="password"
                value={adminCode}
                onChange={setAdminCode}
                hint="Leave blank to register as a regular user."
              />
            )}

            {error && (
              <p
                role="alert"
                className="rounded-md border border-[var(--color-danger)]/40 bg-[var(--color-danger)]/10 px-3 py-2 text-sm text-[var(--color-danger)]"
              >
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="focus-ring mt-2 rounded-md bg-[var(--color-signal)] px-4 py-2.5 font-[family-name:var(--font-display)] text-sm font-semibold text-[var(--color-ink)] transition hover:brightness-110 disabled:opacity-50"
            >
              {submitting
                ? "Please wait…"
                : mode === "login"
                ? "Sign in"
                : "Create account"}
            </button>
          </form>

          <button
            onClick={() => {
              setError(null);
              setMode(mode === "login" ? "register" : "login");
            }}
            className="focus-ring mt-6 w-full text-center text-sm text-[var(--color-muted)] underline decoration-dotted underline-offset-4 hover:text-[var(--color-text)]"
          >
            {mode === "login"
              ? "Need an account? Register"
              : "Already have an account? Sign in"}
          </button>
        </div>
      </div>
    </main>
  );
}

function Field({
  label,
  type,
  value,
  onChange,
  autoComplete,
  required,
  hint,
}: {
  label: string;
  type: string;
  value: string;
  onChange: (v: string) => void;
  autoComplete?: string;
  required?: boolean;
  hint?: string;
}) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="font-mono text-[11px] uppercase tracking-wider text-[var(--color-muted)]">
        {label}
      </span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        autoComplete={autoComplete}
        required={required}
        className="focus-ring rounded-md border border-[var(--color-border)] bg-[var(--color-surface-raised)] px-3 py-2 text-sm text-[var(--color-text)] placeholder:text-[var(--color-muted)]"
      />
      {hint && <span className="text-xs text-[var(--color-muted)]">{hint}</span>}
    </label>
  );
}
