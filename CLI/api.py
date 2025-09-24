import requests
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import threading
import time

# WebSocket import - optional dependency
try:
    import websocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    websocket = None

class IgniteAPIClient:
    """
    API client for the Ignite Chat application backend.
    Provides interface to all backend routes with authentication handling.
    """
    
    def __init__(self, base_url: str = "http://homebred-irredeemably-madie.ngrok-free.dev/"):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the backend server
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        
    def _get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """Get headers for requests with optional authentication."""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if include_auth and self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
            
        return headers
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     include_auth: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to the backend.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            data: Request data for POST requests
            include_auth: Whether to include authentication header
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON data
            
        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(include_auth)
        
        # Merge any additional headers
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))
            
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers, **kwargs)
            elif method.upper() == 'POST':
                response = self.session.post(url, headers=headers, json=data, **kwargs)
            elif method.upper() == 'PUT':
                response = self.session.put(url, headers=headers, json=data, **kwargs)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            # Raise exception for bad status codes
            response.raise_for_status()
            
            # Try to parse JSON, fallback to text if not JSON
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"text": response.text}
                
        except requests.RequestException as e:
            # Try to extract error message from response if available
            try:
                error_data = e.response.json() if hasattr(e, 'response') and e.response else {}
                error_message = error_data.get('detail', str(e))
            except (json.JSONDecodeError, AttributeError):
                error_message = str(e)
                
            raise requests.RequestException(f"Request failed: {error_message}") from e

    # Authentication Methods
    def register(self, username: str, password: str) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            username: Username for the new user
            password: Password (must be at least 6 characters)
            
        Returns:
            Registration response
        """
        data = {
            "username": username,
            "password": password
        }
        return self._make_request('POST', '/register', data, include_auth=False)
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login and obtain access token.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Login response with access_token and token_type
        """
        data = {
            "username": username,
            "password": password
        }
        response = self._make_request('POST', '/login', data, include_auth=False)
        
        # Store token for future requests
        if 'access_token' in response:
            self.access_token = response['access_token']
            # Calculate token expiration (30 minutes from backend)
            self.token_expires_at = datetime.now() + timedelta(minutes=30)
            
        return response
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated with valid token."""
        return (self.access_token is not None and 
                self.token_expires_at is not None and 
                datetime.now() < self.token_expires_at)
    
    def logout(self):
        """Clear authentication token."""
        self.access_token = None
        self.token_expires_at = None

    # Room Management Methods
    def create_room(self, room_name: str, private: bool = False, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new chat room.
        
        Args:
            room_name: Name of the room to create
            private: Whether the room is private (default: False)
            password: Password for the room (optional)
            
        Returns:
            Room creation response
        """
        data = {
            "room_name": room_name,
            "private": private
        }
        if password:
            data["password"] = password
            
        return self._make_request('POST', '/create_room', data)
    
    def join_room(self, room_name: str, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Join an existing room.
        
        Args:
            room_name: Name of the room to join
            password: Password for the room (if required)
            
        Returns:
            Join room response
        """
        data = {
            "room_name": room_name
        }
        if password:
            data["password"] = password
            
        return self._make_request('POST', '/join_room', data)
    
    def get_room_status(self, room_name: str) -> Dict[str, Any]:
        """
        Get the status of a room including connected users.
        
        Args:
            room_name: Name of the room
            
        Returns:
            Room status information
        """
        return self._make_request('GET', f'/room-status/{room_name}')

    # Message Methods
    def send_message(self, room_name: str, message: str) -> Dict[str, Any]:
        """
        Send a message to a room.
        
        Args:
            room_name: Name of the room
            message: Message content
            
        Returns:
            Send message response
        """
        data = {
            "room_name": room_name,
            "message": message
        }
        return self._make_request('POST', '/send_message', data)
    
    def get_messages(self, room_name: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Get messages from a room.
        
        Args:
            room_name: Name of the room
            limit: Maximum number of messages to retrieve (optional)
            
        Returns:
            Messages and count
        """
        if limit is not None:
            endpoint = f'/get_messages/{room_name}/{limit}'
        else:
            endpoint = f'/get_messages/{room_name}'
            
        return self._make_request('GET', endpoint)
    
    def get_message_count(self, room_id: int) -> Dict[str, Any]:
        """
        Get the total number of messages in a room.
        
        Args:
            room_id: ID of the room
            
        Returns:
            Message count information
        """
        return self._make_request('GET', f'/messages/count/{room_id}')

    # Utility Methods
    def get_root(self) -> Dict[str, Any]:
        """Get root endpoint response."""
        return self._make_request('GET', '/', include_auth=False)
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information for accessing the server."""
        return self._make_request('GET', '/network-info', include_auth=False)

class WebSocketClient:
    """
    WebSocket client for real-time messaging with the Ignite Chat backend.
    Note: Requires websocket-client package (pip install websocket-client)
    """
    
    def __init__(self, base_url: str = "ws://localhost:8000", token: Optional[str] = None):
        """
        Initialize WebSocket client.
        
        Args:
            base_url: WebSocket base URL (default: ws://localhost:8000)
            token: JWT token for authentication
        """
        if not WEBSOCKET_AVAILABLE:
            raise ImportError("websocket-client package is required for WebSocket functionality. Install with: pip install websocket-client")
        
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.ws = None
        self.is_connected = False
        self.message_handlers = []
        self._listen_thread: Optional[threading.Thread] = None
        self._stop_listening = False
    
    def connect(self, room_name: str) -> bool:
        """
        Connect to a room via WebSocket.
        
        Args:
            room_name: Name of the room to connect to
            
        Returns:
            True if connection successful, False otherwise
        """
        if not WEBSOCKET_AVAILABLE:
            raise ImportError("websocket-client package is required")
            
        try:
            ws_url = f"{self.base_url}/ws/{room_name}"
            self.ws = websocket.create_connection(ws_url)  # type: ignore
            
            # Send authentication message
            auth_message = {
                "type": "auth",
                "token": self.token
            }
            self.ws.send(json.dumps(auth_message))
            
            # Wait for auth response
            response = json.loads(self.ws.recv())
            if response.get("type") == "auth_success":
                self.is_connected = True
                self._stop_listening = False
                
                # Start listening thread
                self._listen_thread = threading.Thread(target=self._listen_for_messages, daemon=True)
                self._listen_thread.start()
                
                return True
            else:
                error_msg = response.get("message", "Authentication failed")
                print(f"WebSocket auth failed: {error_msg}")
                self.ws.close()
                return False
                
        except Exception as e:
            print(f"WebSocket connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from WebSocket."""
        self._stop_listening = True
        self.is_connected = False
        
        if self.ws:
            self.ws.close()
            self.ws = None
            
        if self._listen_thread and self._listen_thread.is_alive():
            self._listen_thread.join(timeout=1)
    
    def send_message(self, message: str):
        """
        Send a message through WebSocket.
        
        Args:
            message: Message content to send
        """
        if not self.is_connected or not self.ws:
            raise RuntimeError("WebSocket not connected")
            
        message_data = {
            "type": "send_message",
            "message": message
        }
        self.ws.send(json.dumps(message_data))
    
    def add_message_handler(self, handler):
        """
        Add a message handler function.
        
        Args:
            handler: Function that takes a message dict as parameter
        """
        self.message_handlers.append(handler)
    
    def remove_message_handler(self, handler):
        """Remove a message handler."""
        if handler in self.message_handlers:
            self.message_handlers.remove(handler)
    
    def _listen_for_messages(self):
        """Listen for incoming WebSocket messages (runs in separate thread)."""
        while not self._stop_listening and self.is_connected and self.ws:
            try:
                message = self.ws.recv()
                if message:
                    try:
                        data = json.loads(message)
                        # Call all registered message handlers
                        for handler in self.message_handlers:
                            try:
                                handler(data)
                            except Exception as e:
                                print(f"Error in message handler: {e}")
                    except json.JSONDecodeError:
                        print(f"Received non-JSON message: {message}")
                        
            except Exception as e:
                # Handle WebSocket disconnection and other errors
                if "Connection is already closed" in str(e) or "WebSocket connection" in str(e):
                    print("WebSocket connection closed")
                    break
                else:
                    print(f"Error receiving WebSocket message: {e}")
                    break
        
        self.is_connected = False


# Example usage and convenience functions
def create_client() -> IgniteAPIClient:
    """Create a new API client instance."""
    return IgniteAPIClient()

def create_websocket_client(token: Optional[str] = None) -> WebSocketClient:
    """Create a new WebSocket client instance."""
    return WebSocketClient(token=token)


# Example usage
if __name__ == "__main__":
    # Example of how to use the API client
    client = create_client()
    
    try:
        # Test connection
        print("Testing connection...")
        root_response = client.get_root()
        print(f"Root response: {root_response}")
        
        # Register a user (optional, uncomment if needed)
        # print("Registering user...")
        # register_response = client.register("test_user", "test_password")
        # print(f"Register response: {register_response}")
        
        # Login
        print("Logging in...")
        login_response = client.login("cam", "123456")
        print(f"Login response: {login_response}")
        
        if client.is_authenticated():
            print("Successfully authenticated!")
            
            # Create a room
            print("Creating room...")
            room_response = client.create_room("test_room")
            print(f"Room creation response: {room_response}")
            
            # Send a message
            print("Sending message...")
            message_response = client.send_message("test_room", "Hello from API client!")
            print(f"Message response: {message_response}")
            
            # Get messages
            print("Getting messages...")
            messages_response = client.get_messages("test_room")
            print(f"Messages response: {messages_response}")
            
        else:
            print("Authentication failed")
            
    except Exception as e:
        print(f"Error: {e}")