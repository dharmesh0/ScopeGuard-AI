import { API_BASE_URL } from "./config";
import type {
  DashboardStats,
  Engagement,
  Plugin,
  Report,
  Scan,
  User,
} from "./types";

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    cache: "no-store",
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || `Request failed: ${response.status}`);
  }

  if (response.headers.get("Content-Type")?.includes("application/json")) {
    return (await response.json()) as T;
  }

  return (await response.text()) as T;
}

export const api = {
  register: (payload: { email: string; password: string; role?: "admin" | "user" }) =>
    request<User>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  login: (payload: { email: string; password: string }) =>
    request<User>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  me: (token: string) => request("/api/v1/auth/me", {}, token),
  dashboard: (token: string) =>
    request<DashboardStats>("/api/v1/scans/dashboard", {}, token),
  scans: (token: string) => request<Scan[]>("/api/v1/scans", {}, token),
  scan: (id: string, token: string) =>
    request<Scan>(`/api/v1/scans/${id}`, {}, token),
  createScan: (
    payload: {
      engagement_id: string;
      target: string;
      human_in_the_loop: boolean;
      attestation: string;
    },
    token: string
  ) =>
    request<Scan>("/api/v1/scans", {
      method: "POST",
      body: JSON.stringify(payload),
    }, token),
  resumeScan: (id: string, token: string) =>
    request<Scan>(`/api/v1/scans/${id}/resume`, { method: "POST" }, token),
  plugins: (token: string) =>
    request<Plugin[]>("/api/v1/plugins", {}, token),
  engagements: (token: string) =>
    request<Engagement[]>("/api/v1/engagements", {}, token),
  createEngagement: (
    payload: {
      name: string;
      description: string;
      scope: string[];
      approval_mode: boolean;
    },
    token: string
  ) =>
    request<Engagement>("/api/v1/engagements", {
      method: "POST",
      body: JSON.stringify(payload),
    }, token),
  latestCves: (token: string) =>
    request<{ id: string; description: string }[]>(
      "/api/v1/intelligence/latest-cves",
      {},
      token
    ),
  report: (scanId: string, token: string) =>
    request<Report>(`/api/v1/reports/scan/${scanId}`, {}, token),
  reportMarkdown: (scanId: string, token: string) =>
    request<string>(`/api/v1/reports/scan/${scanId}/markdown`, {}, token),
};
