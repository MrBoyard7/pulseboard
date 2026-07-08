import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";

import { API_BASE_URL, getStoredToken } from "@/api/client";

/**
 * Opens a WebSocket connection to the dashboard event stream and
 * invalidates the relevant React Query caches whenever the backend
 * broadcasts a change. This is what satisfies the "no manual refresh"
 * acceptance criterion: any write from any user (or the seed script)
 * is reflected within a second across every connected browser tab.
 *
 * Reconnects automatically with a short backoff if the connection drops.
 */
export function useRealtimeDashboard(): void {
  const queryClient = useQueryClient();
  const reconnectTimer = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    let socket: WebSocket | null = null;
    let cancelled = false;

    const connect = () => {
      const token = getStoredToken();
      if (!token || cancelled) return;

      const wsUrl = `${API_BASE_URL.replace(/^http/, "ws")}/ws/dashboard?token=${token}`;
      socket = new WebSocket(wsUrl);

      socket.onmessage = () => {
        // Any event type invalidates dashboard-scoped queries; the
        // payload is small enough that a targeted diff isn't worth
        // the added complexity for a portfolio of a few hundred rows.
        queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
        queryClient.invalidateQueries({ queryKey: ["dashboard-kpis"] });
        queryClient.invalidateQueries({ queryKey: ["project"] });
      };

      socket.onclose = () => {
        if (!cancelled) {
          reconnectTimer.current = setTimeout(connect, 3000);
        }
      };
    };

    connect();

    return () => {
      cancelled = true;
      socket?.close();
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };
  }, [queryClient]);
}
