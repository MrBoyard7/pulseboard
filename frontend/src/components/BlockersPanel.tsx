import type { ProjectSummary } from "@/types";

interface BlockersPanelProps {
  projects: ProjectSummary[];
}

/** Surfaces the projects with the most severe open blockers at a glance. */
export function BlockersPanel({ projects }: BlockersPanelProps) {
  const blocked = projects
    .filter((project) => project.open_blockers > 0)
    .sort((a, b) => b.critical_blockers - a.critical_blockers || b.open_blockers - a.open_blockers)
    .slice(0, 8);

  return (
    <div className="rounded-lg bg-white p-4 shadow-sm">
      <h3 className="mb-3 text-sm font-semibold text-slate-700">Projects with open blockers</h3>
      {blocked.length === 0 ? (
        <p className="text-sm text-slate-500">No open blockers across the portfolio. 🎉</p>
      ) : (
        <ul className="space-y-2">
          {blocked.map((project) => (
            <li key={project.id} className="flex items-center justify-between text-sm">
              <span className="text-slate-700">{project.name}</span>
              <span className="flex items-center gap-2">
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
                  {project.open_blockers} open
                </span>
                {project.critical_blockers > 0 && (
                  <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700">
                    {project.critical_blockers} critical
                  </span>
                )}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
