import "@testing-library/jest-dom/vitest";

class ResizeObserverPolyfill {
  observe() {}
  unobserve() {}
  disconnect() {}
}

globalThis.ResizeObserver = ResizeObserverPolyfill as unknown as typeof ResizeObserver;