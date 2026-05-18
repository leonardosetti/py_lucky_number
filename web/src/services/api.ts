"use client";

// Lucky Number API client — JWT auth, CSRF, error handling
// Prevents CWE-522: credentials via env vars (NEXT_PUBLIC_API_URL)

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface ApiOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

let token: string | null = null;

export function setAuthToken(newToken: string | null) {
  token = newToken;
  if (newToken) {
    localStorage.setItem("jwt", newToken);
  } else {
    localStorage.removeItem("jwt");
  }
}

export function getStoredToken(): string | null {
  if (token) return token;
  const stored = localStorage.getItem("jwt");
  if (stored) token = stored;
  return token;
}

export async function apiRequest<T = unknown>(endpoint: string, options: ApiOptions = {}): Promise<T> {
  const { method = "GET", body, headers = {} } = options;

  // Prevents CWE-522: JWT from storage, never hardcoded
  const jwt = getStoredToken();
  if (jwt) {
    headers["Authorization"] = `Bearer ${jwt}`;
  }

  // Prevents CWE-352: CSRF token for mutations
  if (body && method !== "GET") {
    const csrf = localStorage.getItem("csrf_token");
    if (csrf) {
      headers["X-CSRF-Token"] = csrf;
    }
  }

  const config: RequestInit = { method, headers: { "Content-Type": "application/json", ...headers } };
  if (body) {
    config.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_URL}${endpoint}`, config);

  if (!response.ok) {
    if (response.status === 401) {
      setAuthToken(null);
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorData.detail || `Erro ${response.status}`);
  }

  // Handle CSV/PDF downloads differently
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("text/csv") || contentType.includes("application/pdf")) {
    return response as unknown as T;
  }

  return response.json() as Promise<T>;
}

// ---- Auth ----

export const auth = {
  register: (email: string, password: string, nome?: string) =>
    apiRequest<{ access_token: string }>("/auth/register", {
      method: "POST",
      body: { email, password, nome },
    }),
  login: (email: string, password: string) =>
    apiRequest<{ access_token: string; token_type: string }>("/auth/login", {
      method: "POST",
      body: { email, password },
    }),
  refresh: () => apiRequest<{ access_token: string }>("/auth/refresh"),
  logout: () => apiRequest<{ message: string }>("/auth/logout"),
};

// ---- Features ----

export const features = {
  list: () => apiRequest<Array<{ slug: string; nome: string; ativa: boolean }>>("/admin/features"),
  toggle: (slug: string) => apiRequest<{ slug: string; ativa: boolean }>(`/admin/features/${slug}`, { method: "PUT" }),
};

// ---- Bets ----

export const bets = {
  generate: (jogo: string, quantidade_apostas: number, dezenas_por_aposta: number) =>
    apiRequest<{ jogo: string; apostas: number[][]; valor_total: number }>("/gerar-apostas", {
      method: "POST",
      body: { jogo, quantidade_apostas, dezenas_por_aposta },
    }),
};

// ---- Combinations ----

export const combinacoes = {
  list: (page = 1, jogo?: string) =>
    apiRequest<Array<{ id: string; jogo: string; dezenas: number[]; favorita: boolean }>>(
      `/combinacoes?page=${page}${jogo ? `&jogo=${jogo}` : ""}`
    ),
  save: (jogo: string, dezenas: number[], dezenas_por_aposta: number) =>
    apiRequest("/combinacoes", { method: "POST", body: { jogo, dezenas, dezenas_por_aposta } }),
  delete: (id: string) => apiRequest(`/combinacoes/${id}`, { method: "DELETE" }),
  toggleFavorite: (id: string) => apiRequest(`/combinacoes/${id}/favorita`, { method: "PUT" }),
};

// ---- Promises ----

export const promessas = {
  list: (page = 1) => apiRequest<Array<{ id: string; titulo: string; valor_total: number }>>(`/promessas?page=${page}`),
  create: (titulo: string, valor_total: number, combinacoes: unknown[]) =>
    apiRequest("/promessas", { method: "POST", body: { titulo, valor_total, combinacoes } }),
  delete: (id: string) => apiRequest(`/promessas/${id}`, { method: "DELETE" }),
  clone: (id: string) => apiRequest(`/promessas/${id}/clone`, { method: "POST" }),
  share: (id: string) => apiRequest<{ link: string }>(`/promessas/${id}/compartilhar`, { method: "POST" }),
};

// ---- Notifications ----

export const notifications = {
  list: (page = 1) => apiRequest(`/notifications?page=${page}`),
  markRead: (id: string) => apiRequest(`/notifications/${id}/read`, { method: "PUT" }),
};

// ---- Dashboard ----

export const dashboard = {
  summary: () => apiRequest<{ total_usuarios: number; total_apostas: number; total_promessas: number }>("/admin/dashboard/summary"),
  events: (eventType?: string) => apiRequest(`/admin/dashboard/events${eventType ? `?event_type=${eventType}` : ""}`),
};

// ---- Export ----

export const exportApi = {
  csv: () => apiRequest("/export/csv"),
  json: () => apiRequest("/export/json"),
  pdf: () => apiRequest("/export/pdf"),
  whatsapp: () => apiRequest<{ link: string }>("/share/whatsapp"),
  clipboard: () => apiRequest<string>("/share/clipboard"),
};
