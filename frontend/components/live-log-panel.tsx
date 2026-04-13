"use client";

import { useEffect, useState } from "react";

import { API_BASE_URL } from "@/lib/config";

type LogItem = {
  id: number;
  level: string;
  message: string;
  created_at: string;
};

export function LiveLogPanel({
  scanId,
  token,
}: {
  scanId: string;
  token: string;
}) {
  const [logs, setLogs] = useState<LogItem[]>([]);

  useEffect(() => {
    const wsUrl = `${API_BASE_URL.replace("http", "ws")}/ws/scans/${scanId}?token=${token}`;
    const socket = new WebSocket(wsUrl);
    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data) as LogItem;
      setLogs((current) =>
        current.some((item) => item.id === payload.id) ? current : [...current, payload]
      );
    };
    return () => socket.close();
  }, [scanId, token]);

  return (
    <div className="glass rounded-3xl p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold">Live Logs</h3>
        <span className="rounded-full border border-mint/30 bg-mint/10 px-3 py-1 text-xs text-mint">
          WebSocket
        </span>
      </div>
      <div className="max-h-96 space-y-3 overflow-auto rounded-2xl bg-black/20 p-4 font-[var(--font-mono)] text-xs">
        {logs.length === 0 ? (
          <p className="text-ink/50">Waiting for worker output…</p>
        ) : (
          logs.map((log) => (
            <div key={log.id} className="rounded-xl border border-white/5 bg-white/5 p-3">
              <p className="text-mint">{new Date(log.created_at).toLocaleString()}</p>
              <p className="mt-1 text-ink/70">{log.level}</p>
              <p className="mt-1 text-ink">{log.message}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

