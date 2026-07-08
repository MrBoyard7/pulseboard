import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/api/client";
import type { Blocker, PortfolioKpis, Project, ProjectFilters, ProjectSummary, Task } from "@/types";

export function useDashboardSummary(filters: ProjectFilters) {
  return useQuery({
    queryKey: ["dashboard-summary", filters],
    queryFn: async () => {
      const response = await apiClient.get<ProjectSummary[]>("/api/dashboard/summary", {
        params: filters,
      });
      return response.data;
    },
  });
}

export function usePortfolioKpis() {
  return useQuery({
    queryKey: ["dashboard-kpis"],
    queryFn: async () => {
      const response = await apiClient.get<PortfolioKpis>("/api/dashboard/kpis");
      return response.data;
    },
  });
}

export function useProject(projectId: number | null) {
  return useQuery({
    queryKey: ["project", projectId],
    queryFn: async () => {
      const response = await apiClient.get<Project>(`/api/projects/${projectId}`);
      return response.data;
    },
    enabled: projectId !== null,
  });
}

export function useProjectTasks(projectId: number | null) {
  return useQuery({
    queryKey: ["project-tasks", projectId],
    queryFn: async () => {
      const response = await apiClient.get<Task[]>("/api/tasks", { params: { project_id: projectId } });
      return response.data;
    },
    enabled: projectId !== null,
  });
}

export function useProjectBlockers(projectId: number | null) {
  return useQuery({
    queryKey: ["project-blockers", projectId],
    queryFn: async () => {
      const response = await apiClient.get<Blocker[]>("/api/blockers", {
        params: { project_id: projectId },
      });
      return response.data;
    },
    enabled: projectId !== null,
  });
}
