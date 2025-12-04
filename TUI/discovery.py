"""
mDNS/DNS-SD service discovery for finding Ignite servers on the local network.

Uses Zeroconf (Python implementation of mDNS/DNS-SD) to discover and advertise
Ignite chat servers. Clients can find servers without knowing their IP addresses.
"""

import logging
import socket
import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

try:
    from zeroconf import ServiceBrowser, ServiceInfo, ServiceListener, Zeroconf
    ZEROCONF_AVAILABLE = True
except ImportError:
    ZEROCONF_AVAILABLE = False
    ServiceListener = object  # Placeholder for type hints when zeroconf unavailable

logger = logging.getLogger(__name__)

# Service type for Ignite servers (follows DNS-SD naming conventions)
SERVICE_TYPE = "_ignite-chat._tcp.local."
SERVICE_NAME_PREFIX = "IgniteServer"


@dataclass
class DiscoveredServer:
    """Represents a discovered Ignite server on the network."""
    name: str
    host: str
    port: int
    addresses: List[str] = field(default_factory=list)
    properties: Dict[str, str] = field(default_factory=dict)
    discovered_at: float = field(default_factory=time.time)

    @property
    def base_url(self) -> str:
        """Returns the HTTP base URL for connecting to this server."""
        return f"http://{self.host}:{self.port}"

    @property
    def websocket_url(self) -> str:
        """Returns the WebSocket URL for connecting to this server."""
        return f"ws://{self.host}:{self.port}"


class ServerDiscoveryListener(ServiceListener):
    """Listener for mDNS service events."""

    def __init__(
        self,
        on_found: Optional[Callable[[DiscoveredServer], None]] = None,
        on_removed: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.servers: Dict[str, DiscoveredServer] = {}
        self._on_found = on_found
        self._on_removed = on_removed
        self._lock = threading.Lock()

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        """Called when a service is discovered."""
        info = zc.get_service_info(type_, name)
        if info is None:
            return

        server = self._parse_service_info(name, info)
        if server:
            with self._lock:
                self.servers[name] = server
            logger.info("Discovered server: %s at %s", server.name, server.base_url)
            if self._on_found:
                self._on_found(server)

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        """Called when a service is removed."""
        with self._lock:
            if name in self.servers:
                del self.servers[name]
        logger.info("Server removed: %s", name)
        if self._on_removed:
            self._on_removed(name)

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        """Called when a service is updated."""
        self.add_service(zc, type_, name)

    @staticmethod
    def _parse_service_info(name: str, info: ServiceInfo) -> Optional[DiscoveredServer]:
        """Parse ServiceInfo into a DiscoveredServer object."""
        addresses = [socket.inet_ntoa(addr) for addr in info.addresses if len(addr) == 4]
        if not addresses:
            return None

        properties = {}
        if info.properties:
            for key, value in info.properties.items():
                if isinstance(key, bytes):
                    key = key.decode("utf-8", errors="replace")
                if isinstance(value, bytes):
                    value = value.decode("utf-8", errors="replace")
                properties[key] = value

        return DiscoveredServer(
            name=name.replace(f".{SERVICE_TYPE}", ""),
            host=info.server.rstrip(".") if info.server else addresses[0],
            port=info.port,
            addresses=addresses,
            properties=properties,
        )


class ServerDiscovery:
    """
    Client-side mDNS discovery for finding Ignite servers on the local network.
    
    Usage:
        discovery = ServerDiscovery()
        discovery.start()
        
        # Wait for discovery
        servers = discovery.wait_for_servers(timeout=5.0)
        
        # Or get current servers
        servers = discovery.get_servers()
        
        discovery.stop()
    """

    def __init__(
        self,
        on_server_found: Optional[Callable[[DiscoveredServer], None]] = None,
        on_server_removed: Optional[Callable[[str], None]] = None,
    ) -> None:
        if not ZEROCONF_AVAILABLE:
            raise ImportError(
                "zeroconf is required for server discovery. Install with: pip install zeroconf"
            )

        self._zeroconf: Optional[Zeroconf] = None
        self._browser: Optional[ServiceBrowser] = None
        self._listener = ServerDiscoveryListener(
            on_found=on_server_found,
            on_removed=on_server_removed,
        )
        self._running = False

    def start(self) -> None:
        """Start listening for Ignite servers on the network."""
        if self._running:
            return

        self._zeroconf = Zeroconf()
        self._browser = ServiceBrowser(self._zeroconf, SERVICE_TYPE, self._listener)
        self._running = True
        logger.info("Started mDNS discovery for %s", SERVICE_TYPE)

    def stop(self) -> None:
        """Stop listening for servers."""
        if not self._running:
            return

        if self._browser:
            self._browser.cancel()
            self._browser = None
        if self._zeroconf:
            self._zeroconf.close()
            self._zeroconf = None
        self._running = False
        logger.info("Stopped mDNS discovery")

    def get_servers(self) -> List[DiscoveredServer]:
        """Get all currently discovered servers."""
        with self._listener._lock:
            return list(self._listener.servers.values())

    def wait_for_servers(
        self,
        timeout: float = 5.0,
        min_servers: int = 1,
    ) -> List[DiscoveredServer]:
        """
        Wait for servers to be discovered.
        
        Args:
            timeout: Maximum time to wait in seconds
            min_servers: Minimum number of servers to wait for
            
        Returns:
            List of discovered servers
        """
        start = time.time()
        while time.time() - start < timeout:
            servers = self.get_servers()
            if len(servers) >= min_servers:
                return servers
            time.sleep(0.1)
        return self.get_servers()

    def __enter__(self) -> "ServerDiscovery":
        self.start()
        return self

    def __exit__(self, *args) -> None:
        self.stop()


def discover_servers(timeout: float = 5.0) -> List[DiscoveredServer]:
    """
    Convenience function to discover Ignite servers on the local network.
    
    Args:
        timeout: How long to wait for discovery in seconds
        
    Returns:
        List of discovered servers
        
    Example:
        servers = discover_servers(timeout=3.0)
        if servers:
            client = IgniteAPIClient(base_url=servers[0].base_url)
    """
    if not ZEROCONF_AVAILABLE:
        raise ImportError(
            "zeroconf is required for server discovery. Install with: pip install zeroconf"
        )

    with ServerDiscovery() as discovery:
        return discovery.wait_for_servers(timeout=timeout)


def get_local_ip() -> str:
    """Get the local IP address of this machine."""
    try:
        # Create a dummy connection to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
