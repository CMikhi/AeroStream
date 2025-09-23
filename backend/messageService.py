from datetime import datetime
from typing import List, Dict, Optional, Any

class MessageService:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def send_message(self, user_id: int, room_id: int, content: str) -> Dict[str, Any]:
        """
        Send a message to a room.
        The timestamp is automatically set by the database using CURRENT_TIMESTAMP.
        
        Args:
            user_id: ID of the user sending the message
            room_id: ID of the room to send the message to
            content: The message content
            
        Returns:
            Dict with success status and message
        """
        try:
            self.db_manager.execute_query(
                "INSERT INTO messages (user_id, room_id, content) VALUES (?, ?, ?)",
                (user_id, room_id, content)
            )
            return {"success": True, "message": "Message sent successfully"}
        except Exception as e:
            return {"success": False, "message": f"Failed to send message: {str(e)}"}

    def get_room_messages(self, room_id: int, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Get all messages for a room in chronological order (oldest first).
        
        Args:
            room_id: ID of the room to get messages for
            limit: Optional limit on number of messages to return (most recent)
            
        Returns:
            Dict with success status and list of messages
        """
        try:
            # Query messages with user information, ordered by timestamp
            query = """
                SELECT 
                    m.id,
                    m.content,
                    m.timestamp,
                    m.user_id,
                    u.username
                FROM messages m
                JOIN users u ON m.user_id = u.id
                WHERE m.room_id = ?
                ORDER BY m.timestamp ASC
            """
            
            if limit:
                # Efficiently get the most recent messages in chronological order using LIMIT and OFFSET
                count_query = "SELECT COUNT(*) FROM messages WHERE room_id = ?"
                count_result = self.db_manager.fetch_all(count_query, (room_id,))
                total_count = count_result[0][0] if count_result else 0
                offset = max(total_count - limit, 0)
                query = """
                    SELECT 
                        m.id,
                        m.content,
                        m.timestamp,
                        m.user_id,
                        u.username
                    FROM messages m
                    JOIN users u ON m.user_id = u.id
                    WHERE m.room_id = ?
                    ORDER BY m.timestamp ASC
                    LIMIT ? OFFSET ?
                """
                params = (room_id, limit, offset)
            else:
                params = (room_id,)
            
            messages = self.db_manager.fetch_all(query, params)
            
            # Convert to list of dictionaries for easier JSON serialization
            message_list = []
            for msg in messages:
                message_list.append({
                    "id": msg[0],
                    "content": msg[1],
                    "timestamp": msg[2],
                    "user_id": msg[3],
                    "username": msg[4]
                })
            
            return {
                "success": True, 
                "messages": message_list,
                "count": len(message_list)
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to retrieve messages: {str(e)}"}

    def get_room_messages_by_name(self, room_name: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Get all messages for a room by room name in chronological order.
        
        Args:
            room_name: Name/key of the room to get messages for
            limit: Optional limit on number of messages to return
            
        Returns:
            Dict with success status and list of messages
        """
        try:
            # First get the room ID
            room_query = "SELECT id FROM rooms WHERE room_key = ?"
            rooms = self.db_manager.fetch_all(room_query, (room_name,))
            
            if not rooms:
                return {"success": False, "message": f"Room '{room_name}' not found"}
            
            room_id = rooms[0][0]
            return self.get_room_messages(room_id, limit)
            
        except Exception as e:
            return {"success": False, "message": f"Failed to retrieve messages: {str(e)}"}

    def delete_message(self, message_id: int, user_id: int) -> Dict[str, Any]:
        """
        Delete a message (only if the user owns it).
        
        Args:
            message_id: ID of the message to delete
            user_id: ID of the user attempting to delete (must match message owner)
            
        Returns:
            Dict with success status and message
        """
        try:
            # First check if the message exists and belongs to the user
            check_query = "SELECT id FROM messages WHERE id = ? AND user_id = ?"
            existing = self.db_manager.fetch_all(check_query, (message_id, user_id))
            
            if not existing:
                return {"success": False, "message": "Message not found or you don't have permission to delete it"}
            
            # Delete the message
            self.db_manager.execute_query("DELETE FROM messages WHERE id = ?", (message_id,))
            return {"success": True, "message": "Message deleted successfully"}
            
        except Exception as e:
            return {"success": False, "message": f"Failed to delete message: {str(e)}"}

    def get_message_count(self, room_id: int) -> int:
        """
        Get the total number of messages in a room.
        
        Args:
            room_id: ID of the room
            
        Returns:
            Number of messages in the room
        """
        try:
            result = self.db_manager.fetch_all("SELECT COUNT(*) FROM messages WHERE room_id = ?", (room_id,))
            return result[0][0] if result else 0
        except Exception:
            return 0