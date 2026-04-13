"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { api } from "@/lib/api";
import { saveSession } from "@/lib/auth";

export function LoginForm() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("admin@scopeguard.local");
  const [password, setPassword] = useState("ChangeThisNow123!");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const session =
        mode === "login"
          ? await api.login({ email, password })
          : await api.login({ email, password }).catch(async () => {
              await api.register({ email, password, role: "user" });
              return api.login({ email, password });
            });
      saveSession(session);
      router.push("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={submit} className="glass w-full max-w-lg rounded-[2rem] p-8">
      <div className="mb-6 flex gap-2 rounded-2xl border border-white/10 bg-black/10 p-1">
        {(["login", "register"] as const).map((entry) => (
          <button
            key={entry}
            type="button"
            onClick={() => setMode(entry)}
            className={`flex-1 rounded-xl px-4 py-2 text-sm capitalize transition ${
              mode === entry ? "bg-accent text-canvas" : "text-ink/70 hover:bg-white/5"
            }`}
          >
            {entry}
          </button>
        ))}
      </div>
      <label className="mb-4 block text-sm text-ink/70">
        Email
        <input
          className="mt-2 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none transition focus:border-mint/40"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          type="email"
          required
        />
      </label>
      <label className="mb-4 block text-sm text-ink/70">
        Password
        <input
          className="mt-2 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none transition focus:border-mint/40"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          type="password"
          required
        />
      </label>
      {error ? <p className="mb-4 text-sm text-danger">{error}</p> : null}
      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-2xl bg-accent px-4 py-3 font-medium text-canvas transition hover:brightness-110 disabled:opacity-60"
      >
        {loading ? "Working…" : mode === "login" ? "Sign in" : "Create account"}
      </button>
    </form>
  );
}

