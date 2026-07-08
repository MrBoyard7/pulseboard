import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { FilterBar } from "@/components/FilterBar";

describe("FilterBar", () => {
  it("calls onChange with the selected stage", () => {
    const onChange = vi.fn();
    render(<FilterBar filters={{}} onChange={onChange} />);

    fireEvent.change(screen.getByLabelText(/stage/i), { target: { value: "in_progress" } });

    expect(onChange).toHaveBeenCalledWith({ stage: "in_progress" });
  });

  it("shows a clear-filters button only when a filter is active", () => {
    const { rerender } = render(<FilterBar filters={{}} onChange={vi.fn()} />);
    expect(screen.queryByText(/clear filters/i)).not.toBeInTheDocument();

    rerender(<FilterBar filters={{ stage: "planning" }} onChange={vi.fn()} />);
    expect(screen.getByText(/clear filters/i)).toBeInTheDocument();
  });

  it("resets all filters when clear is clicked", () => {
    const onChange = vi.fn();
    render(<FilterBar filters={{ stage: "planning", health: "at_risk" }} onChange={onChange} />);

    fireEvent.click(screen.getByText(/clear filters/i));

    expect(onChange).toHaveBeenCalledWith({});
  });
});
