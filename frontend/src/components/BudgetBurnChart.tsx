import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { ProjectSummary } from "@/types";

interface BudgetBurnChartProps {
  projects: ProjectSummary[];
}

/** Shows the ten projects with the highest budget burn percentage. */
export function BudgetBurnChart({ projects }: BudgetBurnChartProps) {
  const data = [...projects]
    .sort((a, b) => b.budget_burn_pct - a.budget_burn_pct)
    .slice(0, 10)
    .map((project) => ({
      name: project.name.length > 18 ? `${project.name.slice(0, 18)}…` : project.name,
      burn: project.budget_burn_pct,
    }));

  return (
    <div className="rounded-lg bg-white p-4 shadow-sm">
      <h3 className="mb-3 text-sm font-semibold text-slate-700">Top budget burn</h3>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} layout="vertical" margin={{ left: 24 }}>
          <CartesianGrid strokeDasharray="3 3" horizontal={false} />
          <XAxis type="number" unit="%" domain={[0, "dataMax"]} />
          <YAxis type="category" dataKey="name" width={130} tick={{ fontSize: 12 }} />
          <Tooltip formatter={(value: number) => [`${value.toFixed(1)}%`, "Budget burn"]} />
          <Bar dataKey="burn" fill="#3b6ef6" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
