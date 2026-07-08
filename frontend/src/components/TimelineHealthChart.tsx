import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import type { ProjectSummary, TimelineHealth } from "@/types";

interface TimelineHealthChartProps {
  projects: ProjectSummary[];
}

const HEALTH_COLORS: Record<TimelineHealth, string> = {
  on_track: "#16a34a",
  at_risk: "#d97706",
  delayed: "#dc2626",
};

const HEALTH_LABELS: Record<TimelineHealth, string> = {
  on_track: "On track",
  at_risk: "At risk",
  delayed: "Delayed",
};

/** Donut chart summarizing how many projects fall into each health bucket. */
export function TimelineHealthChart({ projects }: TimelineHealthChartProps) {
  const counts: Record<TimelineHealth, number> = { on_track: 0, at_risk: 0, delayed: 0 };
  for (const project of projects) {
    counts[project.timeline_health] += 1;
  }
  const data = (Object.keys(counts) as TimelineHealth[]).map((health) => ({
    name: HEALTH_LABELS[health],
    value: counts[health],
    health,
  }));

  return (
    <div className="rounded-lg bg-white p-4 shadow-sm">
      <h3 className="mb-3 text-sm font-semibold text-slate-700">Timeline health</h3>
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90} paddingAngle={2}>
            {data.map((entry) => (
              <Cell key={entry.health} fill={HEALTH_COLORS[entry.health]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
