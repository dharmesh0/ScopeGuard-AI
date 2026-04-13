"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AlertTriangle, ArrowRight, Shield } from "lucide-react";

import { AppShell } from "@/components/shell";
import { StatCard } from "@/components/stat-card";
import { api } from "@/lib/api";
import { getToken } from "@/lib/auth";
import type { DashboardStats, Plugin, Scan } from "@/lib/types";

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [scans, setScans] = useState<Scan[]>([]);
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [cves, setCves] = useState<{ id: string; description: string }[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push("/login");
      return;
    }

    Promise.all([api.dashboard(token), api.scans(token), api.plugins(token), api.latestCves(token)])
      .then(([dashboard, scanItems, pluginItems, latestCves]) => {
        setStats(dashboard);
        setScans(scanItems);
        setPlugins(pluginItems);
        setCves(latestCves);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Failed to load dashboard.");
      });
  }, [router]);

  return (
    <AppShell
      title="Mission Control"
      subtitle="Track approved engagements, launch guarded assessments, and keep the operator loop visible from request to report."
    >
      {error ? (
        <div className="mb-6 rounded-3xl border border-danger/30 bg-danger/10 p-4 text-sm text-danger">
          {error}
        </div>
      ) : null}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total scans" value={stats?.scans_total ?? "…"} />
        <StatCard label="Active scans" value={stats?.active_scans ?? "…"} tone="accent" />
        <StatCard label="Total findings" value={stats?.findings_total ?? "…"} />
        <StatCard label="Critical findings" value={stats?.critical_findings ?? "…"} tone="danger" />
      </div>
      <div className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <section className="glass rounded-3xl p-6">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-semibold">Recent assessments</h2>
              <p className="text-sm text-ink/60">Only approved, scope-bound runs appear here.</p>
            </div>
            <Link
              href="/scans/new"
              className="rounded-2xl bg-accent px-4 py-2 text-sm font-medium text-canvas"
            >
              New scan
            </Link>
          </div>
          <div className="space-y-4">
            {scans.length === 0 ? (
              <div className="rounded-3xl border border-dashed border-white/10 p-6 text-sm text-ink/60">
                No scans yet. Create an engagement and request your first authorized assessment.
              </div>
            ) : (
              scans.map((scan) => (
                <Link
                  key={scan.id}
                  href={`/scans/${scan.id}`}
                  className="block rounded-3xl border border-white/10 bg-white/5 p-5 transition hover:bg-white/10"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-[var(--font-mono)] text-sm text-mint">{scan.target}</p>
                      <h3 className="mt-2 text-xl font-medium">{scan.status.replaceAll("_", " ")}</h3>
                      <p className="mt-2 text-sm text-ink/65">{scan.summary || "Awaiting analysis summary."}</p>
                    </div>
                    <ArrowRight className="h-5 w-5 shrink-0 text-ink/50" />
                  </div>
                </Link>
              ))
            )}
          </div>
        </section>
        <div className="space-y-6">
          <section className="glass rounded-3xl p-6">
            <div className="mb-4 flex items-center gap-3">
              <Shield className="h-5 w-5 text-accent" />
              <h2 className="text-xl font-semibold">Built-in plugins</h2>
            </div>
            <div className="space-y-3">
              {plugins.map((plugin) => (
                <div key={plugin.name} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="font-medium">{plugin.name}</p>
                  <p className="mt-1 text-sm text-ink/65">{plugin.description}</p>
                </div>
              ))}
            </div>
          </section>
          <section className="glass rounded-3xl p-6">
            <div className="mb-4 flex items-center gap-3">
              <AlertTriangle className="h-5 w-5 text-danger" />
              <h2 className="text-xl font-semibold">Latest CVE context</h2>
            </div>
            <div className="space-y-3">
              {cves.slice(0, 4).map((cve) => (
                <div key={cve.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="font-[var(--font-mono)] text-sm text-accent">{cve.id}</p>
                  <p className="mt-2 text-sm text-ink/70">{cve.description.slice(0, 180)}...</p>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </AppShell>
  );
}

