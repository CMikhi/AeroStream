import asyncio
from typing import Dict, Set, Any
from fastapi import WebSocket

__all__ = ['ConnectionManager', 'manager']

class ConnectionManager:
    def __init__(self):
        self.active_rooms: Dict[str, Set[WebSocket]] = {}
        self.lock = asyncio.Lock()

    async def connect(self, room_name: str, ws: WebSocket):
        async with self.lock:
            if room_name not in self.active_rooms:
                self.active_rooms[room_name] = set()
            self.active_rooms[room_name].add(ws)

    async def disconnect(self, room_name: str, ws: WebSocket):
        async with self.lock:
            if room_name in self.active_rooms:
                self.active_rooms[room_name].discard(ws)
                if not self.active_rooms[room_name]:
                    del self.active_rooms[room_name]

    async def broadcast(self, room_name: str, data: Any):
        """Send JSON-serializable data to all sockets in room (best-effort)."""
        # copy to avoid holding lock while awaiting sends
        async with self.lock:
            sockets = list(self.active_rooms.get(room_name, []))
        bad = []
        for s in sockets:
            try:
                await s.send_json(data)
            except Exception:
                bad.append(s)
        # cleanup bad sockets
        if bad:
            async with self.lock:
                for s in bad:
                    self.active_rooms.get(room_name, set()).discard(s)

# single instance to import
manager = ConnectionManager()
