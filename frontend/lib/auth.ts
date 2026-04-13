"use client";

const STORAGE_KEY = "scopeguard-session";

export function saveSession(session: unknown) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

export function getSession<T>() {
  const raw = localStorage.getItem(STORAGE_KEY);
  return raw ? (JSON.parse(raw) as T) : null;
}

export function clearSession() {
  localStorage.removeItem(STORAGE_KEY);
}

export function getToken() {
  const session = getSession<{ access_token: string }>();
  return session?.access_token ?? "";
}

