"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { AppShell } from "@/components/shell";
import { LiveLogPanel } from "@/components/live-log-panel";
import { api } from "@/lib/api";
import { getToken } from "@/lib/auth";
import type { Report, Scan } from "@/lib/types";

export default function ScanDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [scan, setScan] = useState<Scan | null>(null);
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState("");
  const token = getToken();

  useEffect(() => {
    if (!token) {
      router.push("/login");
      return;
    }

    const load = () => {
      api.scan(params.id, token)
        .then((scanData) => {
          setScan(scanData);
          if (scanData.status === "completed") {
            api.report(params.id, token).then(setReport).catch(() => setReport(null));
          }
        })
        .catch((err) => setError(err instanceof Error ? err.message : "Failed to load scan."));
    };

    load();
    const timer = window.setInterval(load, 5000);
    return () => window.clearInterval(timer);
  }, [params.id, router, token]);

  return (
    <AppShell
      title="Assessment Detail"
      subtitle="Monitor the worker lifecycle, review findings as they arrive, and move from approval to reporting without losing context."
    >
      {error ? (
        <div className="mb-6 rounded-3xl border border-danger/30 bg-danger/10 p-4 text-sm text-danger">
          {error}
        </div>
      ) : null}
      <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <div className="space-y-6">
          <section className="glass rounded-3xl p-6">
            <p className="font-[var(--font-mono)] text-sm text-mint">{scan?.target ?? "Loading target…"}</p>
            <div className="mt-4 flex flex-wrap gap-3">
              <span className="rounded-full border border-accent/20 bg-accent/10 px-3 py-1 text-xs text-accent">
                Status: {scan?.status ?? "…"}
              </span>
              <span className="rounded-full border border-mint/20 bg-mint/10 px-3 py-1 text-xs text-mint">
                Approval: {scan?.approval_status ?? "…"}
              </span>
            </div>
            <p className="mt-5 text-sm text-ink/75">{scan?.summary || "Summary will appear after the analysis agent finishes."}</p>
            {scan?.status === "waiting_for_approval" ? (
              <button
                type="button"
                onClick={() => api.resumeScan(params.id, token).then(setScan).catch((err) => setError(String(err)))}
                className="mt-5 rounded-2xl border border-white/10 px-4 py-3 text-sm text-ink/80 hover:bg-white/5"
              >
                Attempt resume after approval
              </button>
            ) : null}
            {report ? (
              <Link
                href={`/reports/${params.id}`}
                className="mt-5 inline-flex rounded-2xl bg-accent px-4 py-3 text-sm font-medium text-canvas"
              >
                Open report
              </Link>
            ) : null}
          </section>
          <section className="glass rounded-3xl p-6">
            <h2 className="text-2xl font-semibold">Findings</h2>
            <div className="mt-4 space-y-4">
              {scan?.findings?.length ? (
                scan.findings.map((finding) => (
                  <div key={finding.id} className="rounded-3xl border border-white/10 bg-white/5 p-5">
                    <div className="flex items-center justify-between gap-4">
                      <h3 className="text-lg font-medium">{finding.title}</h3>
                      <span className="rounded-full border border-white/10 px-3 py-1 text-xs uppercase text-ink/70">
                        {finding.severity}
                      </span>
                    </div>
                    <p className="mt-3 text-sm text-ink/70">{finding.description}</p>
                    <p className="mt-3 text-sm text-mint">Remediation: {finding.remediation}</p>
                  </div>
                ))
              ) : (
                <p className="rounded-3xl border border-dashed border-white/10 p-6 text-sm text-ink/60">
                  Findings will populate here once the worker persists them.
                </p>
              )}
            </div>
          </section>
        </div>
        <LiveLogPanel scanId={params.id} token={token} />
      </div>
    </AppShell>
  );
}

