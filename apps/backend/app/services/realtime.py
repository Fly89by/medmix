import json
from fastapi import WebSocket
from typing import Set

connected_clients: Set[WebSocket] = set()


async def connect(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)


def disconnect(websocket: WebSocket):
    connected_clients.discard(websocket)


async def broadcast(event: str, data: dict = None):
    message = json.dumps({"event": event, "data": data or {}}, ensure_ascii=False)
    stale = set()
    for client in connected_clients:
        try:
            await client.send_text(message)
        except Exception:
            stale.add(client)
    connected_clients.difference_update(stale)
