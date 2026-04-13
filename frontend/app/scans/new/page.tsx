"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { AppShell } from "@/components/shell";
import { ScanForm } from "@/components/scan-form";
import { getToken } from "@/lib/auth";

export default function NewScanPage() {
  const router = useRouter();

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
    }
  }, [router]);

  return (
    <AppShell
      title="Create Assessment"
      subtitle="Define the engagement boundary, confirm authorization, and launch a guarded defensive assessment."
    >
      <ScanForm />
    </AppShell>
  );
}

