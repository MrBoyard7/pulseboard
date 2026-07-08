"""WebSocket endpoint that pushes live update events to the dashboard.

The token is passed as a query parameter (`?token=...`) because browser
WebSocket clients cannot set an Authorization header on the handshake
request.
"""
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import SessionLocal
from app.models.user import User
from app.services.realtime import manager

router = APIRouter(tags=["realtime"])


@router.websocket("/ws/dashboard")
async def dashboard_updates(websocket: WebSocket, token: str = Query(...)) -> None:
    """Authenticate the socket, then relay broadcast events until disconnect."""
    payload = decode_access_token(token)
    if payload is None:
        await websocket.close(code=4401)
        return

    db: Session = SessionLocal()
    try:
        user = db.get(User, int(payload["sub"]))
        if user is None or not user.is_active:
            await websocket.close(code=4401)
            return
    finally:
        db.close()

    await manager.connect(websocket)
    try:
        while True:
            # The client does not need to send anything; we simply keep the
            # connection open and wait for a disconnect to clean it up.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
