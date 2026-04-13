"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { AppShell } from "@/components/shell";
import { ReportViewer } from "@/components/report-viewer";
import { API_BASE_URL } from "@/lib/config";
import { api } from "@/lib/api";
import { getToken } from "@/lib/auth";

export default function ReportPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [markdown, setMarkdown] = useState("");
  const [error, setError] = useState("");
  const token = getToken();

  useEffect(() => {
    if (!token) {
      router.push("/login");
      return;
    }
    api.reportMarkdown(params.id, token)
      .then(setMarkdown)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load report."));
  }, [params.id, router, token]);

  return (
    <AppShell
      title="Assessment Report"
      subtitle="Share a durable summary with engineering and security teams using Markdown or PDF artifacts generated from the same findings set."
    >
      <div className="mb-6 flex items-center justify-between gap-4">
        <div className="text-sm text-ink/65">
          {error || "Markdown and PDF artifacts are generated from the completed scan state."}
        </div>
        <Link
          href={`${API_BASE_URL}/api/v1/reports/scan/${params.id}/pdf?token=${encodeURIComponent(token)}`}
          className="rounded-2xl bg-accent px-4 py-3 text-sm font-medium text-canvas"
          target="_blank"
        >
          Download PDF
        </Link>
      </div>
      {markdown ? (
        <ReportViewer markdown={markdown} />
      ) : (
        <div className="glass rounded-3xl p-6 text-sm text-ink/60">Report content is not ready yet.</div>
      )}
    </AppShell>
  );
}
