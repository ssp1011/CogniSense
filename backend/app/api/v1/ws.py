"""
CogniSense — WebSocket Streaming Endpoint.

WS /ws/load — Real-time cognitive load streaming
"""

import logging
import asyncio
import json
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.scoring_service import ScoringService

logger = logging.getLogger(__name__)
router = APIRouter()

# Singleton scoring service
_scoring_service = ScoringService()
_scoring_service.load_model()


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket client connected (%d total)", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info("WebSocket client disconnected (%d remaining)", len(self.active_connections))

    async def broadcast(self, message: dict):
        """Send a message to all connected clients."""
        disconnected = []
        for ws in self.active_connections:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.active_connections.remove(ws)


manager = ConnectionManager()


@router.websocket("/load")
async def websocket_load_stream(websocket: WebSocket):
    """
    Stream real-time cognitive load predictions via WebSocket.

    Sends JSON messages every ~1 second with:
    {
        "load_level": "low|medium|high",
        "confidence": 0.85,
        "modality_scores": {"visual": 0.3, "behavioral": 0.4, "audio": 0.3},
        "probabilities": {"low": 0.1, "medium": 0.05, "high": 0.85},
        "timestamp": "2026-02-11T12:00:00"
    }

    Clients can send JSON commands:
    {"action": "pause"}  — Pause streaming
    {"action": "resume"} — Resume streaming
    {"action": "ping"}   — Health check (responds with pong)
    """
    await manager.connect(websocket)
    streaming = True

    try:
        while True:
            # Check for client messages (non-blocking)
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(), timeout=0.1
                )
                try:
                    cmd = json.loads(data)
                    action = cmd.get("action", "")
                    if action == "pause":
                        streaming = False
                        await websocket.send_json({"status": "paused"})
                    elif action == "resume":
                        streaming = True
                        await websocket.send_json({"status": "streaming"})
                    elif action == "ping":
                        await websocket.send_json({"status": "pong"})
                except json.JSONDecodeError:
                    pass
            except asyncio.TimeoutError:
                pass

            # Send prediction if streaming
            if streaming:
                features = {}  # In production: from fusion engine
                result = _scoring_service.predict(features)
                result["timestamp"] = datetime.utcnow().isoformat()
                await websocket.send_json(result)

            await asyncio.sleep(1.0)  # 1 Hz update rate

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket error: %s", e)
        manager.disconnect(websocket)
