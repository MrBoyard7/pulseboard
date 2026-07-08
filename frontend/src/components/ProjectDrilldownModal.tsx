import { useProject, useProjectBlockers, useProjectTasks } from "@/hooks/useProjects";

interface ProjectDrilldownModalProps {
  projectId: number;
  onClose: () => void;
}

export function ProjectDrilldownModal({ projectId, onClose }: ProjectDrilldownModalProps) {
  const { data: project, isLoading: projectLoading } = useProject(projectId);
  const { data: tasks } = useProjectTasks(projectId);
  const { data: blockers } = useProjectBlockers(projectId);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4">
      <div className="max-h-[85vh] w-full max-w-2xl overflow-y-auto rounded-xl bg-white p-6 shadow-xl">
        <div className="mb-4 flex items-start justify-between">
          <h2 className="text-lg font-semibold text-slate-900">
            {projectLoading ? "Loading…" : project?.name}
          </h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="rounded-full p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          >
            ✕
          </button>
        </div>

        {project && (
          <div className="space-y-6 text-sm text-slate-700">
            <p>{project.description}</p>

            <dl className="grid grid-cols-2 gap-3">
              <div>
                <dt className="text-xs uppercase text-slate-400">Stage</dt>
                <dd className="capitalize">{project.stage.replace("_", " ")}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase text-slate-400">Budget</dt>
                <dd>${project.budget_total.toLocaleString()}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase text-slate-400">Start date</dt>
                <dd>{project.start_date}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase text-slate-400">Target end date</dt>
                <dd>{project.target_end_date}</dd>
              </div>
            </dl>

            <section>
              <h3 className="mb-2 font-semibold text-slate-800">Tasks ({tasks?.length ?? 0})</h3>
              <ul className="divide-y divide-slate-100 rounded-md border border-slate-100">
                {tasks?.map((task) => (
                  <li key={task.id} className="flex items-center justify-between px-3 py-2">
                    <span>{task.title}</span>
                    <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs capitalize text-slate-600">
                      {task.status.replace("_", " ")}
                    </span>
                  </li>
                ))}
              </ul>
            </section>

            <section>
              <h3 className="mb-2 font-semibold text-slate-800">Blockers ({blockers?.length ?? 0})</h3>
              {blockers && blockers.length > 0 ? (
                <ul className="space-y-2">
                  {blockers.map((blocker) => (
                    <li key={blocker.id} className="rounded-md border border-slate-100 px-3 py-2">
                      <div className="flex items-center justify-between">
                        <span className="font-medium capitalize text-slate-800">{blocker.severity}</span>
                        <span className={blocker.resolved ? "text-status-onTrack" : "text-status-delayed"}>
                          {blocker.resolved ? "Resolved" : "Open"}
                        </span>
                      </div>
                      <p className="mt-1 text-slate-600">{blocker.description}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-slate-500">No blockers reported.</p>
              )}
            </section>
          </div>
        )}
      </div>
    </div>
  );
}
