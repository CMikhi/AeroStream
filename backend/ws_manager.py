import asyncio
from typing import Dict, Set, Any, Optional
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Track rooms and their websocket connections
        self.active_rooms: Dict[str, Set[WebSocket]] = {}
        # Track user connections to prevent duplicates
        # Format: {room_name: {username: websocket}}
        self.user_connections: Dict[str, Dict[str, WebSocket]] = {}
        # Track websocket to user mapping for cleanup
        # Format: {websocket: (room_name, username)}
        self.socket_to_user: Dict[WebSocket, tuple[str, str]] = {}
        self.lock = asyncio.Lock()

    async def connect(self, room_name: str, user: dict, ws: WebSocket):
        username = user["username"]
        
        async with self.lock:
            # Initialize room structures if they don't exist
            if room_name not in self.active_rooms:
                self.active_rooms[room_name] = set()
            if room_name not in self.user_connections:
                self.user_connections[room_name] = {}
            
            # Check if user already has a connection in this room
            if username in self.user_connections[room_name]:
                old_ws = self.user_connections[room_name][username]
                print(f"User {username} already connected to room {room_name}. Rejecting new connection.")
                
                # Check if old connection is still alive
                try:
                    # Try to send a ping to see if the old connection is still active
                    await old_ws.send_json({"type": "ping"})
                    # If we get here, old connection is still active, reject new one
                    raise ConnectionRefusedError(f"User {username} is already connected to room {room_name}")
                except Exception as e:
                    # Old connection is dead, clean it up and allow new connection
                    print(f"Old connection for {username} appears dead ({e}), cleaning up and allowing new connection")
                    self.active_rooms[room_name].discard(old_ws)
                    if old_ws in self.socket_to_user:
                        del self.socket_to_user[old_ws]
                    del self.user_connections[room_name][username]
            
            # Add new connection
            self.active_rooms[room_name].add(ws)
            self.user_connections[room_name][username] = ws
            self.socket_to_user[ws] = (room_name, username)
            
            print(f"User {username} connected to room {room_name}. Total connections: {len(self.active_rooms[room_name])}")

    async def disconnect(self, room_name: str, ws: WebSocket):
        async with self.lock:
            # Remove from active rooms
            if room_name in self.active_rooms:
                self.active_rooms[room_name].discard(ws)
                if not self.active_rooms[room_name]:
                    del self.active_rooms[room_name]
            
            # Remove from user connections and socket mapping
            if ws in self.socket_to_user:
                stored_room, username = self.socket_to_user[ws]
                del self.socket_to_user[ws]
                
                # Remove user connection if it matches this websocket
                if (room_name in self.user_connections and 
                    username in self.user_connections[room_name] and 
                    self.user_connections[room_name][username] == ws):
                    del self.user_connections[room_name][username]
                    
                    # Clean up empty room
                    if not self.user_connections[room_name]:
                        del self.user_connections[room_name]
                    
                    print(f"User {username} disconnected from room {room_name}")

    async def disconnect_user_from_all_rooms(self, username: str):
        """Disconnect a user from all rooms"""
        async with self.lock:
            rooms_to_disconnect = []
            
            # Find all rooms where this user is connected
            for room_name, users in self.user_connections.items():
                if username in users:
                    rooms_to_disconnect.append((room_name, users[username]))
            
            # Disconnect from each room
            for room_name, ws in rooms_to_disconnect:
                try:
                    await ws.send_json({
                        "type": "force_disconnect",
                        "message": "Disconnected due to new connection"
                    })
                    await ws.close()
                except Exception as e:
                    print(f"Error force-disconnecting {username} from {room_name}: {e}")
                
                # Clean up will be handled by the disconnect method when the socket closes

    def get_room_users(self, room_name: str) -> list[str]:
        """Get list of usernames currently in a room"""
        if room_name in self.user_connections:
            return list(self.user_connections[room_name].keys())
        return []

    def is_user_in_room(self, room_name: str, username: str) -> bool:
        """Check if a specific user is in a room"""
        return (room_name in self.user_connections and 
                username in self.user_connections[room_name])

    async def broadcast(self, room_name: str, data: Any, exclude_socket: WebSocket = None, exclude_user: str = None):
        """Send JSON-serializable data to all sockets in room (best-effort)."""
        print(f"Broadcasting to room '{room_name}': {data}")
        if exclude_socket:
            print(f"Excluding sender socket from broadcast")
        if exclude_user:
            print(f"Excluding user '{exclude_user}' from broadcast")
        
        # copy to avoid holding lock while awaiting sends
        async with self.lock:
            sockets = list(self.active_rooms.get(room_name, []))
            users_in_room = list(self.user_connections.get(room_name, {}).keys())
        
        # Filter out excluded socket and/or user
        filtered_sockets = []
        for s in sockets:
            if exclude_socket and s == exclude_socket:
                continue
            if exclude_user and s in self.socket_to_user:
                _, username = self.socket_to_user[s]
                if username == exclude_user:
                    continue
            filtered_sockets.append(s)
            
        print(f"Found {len(filtered_sockets)} sockets in room (after exclusions)")
        print(f"Users in room: {users_in_room}")
        
        bad = []
        for i, s in enumerate(filtered_sockets):
            try:
                # Get username for this socket for logging
                username = "unknown"
                if s in self.socket_to_user:
                    _, username = self.socket_to_user[s]
                
                print(f"Sending to socket {i+1} (user: {username})")
                await s.send_json(data)
                print(f"Successfully sent to socket {i+1} (user: {username})")
            except Exception as e:
                print(f"Failed to send to socket {i+1} (user: {username}): {e}")
                bad.append(s)
        
        # cleanup bad sockets
        if bad:
            print(f"Cleaning up {len(bad)} bad sockets")
            async with self.lock:
                for s in bad:
                    self.active_rooms.get(room_name, set()).discard(s)
                    if s in self.socket_to_user:
                        _, username = self.socket_to_user[s]
                        if (room_name in self.user_connections and 
                            username in self.user_connections[room_name] and
                            self.user_connections[room_name][username] == s):
                            del self.user_connections[room_name][username]
                        del self.socket_to_user[s]

# single instance to import
manager = ConnectionManager()

class ConnectionRefusedError(Exception):
    """Raised when a connection is refused due to duplicate user"""
    pass
