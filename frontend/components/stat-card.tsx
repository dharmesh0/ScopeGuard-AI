export function StatCard({
  label,
  value,
  tone = "default",
}: {
  label: string;
  value: number | string;
  tone?: "default" | "danger" | "accent";
}) {
  const toneClass =
    tone === "danger"
      ? "from-danger/15 to-danger/5 text-danger"
      : tone === "accent"
        ? "from-accent/20 to-accent/5 text-accent"
        : "from-mint/15 to-mint/5 text-mint";

  return (
    <div className={`rounded-3xl border border-white/10 bg-gradient-to-br ${toneClass} p-[1px]`}>
      <div className="glass rounded-[calc(1.5rem-1px)] p-5">
        <p className="text-xs uppercase tracking-[0.25em] text-ink/50">{label}</p>
        <p className="mt-3 text-4xl font-semibold text-ink">{value}</p>
      </div>
    </div>
  );
}

