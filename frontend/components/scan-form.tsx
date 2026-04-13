"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { api } from "@/lib/api";
import { getToken } from "@/lib/auth";
import type { Engagement } from "@/lib/types";

export function ScanForm() {
  const router = useRouter();
  const [engagements, setEngagements] = useState<Engagement[]>([]);
  const [engagementId, setEngagementId] = useState("");
  const [engagementName, setEngagementName] = useState("Quarterly Web Estate Review");
  const [engagementDescription, setEngagementDescription] = useState(
    "Operator-approved assessment for public web properties only."
  );
  const [scope, setScope] = useState("example.com, *.example.com");
  const [target, setTarget] = useState("https://example.com");
  const [attestation, setAttestation] = useState(
    "I confirm that this target is in scope, approved by the asset owner, and authorized for defensive assessment."
  );
  const [humanInLoop, setHumanInLoop] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = getToken();
    api.engagements(token)
      .then(setEngagements)
      .catch(() => setEngagements([]));
  }, []);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    const token = getToken();
    setError("");
    try {
      let resolvedEngagementId = engagementId;
      if (!resolvedEngagementId) {
        const engagement = await api.createEngagement(
          {
            name: engagementName,
            description: engagementDescription,
            scope: scope.split(",").map((item) => item.trim()).filter(Boolean),
            approval_mode: true,
          },
          token
        );
        resolvedEngagementId = engagement.id;
      }

      const scan = await api.createScan(
        {
          engagement_id: resolvedEngagementId,
          target,
          human_in_the_loop: humanInLoop,
          attestation,
        },
        token
      );
      router.push(`/scans/${scan.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Scan creation failed.");
    }
  };

  return (
    <form onSubmit={submit} className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
      <section className="glass rounded-3xl p-6">
        <h2 className="text-2xl font-semibold">Engagement & Scope</h2>
        <p className="mt-2 text-sm text-ink/65">
          Reuse an approved engagement or create a fresh one with explicit scope boundaries.
        </p>
        <label className="mt-6 block text-sm text-ink/70">
          Existing engagement
          <select
            value={engagementId}
            onChange={(event) => setEngagementId(event.target.value)}
            className="mt-2 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3"
          >
            <option value="">Create a new engagement</option>
            {engagements.map((engagement) => (
              <option key={engagement.id} value={engagement.id}>
                {engagement.name}
              </option>
            ))}
          </select>
        </label>
        {!engagementId ? (
          <>
            <label className="mt-4 block text-sm text-ink/70">
              Engagement name
              <input
                className="mt-2 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3"
                value={engagementName}
                onChange={(event) => setEngagementName(event.target.value)}
              />
            </label>
            <label className="mt-4 block text-sm text-ink/70">
              Description
              <textarea
                className="mt-2 min-h-28 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3"
                value={engagementDescription}
                onChange={(event) => setEngagementDescription(event.target.value)}
              />
            </label>
            <label className="mt-4 block text-sm text-ink/70">
              Approved scope
              <textarea
                className="mt-2 min-h-28 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 font-[var(--font-mono)] text-sm"
                value={scope}
                onChange={(event) => setScope(event.target.value)}
              />
            </label>
          </>
        ) : null}
      </section>
      <section className="glass rounded-3xl p-6">
        <h2 className="text-2xl font-semibold">Scan Request</h2>
        <label className="mt-6 block text-sm text-ink/70">
          Target URL or host
          <input
            className="mt-2 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 font-[var(--font-mono)]"
            value={target}
            onChange={(event) => setTarget(event.target.value)}
          />
        </label>
        <label className="mt-4 block text-sm text-ink/70">
          Authorization attestation
          <textarea
            className="mt-2 min-h-40 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3"
            value={attestation}
            onChange={(event) => setAttestation(event.target.value)}
          />
        </label>
        <label className="mt-4 flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-4">
          <input
            type="checkbox"
            checked={humanInLoop}
            onChange={(event) => setHumanInLoop(event.target.checked)}
          />
          <span className="text-sm text-ink/80">Require human-in-the-loop confirmation path</span>
        </label>
        {error ? <p className="mt-4 text-sm text-danger">{error}</p> : null}
        <button
          type="submit"
          className="mt-6 w-full rounded-2xl bg-accent px-4 py-3 font-medium text-canvas transition hover:brightness-110"
        >
          Create assessment
        </button>
      </section>
    </form>
  );
}
