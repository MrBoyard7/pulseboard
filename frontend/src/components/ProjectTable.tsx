import type { ProjectSummary, TimelineHealth } from "@/types";

interface ProjectTableProps {
  projects: ProjectSummary[];
  onSelect: (projectId: number) => void;
}

const HEALTH_STYLES: Record<TimelineHealth, string> = {
  on_track: "bg-status-onTrack/10 text-status-onTrack",
  at_risk: "bg-status-atRisk/10 text-status-atRisk",
  delayed: "bg-status-delayed/10 text-status-delayed",
};

const HEALTH_LABELS: Record<TimelineHealth, string> = {
  on_track: "On track",
  at_risk: "At risk",
  delayed: "Delayed",
};

export function ProjectTable({ projects, onSelect }: ProjectTableProps) {
  if (projects.length === 0) {
    return (
      <div className="rounded-lg bg-white p-8 text-center text-sm text-slate-500 shadow-sm">
        No projects match the current filters.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg bg-white shadow-sm">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-4 py-3">Project</th>
            <th className="px-4 py-3">Owner</th>
            <th className="px-4 py-3">Stage</th>
            <th className="px-4 py-3">Budget burn</th>
            <th className="px-4 py-3">Blockers</th>
            <th className="px-4 py-3">Timeline</th>
            <th className="px-4 py-3">Target end date</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {projects.map((project) => (
            <tr
              key={project.id}
              onClick={() => onSelect(project.id)}
              className="cursor-pointer hover:bg-brand-50"
            >
              <td className="px-4 py-3 font-medium text-slate-900">{project.name}</td>
              <td className="px-4 py-3 text-slate-600">{project.owner_name}</td>
              <td className="px-4 py-3 capitalize text-slate-600">{project.stage.replace("_", " ")}</td>
              <td className="px-4 py-3 text-slate-600">
                {project.budget_burn_pct.toFixed(1)}%{" "}
                <span className="text-xs text-slate-400">
                  (${project.budget_spent.toLocaleString()} / ${project.budget_total.toLocaleString()})
                </span>
              </td>
              <td className="px-4 py-3 text-slate-600">
                {project.open_blockers}
                {project.critical_blockers > 0 && (
                  <span className="ml-1 text-xs font-semibold text-status-delayed">
                    ({project.critical_blockers} critical)
                  </span>
                )}
              </td>
              <td className="px-4 py-3">
                <span
                  className={`rounded-full px-2 py-1 text-xs font-semibold ${HEALTH_STYLES[project.timeline_health]}`}
                >
                  {HEALTH_LABELS[project.timeline_health]}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-600">{project.target_end_date}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
