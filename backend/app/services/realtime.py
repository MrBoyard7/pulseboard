"""In-memory WebSocket connection manager.

Broadcasts a lightweight event (e.g. `{"type": "project.updated"}`) to
every connected dashboard client whenever a write endpoint mutates
data. The frontend reacts by re-fetching the affected query, which is
what keeps the dashboard "live" without the user manually refreshing.

For a multi-instance production deployment, replace the in-process
`ConnectionManager` with a Redis pub/sub backend (see docs/ARCHITECTURE.md)
so events broadcast across all API replicas, not just the one that
handled the write.
"""

import json
from dataclasses import dataclass, field

from fastapi import WebSocket


@dataclass
class ConnectionManager:
    """Tracks active WebSocket clients and fans out JSON events to them."""

    active_connections: list[WebSocket] = field(default_factory=list)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, event_type: str, payload: dict | None = None) -> None:
        """Send an event to every connected client, dropping dead sockets."""
        message = json.dumps({"type": event_type, "payload": payload or {}})
        stale: list[WebSocket] = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:  # noqa: BLE001 - a dead socket should not break the loop
                stale.append(connection)
        for connection in stale:
            self.disconnect(connection)


manager = ConnectionManager()
