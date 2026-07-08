export type UserRole = "admin" | "member" | "executive";

export type ProjectStage =
  | "kickoff"
  | "planning"
  | "in_progress"
  | "on_hold"
  | "review"
  | "closed";

export type TaskStatus = "todo" | "in_progress" | "blocked" | "done";

export type BlockerSeverity = "low" | "medium" | "high" | "critical";

export type TimelineHealth = "on_track" | "at_risk" | "delayed";

export interface User {
  id: number;
  full_name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  team_id: number | null;
}

export interface Project {
  id: number;
  name: string;
  description: string | null;
  stage: ProjectStage;
  start_date: string;
  target_end_date: string;
  actual_end_date: string | null;
  budget_total: number;
  owner_id: number;
  team_id: number | null;
}

export interface ProjectSummary {
  id: number;
  name: string;
  stage: ProjectStage;
  owner_name: string;
  budget_total: number;
  budget_spent: number;
  budget_burn_pct: number;
  open_blockers: number;
  critical_blockers: number;
  timeline_health: TimelineHealth;
  target_end_date: string;
}

export interface Task {
  id: number;
  project_id: number;
  title: string;
  status: TaskStatus;
  due_date: string | null;
  assignee_id: number | null;
}

export interface Blocker {
  id: number;
  project_id: number;
  description: string;
  severity: BlockerSeverity;
  resolved: boolean;
  reported_by_id: number;
  created_at: string;
  resolved_at: string | null;
}

export interface PortfolioKpis {
  total_projects: number;
  active_projects: number;
  delayed_projects: number;
  at_risk_projects: number;
  total_budget: number;
  total_spent: number;
  overall_burn_pct: number;
}

export interface ProjectFilters {
  stage?: ProjectStage;
  owner_id?: number;
  health?: TimelineHealth;
}
