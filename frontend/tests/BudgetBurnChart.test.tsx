import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { BudgetBurnChart } from "@/components/BudgetBurnChart";
import type { ProjectSummary } from "@/types";

function makeProject(overrides: Partial<ProjectSummary>): ProjectSummary {
  return {
    id: 1,
    name: "Sample Project",
    stage: "in_progress",
    owner_name: "Ada Admin",
    budget_total: 100000,
    budget_spent: 25000,
    budget_burn_pct: 25,
    open_blockers: 0,
    critical_blockers: 0,
    timeline_health: "on_track",
    target_end_date: "2026-12-01",
    ...overrides,
  };
}

describe("BudgetBurnChart", () => {
  it("renders the widget title", () => {
    render(<BudgetBurnChart projects={[makeProject({})]} />);
    expect(screen.getByText(/top budget burn/i)).toBeInTheDocument();
  });

  it("does not crash when given an empty project list", () => {
    render(<BudgetBurnChart projects={[]} />);
    expect(screen.getByText(/top budget burn/i)).toBeInTheDocument();
  });

  it("handles more than ten projects without error", () => {
    const projects = Array.from({ length: 15 }, (_, index) =>
      makeProject({ id: index, name: `Project ${index}`, budget_burn_pct: index * 5 }),
    );
    render(<BudgetBurnChart projects={projects} />);
    expect(screen.getByText(/top budget burn/i)).toBeInTheDocument();
  });
});
