from dbManager import DatabaseManager as db_manager

class RoomService:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.rooms = self._fetch_rooms()

    def _fetch_rooms(self):
        """Fetches all rooms from the database."""
        rooms = {}
        db_rooms = self.db_manager.fetch_all(query="SELECT * FROM rooms")
        for room in db_rooms:
            rooms[room['name']] = room.get('members', [])
        return rooms

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