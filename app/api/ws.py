from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
import json
from typing import Set

router = APIRouter(tags=["websocket"])

# Active WebSocket connections per match
active_connections: dict[str, Set[WebSocket]] = {}


@router.websocket("/ws/matches/{match_id}")
async def websocket_endpoint(websocket: WebSocket, match_id: str):
    """
    WebSocket endpoint for realtime match score + probability updates.

    Connection Flow:
    1. Client connects to /ws/matches/{match_id}
    2. Server sends score updates on each material event (wicket/over)
    3. Win probability recomputed and pushed on same channel
    4. Connection maintained until match completes or client disconnects

    Message Format (from server):
    {
        "type": "score_update" | "probability_update" | "match_complete",
        "match_id": "match_123",
        "data": {
            "team_a_score": 45,
            "team_b_score": 30,
            "overs": "5.2",
            "team_a_win_prob": 0.58,
            "team_b_win_prob": 0.42,
            "confidence": "high",
            "last_wicket": "Player Name",
            "timestamp": "2026-06-24T16:30:00Z"
        }
    }
    """
    await websocket.accept()

    if match_id not in active_connections:
        active_connections[match_id] = set()

    active_connections[match_id].add(websocket)

    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "match_id": match_id,
            "message": "Connected to match feed",
            "timestamp": "2026-06-24T16:30:00Z"
        })

        while True:
            # Receive client messages (e.g., ping, subscription preferences)
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": "2026-06-24T16:30:00Z"
                })

    except WebSocketDisconnect:
        active_connections[match_id].discard(websocket)
        if not active_connections[match_id]:
            del active_connections[match_id]
    except Exception as e:
        await websocket.close(code=status.WS_1011_SERVER_ERROR)
        active_connections[match_id].discard(websocket)


async def broadcast_match_update(match_id: str, update_data: dict):
    """Broadcast match update to all connected clients."""
    if match_id in active_connections:
        disconnected = set()
        for websocket in active_connections[match_id]:
            try:
                await websocket.send_json(update_data)
            except Exception:
                disconnected.add(websocket)

        # Clean up disconnected clients
        for ws in disconnected:
            active_connections[match_id].discard(ws)
