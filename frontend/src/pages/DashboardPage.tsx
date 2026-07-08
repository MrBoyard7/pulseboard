import { useState } from "react";

import { BlockersPanel } from "@/components/BlockersPanel";
import { BudgetBurnChart } from "@/components/BudgetBurnChart";
import { DashboardLayout } from "@/components/DashboardLayout";
import { FilterBar } from "@/components/FilterBar";
import { ProjectDrilldownModal } from "@/components/ProjectDrilldownModal";
import { ProjectTable } from "@/components/ProjectTable";
import { TimelineHealthChart } from "@/components/TimelineHealthChart";
import { useRealtimeDashboard } from "@/hooks/useRealtime";
import { useDashboardSummary } from "@/hooks/useProjects";
import type { ProjectFilters } from "@/types";

export function DashboardPage() {
  const [filters, setFilters] = useState<ProjectFilters>({});
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);

  useRealtimeDashboard();
  const { data: projects, isLoading, isError } = useDashboardSummary(filters);

  return (
    <DashboardLayout>
      <FilterBar filters={filters} onChange={setFilters} />

      {isLoading && <p className="text-sm text-slate-500">Loading portfolio…</p>}
      {isError && (
        <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
          Could not load the portfolio. Please check your connection and try again.
        </p>
      )}

      {projects && (
        <>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <BudgetBurnChart projects={projects} />
            <TimelineHealthChart projects={projects} />
          </div>

          <BlockersPanel projects={projects} />

          <ProjectTable projects={projects} onSelect={setSelectedProjectId} />
        </>
      )}

      {selectedProjectId !== null && (
        <ProjectDrilldownModal projectId={selectedProjectId} onClose={() => setSelectedProjectId(null)} />
      )}
    </DashboardLayout>
  );
}
