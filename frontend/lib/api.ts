/**
 * API client for the FAQ RAG Chatbot backend.
 *
 * Reads the backend URL from NEXT_PUBLIC_API_URL (see .env.local.example).
 * Attaches the stored auth token (if any) to every request.
 */
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: HeadersInit = {
    ...(options.body && !(options.body instanceof FormData)
      ? { "Content-Type": "application/json" }
      : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch {
      // response wasn't JSON; fall back to statusText
    }
    throw new ApiError(res.status, detail);
  }

  // Some endpoints (e.g. DELETE) may return no content
  const text = await res.text();
  return text ? JSON.parse(text) : (undefined as T);
}

// ---- Types ----

export type UserRole = "admin" | "user";

export interface User {
  id: string;
  email: string;
  role: UserRole;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export type DocumentStatus = "processing" | "ready" | "failed";

export interface Document {
  id: string;
  filename: string;
  status: DocumentStatus;
  num_chunks: number;
  error_message: string | null;
  uploaded_at: string;
}

export interface ChatSource {
  filename: string;
  text: string;
  distance: number;
  document_id: string;
}

export function getDownloadUrl(documentId: string): string {
  return `${API_URL}/documents/${documentId}/download`;
}

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
}

// ---- Auth ----

export function login(email: string, password: string) {
  return request<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function register(
  email: string,
  password: string,
  adminSignupCode?: string
) {
  return request<AuthResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify({
      email,
      password,
      admin_signup_code: adminSignupCode || undefined,
    }),
  });
}

export function getMe() {
  return request<User>("/auth/me");
}

// ---- Documents (admin only) ----

export function listDocuments() {
  return request<Document[]>("/documents");
}

export function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return request<Document>("/documents/upload", {
    method: "POST",
    body: formData,
  });
}

export function deleteDocument(id: string) {
  return request<{ status: string; id: string }>(`/documents/${id}`, {
    method: "DELETE",
  });
}

// ---- Chat (public) ----

export function askQuestion(question: string) {
  return request<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}
