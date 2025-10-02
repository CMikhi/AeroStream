import base64
import json
import logging
import threading
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:  # Optional dependency for realtime features
    import socketio 
    SOCKETIO_AVAILABLE = True
except ImportError:
    raise ImportError("python-socketio is required for realtime features. Install with: pip install python-socketio")

logger = logging.getLogger(__name__)
MessageHandler = Callable[[Dict[str, Any]], None]


class IgniteAPIError(Exception):
    """Custom exception for Ignite API client failures."""

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload or {}


class IgniteAPIClient:
    """HTTP client for the NestJS Ignite backend with token management."""

    DEFAULT_TIMEOUT = 10.0

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        *,
        timeout: float = DEFAULT_TIMEOUT,
        retry_total: int = 3,
        backoff_factor: float = 0.5,
    ) -> None:
        self.base_url = self._normalize_base(base_url)
        self.timeout = timeout
        self.session = requests.Session()
        self._configure_retries(retry_total, backoff_factor)

        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_type: Optional[str] = None
        self.user_id: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self._token_refresh_margin = timedelta(seconds=30)

        self._last_response: Optional[Response] = None
        self._lock = threading.Lock()

    # ---------------------------------------------------------------------
    # Session setup helpers
    # ---------------------------------------------------------------------
    @staticmethod
    def _normalize_base(base_url: str) -> str:
        url = (base_url or "http://localhost:8000").strip()
        if not url.startswith(("http://", "https://")):
            url = f"http://{url}"
        return url.rstrip("/ ")

    def _configure_retries(self, retry_total: int, backoff_factor: float) -> None:
        retry = Retry(
            total=retry_total,
            read=retry_total,
            connect=retry_total,
            backoff_factor=backoff_factor,
            status_forcelist=(408, 429, 500, 502, 503, 504),
            allowed_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _build_url(self, endpoint: str) -> str:
        path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        return f"{self.base_url}{path}"

    # ---------------------------------------------------------------------
    # Token utilities
    # ---------------------------------------------------------------------
    @staticmethod
    def _decode_jwt_exp(token: str) -> Optional[datetime]:
        try:
            payload_segment = token.split(".")[1]
            padding = "=" * (-len(payload_segment) % 4)
            decoded = base64.urlsafe_b64decode(payload_segment + padding)
            payload = json.loads(decoded)
            exp = payload.get("exp")
            if exp is not None:
                return datetime.fromtimestamp(float(exp), tz=timezone.utc)
        except Exception:  # pragma: no cover - defensive logging
            logger.debug("Failed to decode JWT expiration", exc_info=True)
        return None

    def _update_tokens(self, payload: Dict[str, Any]) -> None:
        access = payload.get("access_token") or payload.get("accessToken")
        refresh = (
            payload.get("refresh_token")
            or payload.get("refreshToken")
            or payload.get("newRefreshToken")
        )
        user_id = payload.get("user_id") or payload.get("userID")

        with self._lock:
            if access:
                self.access_token = access
                self.token_expires_at = self._decode_jwt_exp(access)
            if refresh:
                self.refresh_token = refresh
            if user_id:
                self.user_id = str(user_id)
            self.token_type = payload.get("token_type", self.token_type)

    def _get_valid_token(self) -> str:
        if not self.access_token:
            raise IgniteAPIError("Authentication required", status_code=401)

        if self.token_expires_at is None:
            return self.access_token

        now = datetime.now(timezone.utc)
        if now + self._token_refresh_margin < self.token_expires_at:
            return self.access_token

        if now >= self.token_expires_at:
            if self.refresh_token:
                self.refresh_access_token()
                if not self.access_token:
                    raise IgniteAPIError("Unable to refresh access token", status_code=401)
                return self.access_token
            raise IgniteAPIError("Access token expired", status_code=401)

        # approaching expiry but not yet expired; try to refresh opportunistically
        if self.refresh_token:
            try:
                self.refresh_access_token()
            except IgniteAPIError:
                logger.warning("Automatic token refresh failed", exc_info=True)
        return self.access_token

    # ---------------------------------------------------------------------
    # Core request helper
    # ---------------------------------------------------------------------
    def _make_request(
        self,
        method: str,
        endpoint: str,
        *,
        json_payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        include_auth: bool = True,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        url = self._build_url(endpoint)
        headers: Dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": "IgniteTUI/1.0",
        }
        if json_payload is not None:
            headers["Content-Type"] = "application/json"

        if include_auth:
            headers["Authorization"] = f"Bearer {self._get_valid_token()}"

        effective_timeout = timeout or getattr(self.session, "timeout", self.timeout)

        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                json=json_payload,
                params=params,
                headers=headers,
                timeout=effective_timeout,
            )
        except requests.RequestException as exc:
            raise IgniteAPIError(
                "Network error while contacting Ignite backend",
                payload={"endpoint": endpoint, "error": str(exc)},
            ) from exc

        return self._process_response(response)

    def _process_response(self, response: Response) -> Dict[str, Any]:
        self._last_response = response

        if response.status_code == 204:
            data: Dict[str, Any] = {}
        else:
            try:
                data = response.json()
            except json.JSONDecodeError:
                data = {"raw": response.text}

        if 200 <= response.status_code < 300:
            return data

        message = (
            data.get("message")
            or data.get("detail")
            or response.reason
            or "Request to Ignite backend failed"
        )
        raise IgniteAPIError(message, status_code=response.status_code, payload=data)

    # ---------------------------------------------------------------------
    # Authentication API
    # ---------------------------------------------------------------------
    def register(
        self,
        username: str,
        password: str,
        *,
        role: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "username": username,
            "password": password,
        }
        if role:
            payload["role"] = role

        response = self._make_request("POST", "/register", json_payload=payload, include_auth=False)
        self._update_tokens(response)
        return response

    def login(self, username: str, password: str) -> Dict[str, Any]:
        payload = {"username": username, "password": password}
        response = self._make_request("POST", "/login", json_payload=payload, include_auth=False)
        self._update_tokens(response)
        return response

    def refresh_access_token(self) -> Dict[str, Any]:
        if not (self.refresh_token and self.user_id):
            raise IgniteAPIError("Refresh token is not available", status_code=401)

        payload = {
            "userID": self.user_id,
            "refreshToken": self.refresh_token,
        }
        response = self._make_request(
            "PATCH",
            "/auth/refresh",
            json_payload=payload,
            include_auth=False,
        )
        self._update_tokens(response)
        return response

    def get_current_user(self) -> Dict[str, Any]:
        return self._make_request("GET", "/auth/me")

    def is_authenticated(self) -> bool:
        if not self.access_token:
            return False
        if self.token_expires_at is None:
            return True
        return datetime.now(timezone.utc) < self.token_expires_at

    def logout(self) -> None:
        with self._lock:
            self.access_token = None
            self.refresh_token = None
            self.token_type = None
            self.user_id = None
            self.token_expires_at = None

    # ---------------------------------------------------------------------
    # Room management
    # ---------------------------------------------------------------------
    def create_room(
        self,
        room_name: str,
        *,
        private: bool = False,
        password: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "room_name": room_name,
            "private": private,
        }
        if private and password:
            payload["password"] = password
        response = self._make_request("POST", "/create_room", json_payload=payload)
        return response

    def join_room(self, room_name: str, password: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"room_name": room_name}
        if password:
            payload["password"] = password
        return self._make_request("POST", "/join_room", json_payload=payload)

    def list_rooms(self) -> Dict[str, Any]:
        return self._make_request("GET", "/rooms")

    def get_room(self, room_name: str) -> Dict[str, Any]:
        rooms_response = self.list_rooms()
        rooms = rooms_response.get("rooms", [])
        for room in rooms:
            if room.get("name") == room_name:
                return room
        raise IgniteAPIError(
            f"Room '{room_name}' not found",
            status_code=404,
            payload={"rooms": rooms},
        )

    # ---------------------------------------------------------------------
    # Messaging
    # ---------------------------------------------------------------------
    def send_message(self, room_name: str, message: str) -> Dict[str, Any]:
        payload = {"room_name": room_name, "message": message}
        return self._make_request("POST", "/send_message", json_payload=payload)

    def get_messages(self, room_name: str, *, limit: Optional[int] = None) -> Dict[str, Any]:
        params = {"limit": limit} if limit is not None else None
        endpoint = f"/messages/{room_name}"
        return self._make_request("GET", endpoint, params=params)

    def get_message_count(self, room_id: str) -> Dict[str, Any]:
        endpoint = f"/messages/count/{room_id}"
        return self._make_request("GET", endpoint)

    # ---------------------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------------------
    def get_root(self) -> Dict[str, Any]:
        return self._make_request("GET", "/", include_auth=False)

    def get_last_response(self) -> Optional[Response]:
        return self._last_response


