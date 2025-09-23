
class RoomService:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def room_exists(self, room_name):
        """Check if a room exists by room_key."""
        rooms = self.db_manager.fetch_all("SELECT id FROM rooms WHERE room_key = ?", (room_name,))
        return len(rooms) > 0

    def create_room(self, room_name, created_by_user_id):
        """Creates a new chat room."""
        if self.room_exists(room_name):
            return {"success": False, "message": f"Room '{room_name}' already exists."}
        
        try:
            self.db_manager.execute_query("INSERT INTO rooms (room_key, created_by) VALUES (?, ?)", 
                                        (room_name, created_by_user_id))
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

    def join_room(self, room_name):
        """Check if a user can join a room (room exists)."""
        if not self.room_exists(room_name):
            return {"success": False, "message": f"Room '{room_name}' does not exist."}
        return {"success": True, "message": f"Successfully joined room '{room_name}'."}

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
=======
from dbManager import DatabaseManager

class RoomService:
    def __init__(self):
        

    def create_room(self, room_name):
        """Creates a new chat room."""
        if room_name in self.rooms:
            return f"Room '{room_name}' already exists."
        self.rooms[room_name] = []
        return f"Room '{room_name}' created successfully."

    def delete_room(self, room_name):
        """Deletes an existing chat room."""
        if room_name not in self.rooms:
            return f"Room '{room_name}' does not exist."
        del self.rooms[room_name]
        return f"Room '{room_name}' deleted successfully."

    def add_member(self, room_name, member_name):
        """Adds a member to a chat room."""
        if room_name not in self.rooms:
            return f"Room '{room_name}' does not exist."
        if member_name in self.rooms[room_name]:
            return f"Member '{member_name}' is already in the room '{room_name}'."
        self.rooms[room_name].append(member_name)
        return f"Member '{member_name}' added to room '{room_name}'."

    def remove_member(self, room_name, member_name):
        """Removes a member from a chat room."""
        if room_name not in self.rooms:
            return f"Room '{room_name}' does not exist."
        if member_name not in self.rooms[room_name]:
            return f"Member '{member_name}' is not in the room '{room_name}'."
        self.rooms[room_name].remove(member_name)
        return f"Member '{member_name}' removed from room '{room_name}'."

    def list_rooms(self):
        """Lists all chat rooms."""
        return list(self.rooms.keys())

    def list_members(self, room_name):
        """Lists all members in a chat room."""
        if room_name not in self.rooms:
            return f"Room '{room_name}' does not exist."
        return self.rooms[room_name]

