import type { ReactNode } from "react";

import { useAuth } from "@/hooks/useAuth";
import { usePortfolioKpis } from "@/hooks/useProjects";

interface DashboardLayoutProps {
  children: ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const { user, logout } = useAuth();
  const { data: kpis } = usePortfolioKpis();

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <h1 className="text-xl font-bold text-brand-700">PulseBoard</h1>
          <div className="flex items-center gap-4 text-sm text-slate-600">
            <span>
              {user?.full_name} <span className="text-slate-400">({user?.role})</span>
            </span>
            <button
              type="button"
              onClick={logout}
              className="rounded-md border border-slate-300 px-3 py-1 hover:bg-slate-100"
            >
              Log out
            </button>
          </div>
        </div>
      </header>

      {kpis && (
        <div className="mx-auto grid max-w-7xl grid-cols-2 gap-4 px-6 pt-6 sm:grid-cols-3 lg:grid-cols-6">
          <KpiCard label="Total projects" value={kpis.total_projects} />
          <KpiCard label="Active" value={kpis.active_projects} />
          <KpiCard label="At risk" value={kpis.at_risk_projects} accent="text-status-atRisk" />
          <KpiCard label="Delayed" value={kpis.delayed_projects} accent="text-status-delayed" />
          <KpiCard label="Total budget" value={`$${kpis.total_budget.toLocaleString()}`} />
          <KpiCard label="Overall burn" value={`${kpis.overall_burn_pct.toFixed(1)}%`} />
        </div>
      )}

      <main className="mx-auto max-w-7xl space-y-6 px-6 py-6">{children}</main>
    </div>
  );
}

function KpiCard({ label, value, accent }: { label: string; value: string | number; accent?: string }) {
  return (
    <div className="rounded-lg bg-white p-4 shadow-sm">
      <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
      <p className={`mt-1 text-2xl font-semibold ${accent ?? "text-slate-900"}`}>{value}</p>
    </div>
  );
}