class WebSocketClient:
    """Socket.IO client mirroring the browser flow used by the HTML test client."""

    SOCKET_EVENTS = (
        "auth_success",
        "message_history",
        "message_sent",
        "new_message",
        "user_joined",
        "user_left",
        "connection_replaced",
        "force_disconnect",
        "error",
        "pong",
    )

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        *,
        token: Optional[str] = None,
    ) -> None:
        if not SOCKETIO_AVAILABLE:
            raise ImportError(
                "python-socketio is required for realtime features. Install with: pip install python-socketio",
            )

        self.base_url = self._normalize_http_base(base_url)
        self.token = token
        self.namespace: Optional[str] = None
        self.client: Optional[Any] = None
        self.message_handlers: List[MessageHandler] = []

        self.is_connected = False
        self._ready = threading.Event()
        self._stop = threading.Event()
        self._last_error: Optional[str] = None
        self.user_context: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def connect(
        self,
        room_name: str,
        *,
        api_client: Optional[IgniteAPIClient] = None,
        wait_ready_seconds: float = 8.0,
        token: Optional[str] = None,
    ) -> bool:
        if token:
            self.token = token
        elif api_client and api_client.access_token:
            self.token = api_client.access_token

        if not self.token:
            raise IgniteAPIError("Authentication token is required for realtime connection", status_code=401)

        if api_client is not None:
            try:
                api_client.join_room(room_name)
            except IgniteAPIError as exc:
                logger.warning("Room join failed before websocket connect", exc_info=True)
                raise exc

        self.namespace = self._build_namespace(room_name)
        client = socketio.Client(  # type: ignore[attr-defined]
            reconnection=True,
            reconnection_attempts=4,
            reconnection_delay=1,
            reconnection_delay_max=5,
        )

        self.client = client
        self._register_event_handlers(self.namespace)

        self._ready.clear()
        self._stop.clear()
        self._last_error = None
        self.is_connected = False

        try:
            client.connect(
                self.base_url,
                namespaces=[self.namespace],
                transports=["websocket", "polling"],
                wait_timeout=wait_ready_seconds,
                headers=self._build_headers(),
            )
        except Exception as exc:  # pragma: no cover - network dependent
            self._last_error = str(exc)
            logger.error("Socket.IO connection failed", exc_info=True)
            self._cleanup_after_disconnect()
            return False

        ready = self._ready.wait(timeout=wait_ready_seconds)
        if not ready:
            logger.error("Socket.IO authentication timed out: %s", self._last_error)
            self.disconnect()
            return False

        self.is_connected = True
        return True

    def disconnect(self) -> None:
        self._stop.set()
        if self.client:
            try:
                self.client.disconnect()
            except Exception:  # pragma: no cover - defensive
                logger.debug("Socket.IO disconnect raised", exc_info=True)
        self._cleanup_after_disconnect()

    def send_message(self, message: str) -> None:
        if not message.strip():
            raise ValueError("Message content cannot be empty")
        if not (self.client and self.namespace and self.is_connected):
            raise RuntimeError("Socket.IO client is not connected")
        self.client.emit("send_message", {"message": message.strip()}, namespace=self.namespace)

    def ping(self) -> None:
        if self.client and self.namespace:
            self.client.emit("ping", namespace=self.namespace)

    def add_message_handler(self, handler: MessageHandler) -> None:
        if handler not in self.message_handlers:
            self.message_handlers.append(handler)

    def remove_message_handler(self, handler: MessageHandler) -> None:
        if handler in self.message_handlers:
            self.message_handlers.remove(handler)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_http_base(base_url: str) -> str:
        url = (base_url or "http://localhost:8000").strip()
        if url.startswith("ws://"):
            url = "http://" + url[len("ws://") :]
        elif url.startswith("wss://"):
            url = "https://" + url[len("wss://") :]
        elif not url.startswith(("http://", "https://")):
            url = f"http://{url}"
        return url.rstrip("/ ")

    @staticmethod
    def _build_namespace(room_name: str) -> str:
        safe = room_name.strip().replace(" ", "-")
        return f"/ws/{safe}"

    def _build_headers(self) -> Dict[str, str]:
        origin = self._compute_origin()
        headers = {
            "Origin": origin,
            "User-Agent": "IgniteTUI/1.0",
        }
        if "ngrok" in self.base_url or "ngrok-free.dev" in self.base_url:
            headers["ngrok-skip-browser-warning"] = "true"
        return headers

    def _compute_origin(self) -> str:
        if self.base_url.startswith("https://"):
            return self.base_url
        return self.base_url.replace("http://", "http://", 1)

    def _register_event_handlers(self, namespace: str) -> None:
        assert self.client is not None
        client = self.client

        @client.event(namespace=namespace)
        def connect() -> None:  # pragma: no cover - requires live server
            logger.debug("Socket.IO connected to %s", namespace)
            if not self.token:
                self._last_error = "Missing token after connect"
                self._ready.set()
                return
            client.emit("auth", {"token": self.token}, namespace=namespace)

        @client.event(namespace=namespace)
        def connect_error(data: Any) -> None:  # pragma: no cover - network dependent
            self._last_error = str(data)
            self._ready.set()

        @client.event(namespace=namespace)
        def disconnect() -> None:  # pragma: no cover - network dependent
            logger.info("Socket.IO disconnected from %s", namespace)
            self.is_connected = False
            self._stop.set()
            self._emit({"type": "disconnect", "message": "Disconnected"})

        for event in self.SOCKET_EVENTS:
            client.on(event, namespace=namespace)(self._make_event_handler(event))

    def _make_event_handler(self, event_name: str) -> Callable[[Any], None]:
        def handler(data: Any) -> None:
            payload: Dict[str, Any]
            if isinstance(data, dict):
                payload = dict(data)
            else:
                payload = {"data": data}
            payload.setdefault("type", event_name)

            if event_name == "auth_success":
                self.user_context = payload.get("user") if isinstance(payload.get("user"), dict) else None
                self.is_connected = True
                self._ready.set()
            elif event_name == "error":
                self._last_error = payload.get("message") or "Server returned error"

            self._emit(payload)

        return handler

    def _emit(self, data: Dict[str, Any]) -> None:
        for handler in list(self.message_handlers):
            try:
                handler(data)
            except Exception:  # pragma: no cover - user-provided handler failures
                logger.exception("Message handler raised an error")

    def _cleanup_after_disconnect(self) -> None:
        self.client = None
        self.namespace = None
        self.is_connected = False
        self._ready.clear()
        self._stop.set()


# Convenience factories -------------------------------------------------------

def create_client(**kwargs: Any) -> IgniteAPIClient:
    return IgniteAPIClient(**kwargs)


def create_websocket_client(**kwargs: Any) -> WebSocketClient:
    return WebSocketClient(**kwargs)