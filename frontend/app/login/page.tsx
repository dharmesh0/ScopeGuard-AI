import { ShieldCheck } from "lucide-react";

import { LoginForm } from "@/components/login-form";

export default function LoginPage() {
  return (
    <main className="grid min-h-screen place-items-center px-4 py-10">
      <div className="grid w-full max-w-6xl gap-8 lg:grid-cols-[1.15fr_0.85fr]">
        <section className="glass rounded-[2rem] p-10">
          <div className="inline-flex rounded-3xl bg-accent/15 p-4 text-accent">
            <ShieldCheck className="h-10 w-10" />
          </div>
          <p className="mt-8 text-sm uppercase tracking-[0.3em] text-mint/80">Authorized Use Only</p>
          <h1 className="mt-4 max-w-2xl text-5xl font-semibold leading-tight">
            AI-assisted security assessments with explicit scope controls.
          </h1>
          <p className="mt-6 max-w-2xl text-lg text-ink/70">
            ScopeGuard AI is built for legal, authorized testing only. Every engagement carries
            scope boundaries, operator attestation, and optional human approval before execution.
          </p>
          <div className="mt-10 grid gap-4 sm:grid-cols-3">
            {[
              "Docker-sandboxed runners",
              "Memory + graph-backed analysis",
              "Markdown and PDF reporting",
            ].map((item) => (
              <div key={item} className="rounded-3xl border border-white/10 bg-white/5 p-4 text-sm text-ink/75">
                {item}
              </div>
            ))}
          </div>
        </section>
        <div className="flex items-center justify-center">
          <LoginForm />
        </div>
      </div>
    </main>
  );
}

