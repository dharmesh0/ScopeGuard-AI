export type User = {
  user_id: string;
  email: string;
  role: "admin" | "user";
  access_token: string;
};

export type DashboardStats = {
  scans_total: number;
  active_scans: number;
  findings_total: number;
  critical_findings: number;
};

export type Plugin = {
  name: string;
  description: string;
  source: string;
};

export type Engagement = {
  id: string;
  name: string;
  description: string;
  scope: string[];
  approval_mode: boolean;
  created_at: string;
};

export type ScanLog = {
  id: number;
  level: string;
  message: string;
  created_at: string;
};

export type Finding = {
  id: string;
  plugin: string;
  title: string;
  description: string;
  severity: "info" | "low" | "medium" | "high" | "critical";
  evidence: Record<string, unknown>;
  remediation: string;
  references: string[];
  created_at: string;
};

export type Scan = {
  id: string;
  engagement_id: string;
  requested_by: string;
  target: string;
  human_in_the_loop: boolean;
  approval_status: string;
  status: string;
  policy_snapshot: Record<string, unknown>;
  summary: string;
  severity_counts: Record<string, number>;
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
  findings: Finding[];
  logs: ScanLog[];
};

export type Report = {
  id: string;
  scan_id: string;
  markdown_path: string;
  pdf_path: string;
  checksum: string;
  created_at: string;
};

