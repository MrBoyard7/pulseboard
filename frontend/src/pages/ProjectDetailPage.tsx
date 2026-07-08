import { useNavigate, useParams } from "react-router-dom";

import { DashboardLayout } from "@/components/DashboardLayout";
import { useProject, useProjectBlockers, useProjectTasks } from "@/hooks/useProjects";

export function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const projectId = id ? Number(id) : null;
  const navigate = useNavigate();

  const { data: project, isLoading } = useProject(projectId);
  const { data: tasks } = useProjectTasks(projectId);
  const { data: blockers } = useProjectBlockers(projectId);

  return (
    <DashboardLayout>
      <button
        type="button"
        onClick={() => navigate("/")}
        className="text-sm font-medium text-brand-600 hover:text-brand-700"
      >
        ← Back to dashboard
      </button>

      {isLoading && <p className="text-sm text-slate-500">Loading…</p>}

      {project && (
        <div className="rounded-lg bg-white p-6 shadow-sm">
          <h1 className="text-xl font-bold text-slate-900">{project.name}</h1>
          <p className="mt-2 text-sm text-slate-600">{project.description}</p>

          <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <Stat label="Stage" value={project.stage.replace("_", " ")} />
            <Stat label="Budget" value={`$${project.budget_total.toLocaleString()}`} />
            <Stat label="Start" value={project.start_date} />
            <Stat label="Target end" value={project.target_end_date} />
          </div>

          <h2 className="mt-8 mb-2 text-sm font-semibold text-slate-800">Tasks</h2>
          <ul className="divide-y divide-slate-100 rounded-md border border-slate-100">
            {tasks?.map((task) => (
              <li key={task.id} className="flex items-center justify-between px-3 py-2 text-sm">
                <span>{task.title}</span>
                <span className="text-xs capitalize text-slate-500">{task.status.replace("_", " ")}</span>
              </li>
            ))}
          </ul>

          <h2 className="mt-8 mb-2 text-sm font-semibold text-slate-800">Blockers</h2>
          <ul className="space-y-2">
            {blockers?.map((blocker) => (
              <li key={blocker.id} className="rounded-md border border-slate-100 px-3 py-2 text-sm">
                <span className="font-medium capitalize">{blocker.severity}</span> — {blocker.description}
              </li>
            ))}
          </ul>
        </div>
      )}
    </DashboardLayout>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs uppercase text-slate-400">{label}</p>
      <p className="capitalize text-slate-800">{value}</p>
    </div>
  );
}
