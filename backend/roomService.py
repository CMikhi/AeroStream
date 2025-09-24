class RoomService:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def room_exists(self, room_name):
        """Check if a room exists by room_key."""
        rooms = self.db_manager.fetch_all("SELECT id FROM rooms WHERE room_key = ?", (room_name,))
        return len(rooms) > 0

    def create_room(self, data, created_by_user_id):
        room_name = data.room_name
        private = data.private
        password = None
        if private:
            password = data.password

        """Creates a new chat room."""
        if self.room_exists(room_name):
            return {"success": False, "message": f"Room '{room_name}' already exists."}

        try:
            self.db_manager.execute_query(
            "INSERT INTO rooms (room_key, created_by, private, password) VALUES (?, ?, ?, ?)", 
            (room_name, created_by_user_id, private, password)
            )
            return {"success": True, "message": f"Room '{room_name}' created successfully."}
        except Exception as e:
            return {"success": False, "message": f"Failed to create room: {str(e)}"}

    def delete_room(self, room_name):
        """Deletes an existing chat room."""
        if not self.room_exists(room_name):
            return {"success": False, "message": f"Room '{room_name}' does not exist."}
        
        try:
            self.db_manager.execute_query("DELETE FROM rooms WHERE room_key = ?", (room_name,))
            return {"success": True, "message": f"Room '{room_name}' deleted successfully."}
        except Exception as e:
            return {"success": False, "message": f"Failed to delete room: {str(e)}"}

    def join_room(self, room_name, password=None):
        """Check if a user can join a room (room exists and password if private)."""
        if not self.room_exists(room_name):
            return {"success": False, "message": f"Room '{room_name}' does not exist."}
        
        # Check if room is private and validate password
        try:
            room_data = self.db_manager.fetch_all(
                "SELECT private, password FROM rooms WHERE room_key = ?", 
                (room_name,)
            )
            
            if not room_data:
                return {"success": False, "message": f"Room '{room_name}' does not exist."}
            
            room = room_data[0]
            is_private = room[0]  # private column
            stored_password = room[1]  # password column
            
            # If room is private, password is required
            if is_private:
                if not password:
                    return {"success": False, "message": f"Room '{room_name}' is private. Password required."}
                
                if password != stored_password:
                    return {"success": False, "message": "Incorrect password for private room."}
            
            return {"success": True, "message": f"Successfully joined room '{room_name}'."}
            
        except Exception as e:
            return {"success": False, "message": f"Failed to join room: {str(e)}"}

    def list_rooms(self):
        """Lists all chat rooms."""
        try:
            rooms = self.db_manager.fetch_all("SELECT room_key FROM rooms")
            return {"success": True, "rooms": [room[0] for room in rooms]}
        except Exception as e:
            return {"success": False, "message": f"Failed to fetch rooms: {str(e)}"}

    def get_room_id(self, room_name):
        """Get the room ID by room name."""
        rooms = self.db_manager.fetch_all("SELECT id FROM rooms WHERE room_key = ?", (room_name,))
        return rooms[0][0] if rooms else None
