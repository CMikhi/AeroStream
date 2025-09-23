import asyncio
from typing import Dict, Set, Any
from fastapi import WebSocket

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

    async def broadcast(self, room_name: str, data: Any, exclude_socket: WebSocket = None):
        """Send JSON-serializable data to all sockets in room (best-effort)."""
        print(f"Broadcasting to room '{room_name}': {data}")
        if exclude_socket:
            print(f"Excluding sender socket from broadcast")
        
        # copy to avoid holding lock while awaiting sends
        async with self.lock:
            sockets = list(self.active_rooms.get(room_name, []))
        
        # Filter out the excluded socket if provided
        if exclude_socket:
            sockets = [s for s in sockets if s != exclude_socket]
            
        print(f"Found {len(sockets)} sockets in room (after exclusions)")
        
        bad = []
        for i, s in enumerate(sockets):
            try:
                print(f"Sending to socket {i+1}")
                await s.send_json(data)
                print(f"Successfully sent to socket {i+1}")
            except Exception as e:
                print(f"Failed to send to socket {i+1}: {e}")
                bad.append(s)
        
        # cleanup bad sockets
        if bad:
            print(f"Cleaning up {len(bad)} bad sockets")
            async with self.lock:
                for s in bad:
                    self.active_rooms.get(room_name, set()).discard(s)

# single instance to import
manager = ConnectionManager()
