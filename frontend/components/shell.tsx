"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ShieldCheck, LayoutDashboard, PlusSquare, LogOut } from "lucide-react";

import { clearSession } from "@/lib/auth";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/scans/new", label: "New Scan", icon: PlusSquare },
];

export function AppShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <div className="min-h-screen gridlines">
      <div className="mx-auto flex min-h-screen max-w-7xl gap-6 px-4 py-6 lg:px-8">
        <aside className="glass hidden w-72 shrink-0 rounded-3xl p-6 lg:block">
          <div className="mb-10 flex items-center gap-3">
            <div className="rounded-2xl bg-accent/15 p-3 text-accent">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div>
              <p className="text-lg font-semibold">ScopeGuard AI</p>
              <p className="text-sm text-ink/60">Authorized assessment cockpit</p>
            </div>
          </div>
          <nav className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 rounded-2xl px-4 py-3 transition ${
                    active ? "bg-white/10 text-accent" : "text-ink/70 hover:bg-white/5 hover:text-ink"
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
          <button
            type="button"
            onClick={() => {
              clearSession();
              router.push("/login");
            }}
            className="mt-10 flex w-full items-center justify-center gap-2 rounded-2xl border border-white/10 px-4 py-3 text-sm text-ink/80 transition hover:bg-white/5"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </aside>
        <main className="flex-1">
          <div className="glass mb-4 flex items-center justify-between rounded-3xl p-3 lg:hidden">
            <div className="flex gap-2 overflow-auto">
              {navItems.map((item) => {
                const Icon = item.icon;
                const active = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-2 rounded-2xl px-3 py-2 text-sm ${
                      active ? "bg-white/10 text-accent" : "text-ink/70"
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </div>
            <button
              type="button"
              onClick={() => {
                clearSession();
                router.push("/login");
              }}
              className="rounded-2xl border border-white/10 px-3 py-2 text-xs text-ink/80"
            >
              Sign out
            </button>
          </div>
          <div className="glass mb-6 rounded-3xl p-6">
            <p className="text-sm uppercase tracking-[0.3em] text-mint/80">Operational View</p>
            <h1 className="mt-3 text-4xl font-semibold">{title}</h1>
            <p className="mt-2 max-w-3xl text-sm text-ink/70">{subtitle}</p>
          </div>
          {children}
        </main>
      </div>
    </div>
  );
}
