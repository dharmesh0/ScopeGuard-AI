"use client";

import ReactMarkdown from "react-markdown";

export function ReportViewer({ markdown }: { markdown: string }) {
  return (
    <div className="glass rounded-3xl p-6">
      <div className="prose prose-invert max-w-none prose-headings:text-ink prose-p:text-ink/80 prose-strong:text-accent prose-li:text-ink/80">
        <ReactMarkdown>{markdown}</ReactMarkdown>
      </div>
    </div>
  );
}

