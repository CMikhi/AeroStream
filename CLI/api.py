import requests
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import threading
import time

# WebSocket import - optional dependency
try:
    import websocket  # provided by 'websocket-client'
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
    Browser-parity WebSocket client for the Ignite Chat backend.
    Mirrors the flow used by the working HTML client:
    - Connect -> send auth -> receive auth_success -> receive message_history
    - Send send_message events, receive message_sent/new_message
    - Handles user_joined/user_left/ping/pong

    Requires: websocket-client
    """

    def __init__(self, base_url: str = "ws://localhost:8000", token: Optional[str] = None):
        if not WEBSOCKET_AVAILABLE:
            raise ImportError(
                "websocket-client package is required for WebSocket functionality. Install with: pip install websocket-client"
            )

        self._original_base_url = base_url or "ws://localhost:8000"
        self.base_url = self._normalize_ws_base(self._original_base_url)
        self.token = token

        # Runtime fields
        self.ws = None  # WebSocketApp instance set on connect
        self.is_connected = False
        self._ready = threading.Event()  # set after auth_success is received
        self._stop = threading.Event()
        self._connection_thread = None
        self.message_handlers = []  # handlers receive the message dict

    # ---------------------- public api ----------------------
    def connect(self, room_name: str, api_client=None, wait_ready_seconds: float = 8.0) -> bool:
        """
        Connect to the room and complete the same handshake as the web client.
        Returns True only after auth_success is received.
        """
        # Optional HTTP join validation like the web client
        if api_client and hasattr(api_client, "join_room"):
            try:
                join_resp = api_client.join_room(room_name)
                print(f"[WS] join_room validation: {join_resp}")
            except Exception as e:
                print(f"[WS] join_room validation failed: {e}")
                return False

        ws_url = self._build_ws_url(room_name)
        origin = self._compute_origin()
        header = self._build_headers_with_origin(origin)
        print(f"[WS] Connecting to: {ws_url}\n      base_url={self.base_url}\n      origin={origin}\n      headers={header}")

        # Build WebSocketApp with bound handlers and headers (browser parity)
        self.ws = websocket.WebSocketApp(
            ws_url,
            header=header,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

        self._stop.clear()
        self._ready.clear()

        def _runner():
            try:
                # origin already set via header; keep pings like the browser keeps ws alive
                self.ws.run_forever(
                    ping_interval=25,
                    ping_timeout=10,
                )
            except Exception as e:
                print(f"[WS] run_forever exception: {e}")

        self._connection_thread = threading.Thread(target=_runner, daemon=True)
        self._connection_thread.start()

        # Wait until auth_success or timeout
        ok = self._ready.wait(timeout=wait_ready_seconds)
        self.is_connected = ok and not self._stop.is_set()
        if not self.is_connected:
            print("[WS] Did not become ready before timeout (no auth_success). Common causes: invalid token, room doesn't exist, proxy stripping headers/origin.")
        return self.is_connected

    def disconnect(self):
        self._stop.set()
        self.is_connected = False
        try:
            if self.ws:
                self.ws.close()
        finally:
            self.ws = None
            if self._connection_thread and self._connection_thread.is_alive():
                self._connection_thread.join(timeout=2)
            self._connection_thread = None

    def send_message(self, message: str):
        if not (self.ws and self.is_connected):
            raise RuntimeError("WebSocket not connected")
        payload = {"type": "send_message", "message": message}
        try:
            self.ws.send(json.dumps(payload))
        except Exception as e:
            print(f"[WS] send_message failed: {e}")
            raise

    def add_message_handler(self, handler):
        self.message_handlers.append(handler)

    def remove_message_handler(self, handler):
        if handler in self.message_handlers:
            self.message_handlers.remove(handler)

    # ---------------------- internals ----------------------
    def _normalize_ws_base(self, base_url: str) -> str:
        # Accept http(s) or ws(s) or plain host
        url = base_url.strip()
        if url.endswith('/'):
            url = url[:-1]

        if url.startswith("http://"):
            url = "ws://" + url[len("http://"):]
        elif url.startswith("https://"):
            url = "wss://" + url[len("https://"):]
        elif url.startswith("ws://") or url.startswith("wss://"):
            pass
        else:
            url = f"ws://{url}"
        return url

    def _build_ws_url(self, room_name: str) -> str:
        # Ensure we don't duplicate /ws segment
        if self.base_url.endswith("/ws"):
            return f"{self.base_url}/{room_name}"
        return f"{self.base_url}/ws/{room_name}"

    def _compute_origin(self) -> str:
        # Map ws(s) -> http(s) for Origin header
        if self.base_url.startswith("wss://"):
            return "https://" + self.base_url[len("wss://"):]
        if self.base_url.startswith("ws://"):
            return "http://" + self.base_url[len("ws://"):]
        return "http://localhost"

    def _build_headers(self) -> List[str]:
        """Deprecated: kept for backward compatibility."""
        return ["User-Agent: websocket-client-python"]

    def _build_headers_with_origin(self, origin: str) -> List[str]:
        headers: List[str] = [
            "User-Agent: websocket-client-python",
            f"Origin: {origin}",
        ]
        # Some reverse proxies (like ngrok) gate on this header when accessed outside a browser
        if "ngrok" in self.base_url or "ngrok-free.dev" in self.base_url:
            headers.append("ngrok-skip-browser-warning: true")
        return headers

    # ---------------------- ws callbacks ----------------------
    def _on_open(self, ws):
        print("[WS] on_open -> sending auth payload")
        try:
            auth = {"type": "auth", "token": self.token}
            ws.send(json.dumps(auth))
        except Exception as e:
            print(f"[WS] failed to send auth: {e}")

    def _emit(self, data: Dict[str, Any]):
        for handler in list(self.message_handlers):
            try:
                handler(data)
            except Exception as e:
                print(f"[WS] handler error: {e}")

    def _on_message(self, ws, message: str):
        try:
            data = json.loads(message)
        except Exception as e:
            print(f"[WS] bad json: {e}; raw={message!r}")
            return

        mtype = data.get("type")
        if mtype == "auth_success":
            print("[WS] auth_success received; connection ready")
            self._ready.set()
            self.is_connected = True
        elif mtype == "error":
            print(f"[WS] server error: {data.get('message')}")
        elif mtype == "message_history":
            # Pass through to TUI so it can render the backlog
            pass
        elif mtype in ("new_message", "message_sent", "user_joined", "user_left", "pong"):
            pass
        # Emit everything for the TUI to handle uniformly
        self._emit(data)

    def _on_error(self, ws, error):
        print(f"[WS] on_error: {error}")
        # Keep connection state pessimistic
        self.is_connected = False

    def _on_close(self, ws, status_code, msg):
        print(f"[WS] on_close: {status_code} {msg}")
        self.is_connected = False
        self._stop.set()
    



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