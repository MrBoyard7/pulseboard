import type { ProjectFilters, ProjectStage, TimelineHealth } from "@/types";

const STAGES: ProjectStage[] = ["kickoff", "planning", "in_progress", "on_hold", "review", "closed"];
const HEALTHS: TimelineHealth[] = ["on_track", "at_risk", "delayed"];

interface FilterBarProps {
  filters: ProjectFilters;
  onChange: (filters: ProjectFilters) => void;
}

const STAGE_LABELS: Record<ProjectStage, string> = {
  kickoff: "Kickoff",
  planning: "Planning",
  in_progress: "In progress",
  on_hold: "On hold",
  review: "Review",
  closed: "Closed",
};

const HEALTH_LABELS: Record<TimelineHealth, string> = {
  on_track: "On track",
  at_risk: "At risk",
  delayed: "Delayed",
};

export function FilterBar({ filters, onChange }: FilterBarProps) {
  return (
    <div className="flex flex-wrap items-center gap-3 rounded-lg bg-white p-4 shadow-sm">
      <label className="flex items-center gap-2 text-sm font-medium text-slate-600">
        Stage
        <select
          className="rounded-md border border-slate-300 px-2 py-1 text-sm"
          value={filters.stage ?? ""}
          onChange={(event) =>
            onChange({ ...filters, stage: (event.target.value || undefined) as ProjectStage | undefined })
          }
        >
          <option value="">All</option>
          {STAGES.map((stage) => (
            <option key={stage} value={stage}>
              {STAGE_LABELS[stage]}
            </option>
          ))}
        </select>
      </label>

      <label className="flex items-center gap-2 text-sm font-medium text-slate-600">
        Timeline health
        <select
          className="rounded-md border border-slate-300 px-2 py-1 text-sm"
          value={filters.health ?? ""}
          onChange={(event) =>
            onChange({
              ...filters,
              health: (event.target.value || undefined) as TimelineHealth | undefined,
            })
          }
        >
          <option value="">All</option>
          {HEALTHS.map((health) => (
            <option key={health} value={health}>
              {HEALTH_LABELS[health]}
            </option>
          ))}
        </select>
      </label>

      {(filters.stage || filters.health || filters.owner_id) && (
        <button
          type="button"
          onClick={() => onChange({})}
          className="ml-auto text-sm font-medium text-brand-600 hover:text-brand-700"
        >
          Clear filters
        </button>
      )}
    </div>
  );
}
