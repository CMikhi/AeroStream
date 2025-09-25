from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Middle, Vertical, Horizontal
from textual.widgets import Static, Footer, Input, Button
from textual.screen import Screen, ModalScreen
from textual.message import Message
from PIL import Image
from PIL import ImageEnhance
from keyboard_handler import KeyboardHandler, KeyboardMode, CommandArgs
from floating_island import FloatingCommandLine, FloatingResultPanel
from api import IgniteAPIClient
import json
import os

# Note: client will be initialized per AeroStream instance to avoid conflicts

# TUI Application with integrated chat rooms
# - Login/Registration system with authentication
# - Main menu navigation 
# - Multi-room chat interface with room management
# - API integration for server communication with local fallback
# - Responsive design matching the app's aesthetic

class Colors:
    """ANSI color codes for terminal output"""
    # Standard colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Reset
    RESET = '\033[0m'


def apply_rainbow_effect(text: str) -> str:
    """Apply rainbow color effect to text"""
    rainbow_colors = [
        Colors.RED, Colors.YELLOW, Colors.GREEN, 
        Colors.CYAN, Colors.BLUE, Colors.MAGENTA
    ]
    colored_text = ""
    color_index = 0
    
    for char in text:
        if char != ' ':
            colored_text += rainbow_colors[color_index % len(rainbow_colors)] + char
            color_index += 1
        else:
            colored_text += char
    
    return colored_text + Colors.RESET


def apply_fire_effect(text: str, line_num: int) -> str:
    """Apply fire color effect (red to yellow gradient)"""
    fire_colors = [Colors.BRIGHT_RED, Colors.RED, Colors.YELLOW, Colors.BRIGHT_YELLOW]
    color = fire_colors[line_num % len(fire_colors)]
    
    colored_text = ""
    for char in text:
        if char != ' ':
            colored_text += color + char
        else:
            colored_text += char
    
    return colored_text + Colors.RESET


def apply_ocean_effect(text: str, line_num: int) -> str:
    """Apply ocean color effect (blue to cyan gradient)"""
    ocean_colors = [Colors.BLUE, Colors.BRIGHT_BLUE, Colors.CYAN, Colors.BRIGHT_CYAN]
    color = ocean_colors[line_num % len(ocean_colors)]
    
    colored_text = ""
    for char in text:
        if char != ' ':
            colored_text += color + char
        else:
            colored_text += char
    
    return colored_text + Colors.RESET


def image_to_ascii(image_path: str, width: int = 100, contrast_factor: float = 1.5, brightness_factor: float = 1.2, threshold: int = 150, color: str = None) -> str:
    """Convert an image to ASCII art with increased contrast and brightness, and remove surrounding whitespace.
    Skip sections under a certain brightness or confidence.
    
    Args:
        image_path: Path to the image file
        width: Width of the ASCII art
        contrast_factor: Contrast enhancement factor
        brightness_factor: Brightness enhancement factor
        threshold: Threshold for removing whitespace
        color: Color theme ('red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'white', 
               'bright_red', 'bright_green', 'bright_blue', 'bright_yellow', 'bright_magenta', 
               'bright_cyan', 'bright_white', 'rainbow', 'fire', 'ocean', or None for no color)
    """
    
    # Color themes mapping
    color_themes = {
        'red': Colors.RED,
        'green': Colors.GREEN,
        'blue': Colors.BLUE,
        'yellow': Colors.YELLOW,
        'magenta': Colors.MAGENTA,
        'cyan': Colors.CYAN,
        'white': Colors.WHITE,
        'bright_red': Colors.BRIGHT_RED,
        'bright_green': Colors.BRIGHT_GREEN,
        'bright_blue': Colors.BRIGHT_BLUE,
        'bright_yellow': Colors.BRIGHT_YELLOW,
        'bright_magenta': Colors.BRIGHT_MAGENTA,
        'bright_cyan': Colors.BRIGHT_CYAN,
        'bright_white': Colors.BRIGHT_WHITE,
    }

    chars = ["@", "#", "S", "%", "?", "*", "+", " ", " ", " ", " "]  # Replace "." with " " for whitespace
    try:
        img = Image.open(image_path)
        img = img.convert("L")  # Convert to grayscale

        # Increase contrast and brightness
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast_factor)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness_factor)

        # Apply threshold to remove surrounding whitespace
        img = Image.eval(img, lambda p: 255 if p > threshold else 0)

        aspect_ratio = img.height / img.width
        new_height = int(aspect_ratio * width * 0.35)
        img = img.resize((width, new_height))
        pixels = img.getdata()

        ascii_str = ""
        for pixel in pixels:
            ascii_str += chars[pixel // 25]

        ascii_lines = [ascii_str[i:i + width] for i in range(0, len(ascii_str), width)]
        
        # Apply color effects if specified (using Textual markup instead of ANSI codes)
        if color:
            colored_lines = []
            for line_num, line in enumerate(ascii_lines):
                if color == 'rainbow':
                    # For Textual, we'll use a single color per line cycling through rainbow
                    rainbow_colors_textual = ["red", "yellow", "green", "cyan", "blue", "magenta"]
                    textual_color = rainbow_colors_textual[line_num % len(rainbow_colors_textual)]
                    colored_lines.append(f"[{textual_color}]{line}[/]")
                elif color == 'fire':
                    # Fire effect using Textual colors
                    fire_colors_textual = ["bright_red", "red", "yellow", "bright_yellow"]
                    textual_color = fire_colors_textual[line_num % len(fire_colors_textual)]
                    colored_lines.append(f"[{textual_color}]{line}[/]")
                elif color == 'ocean':
                    # Ocean effect using Textual colors
                    ocean_colors_textual = ["blue", "green", "cyan", "bright_cyan"]
                    textual_color = ocean_colors_textual[line_num % len(ocean_colors_textual)]
                    colored_lines.append(f"[{textual_color}]{line}[/]")
                elif color in color_themes:
                    # Map ANSI color names to Textual color names
                    textual_color_map = {
                        'red': 'red',
                        'green': 'green', 
                        'blue': 'blue',
                        'yellow': 'yellow',
                        'magenta': 'magenta',
                        'cyan': 'cyan',
                        'white': 'white',
                        'bright_red': 'bright_red',
                        'bright_green': 'bright_green',
                        'bright_blue': 'bright_blue', 
                        'bright_yellow': 'bright_yellow',
                        'bright_magenta': 'bright_magenta',
                        'bright_cyan': 'bright_cyan',
                        'bright_white': 'bright_white',
                    }
                    textual_color = textual_color_map.get(color, 'white')
                    colored_lines.append(f"[{textual_color}]{line}[/]")
                else:
                    colored_lines.append(line)  # No color if unknown
            return "\n".join(colored_lines)
        
        return "\n".join(ascii_lines)
    except Exception as e:
        return f"Error generating ASCII art: {e}"

# Generate ASCII art from a .png file with color
try:
    CUSTOM_ASCII_ART = image_to_ascii("CLI/assets/ascii_art.png", width=80, color="red")
except FileNotFoundError:
    try:
        with open("CLI/assets/simple_ascii-art.txt", "r") as file:
            original_art = file.read()
            # Apply color using Textual markup
            CUSTOM_ASCII_ART = f"[bright_cyan]{original_art}[/]"
    except FileNotFoundError:
        # Fallback to simple text with color
        fallback_art = r"""
        ___            _ _       
        | _|__ _ _ __ (_) |_ ___ 
        | |/ _` | '_ \| | __/ _ \
        | | (_| | | | | | ||  __/
        |___\__, |_| |_|_|\__\___|
            |___/                
        """
        # Apply color using Textual markup
        CUSTOM_ASCII_ART = f"[bright_cyan]{fallback_art}[/]"

# Generate alternative colored ASCII art variants for different contexts
try:
    # Rainbow version for special occasions
    RAINBOW_ASCII_ART = image_to_ascii("CLI/assets/ascii_art.png", width=80, color="rainbow")
    
    # Fire effect for energy/action contexts  
    FIRE_ASCII_ART = image_to_ascii("CLI/assets/ascii_art.png", width=80, color="fire")
    
    # Ocean effect for calm/peaceful contexts
    OCEAN_ASCII_ART = image_to_ascii("CLI/assets/ascii_art.png", width=80, color="ocean")
    
    # Green for success/login contexts
    SUCCESS_ASCII_ART = image_to_ascii("CLI/assets/ascii_art.png", width=80, color="bright_green")

    ASCII_ART = image_to_ascii("CLI/assets/ascii_art.png", width=80, color="cyan")

except FileNotFoundError:
    # Use the main ASCII art as fallbacks
    RAINBOW_ASCII_ART = CUSTOM_ASCII_ART
    FIRE_ASCII_ART = CUSTOM_ASCII_ART  
    OCEAN_ASCII_ART = CUSTOM_ASCII_ART
    SUCCESS_ASCII_ART = CUSTOM_ASCII_ART

def get_colored_ascii_art(color: str = "bright_cyan") -> str:
    """Get ASCII art with specified color. Useful for dynamic color changes."""
    try:
        return image_to_ascii("CLI/assets/ascii_art.png", width=80, color=color)
    except FileNotFoundError:
        try:
            with open("CLI/assets/simple_ascii-art.txt", "r") as file:
                original_art = file.read()
                # Apply the specified color
                color_themes = {
                    'red': Colors.RED,
                    'green': Colors.GREEN,
                    'blue': Colors.BLUE,
                    'yellow': Colors.YELLOW,
                    'magenta': Colors.MAGENTA,
                    'cyan': Colors.CYAN,
                    'white': Colors.WHITE,
                    'bright_red': Colors.BRIGHT_RED,
                    'bright_green': Colors.BRIGHT_GREEN,
                    'bright_blue': Colors.BRIGHT_BLUE,
                    'bright_yellow': Colors.BRIGHT_YELLOW,
                    'bright_magenta': Colors.BRIGHT_MAGENTA,
                    'bright_cyan': Colors.BRIGHT_CYAN,
                    'bright_white': Colors.BRIGHT_WHITE,
                }
                
                if color == 'rainbow':
                    # For Textual rainbow effect, alternate colors per line
                    lines = original_art.split('\n')
                    rainbow_colors_textual = ["red", "yellow", "green", "cyan", "blue", "magenta"]
                    colored_lines = []
                    for i, line in enumerate(lines):
                        textual_color = rainbow_colors_textual[i % len(rainbow_colors_textual)]
                        colored_lines.append(f"[{textual_color}]{line}[/]")
                    return '\n'.join(colored_lines)
                elif color == 'fire':
                    lines = original_art.split('\n') 
                    fire_colors_textual = ["red", "orange", "yellow", "red"]
                    colored_lines = []
                    for i, line in enumerate(lines):
                        textual_color = fire_colors_textual[i % len(fire_colors_textual)]
                        colored_lines.append(f"[{textual_color}]{line}[/]")
                    return '\n'.join(colored_lines)
                elif color == 'ocean':
                    lines = original_art.split('\n')
                    ocean_colors_textual = ["blue", "bright_blue", "cyan", "bright_cyan"] 
                    colored_lines = []
                    for i, line in enumerate(lines):
                        textual_color = ocean_colors_textual[i % len(ocean_colors_textual)]
                        colored_lines.append(f"[{textual_color}]{line}[/]")
                    return '\n'.join(colored_lines)
                elif color in color_themes:
                    # Map to Textual color names
                    textual_color_map = {
                        'red': 'red', 'green': 'green', 'blue': 'blue', 'yellow': 'yellow',
                        'magenta': 'magenta', 'cyan': 'cyan', 'white': 'white',
                        'bright_red': 'bright_red', 'bright_green': 'bright_green', 
                        'bright_blue': 'bright_blue', 'bright_yellow': 'bright_yellow',
                        'bright_magenta': 'bright_magenta', 'bright_cyan': 'bright_cyan', 
                        'bright_white': 'bright_white',
                    }
                    textual_color = textual_color_map.get(color, 'white')
                    return f"[{textual_color}]{original_art}[/]"
                else:
                    return original_art  # Return original if color not found
        except FileNotFoundError:
            # Return fallback with color
            fallback_art = r"""
        ___            _ _       
        | _|__ _ _ __ (_) |_ ___ 
        | |/ _` | '_ \| | __/ _ \
        | | (_| | | | | | ||  __/
        |___\__, |_| |_|_|\__\___|
            |___/                
        """
            textual_color_map = {
                'red': 'red', 'green': 'green', 'blue': 'blue', 'yellow': 'yellow',
                'magenta': 'magenta', 'cyan': 'cyan', 'white': 'white',
                'bright_red': 'bright_red', 'bright_green': 'bright_green', 
                'bright_blue': 'bright_blue', 'bright_yellow': 'bright_yellow',
                'bright_magenta': 'bright_magenta', 'bright_cyan': 'bright_cyan', 
                'bright_white': 'bright_white',
            }
            if color in textual_color_map:
                textual_color = textual_color_map[color]
                return f"[{textual_color}]{fallback_art}[/]"
            elif color == 'rainbow':
                lines = fallback_art.split('\n')
                rainbow_colors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
                colored_lines = []
                for i, line in enumerate(lines):
                    textual_color = rainbow_colors[i % len(rainbow_colors)]
                    colored_lines.append(f"[{textual_color}]{line}[/]")
                return '\n'.join(colored_lines)
            elif color == 'fire':
                lines = fallback_art.split('\n')
                fire_colors = ["red", "orange", "yellow", "red"]
                colored_lines = []
                for i, line in enumerate(lines):
                    textual_color = fire_colors[i % len(fire_colors)]
                    colored_lines.append(f"[{textual_color}]{line}[/]")
                return '\n'.join(colored_lines)
            elif color == 'ocean':
                lines = fallback_art.split('\n')
                ocean_colors = ["blue", "bright_blue", "cyan", "bright_cyan"]
                colored_lines = []
                for i, line in enumerate(lines):
                    textual_color = ocean_colors[i % len(ocean_colors)]
                    colored_lines.append(f"[{textual_color}]{line}[/]")
                return '\n'.join(colored_lines)
            return fallback_art

class MenuItem(Static):
    """A menu item with icon and shortcut key."""
    
    class Clicked(Message):
        """Message sent when the menu item is clicked."""
        def __init__(self, action: str) -> None:
            self.action = action
            super().__init__()
    
    def __init__(self, icon: str, label: str, shortcut: str, action: str = None, **kwargs):
        super().__init__(**kwargs)
        self.icon = icon
        self.label = label
        self.shortcut = shortcut
        self.action = action or label.lower().replace(" ", "_")
    
    def render(self) -> str:
        main_content = f"[bright_white]{self.icon}[/] [white]{self.label}[/]"
        shortcut_part = f"[dim]{self.shortcut}[/]"
        # Add padding to create space between content and shortcut
        padding = " " * (41 - 1 - len(self.label))  # Adjust 40 to change spacing
        if self.label == 'Settings':
            padding = (" " * (40 - 1 - len(self.label)))+" " # Adjust 40 to change spacing
        return f"{main_content}{padding}{shortcut_part}"
    
    def on_click(self) -> None:
        """Send a message when the menu item is clicked."""
        self.post_message(self.Clicked(self.action))


class LoginScreen(Static):
    """The login screen with username/password inputs."""
    
    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                with Vertical():
                    # ASCII Art Logo
                    yield Static(SUCCESS_ASCII_ART, classes="ascii-art")
                    
                    # Login form
                    
                    with Vertical(classes="form-container"):
                        with Center():
                            yield Input(placeholder="Username", id="username-input", classes="login-input")
                            yield Input(placeholder="Password", password=True, id="password-input", classes="login-input")
                            
                            # Buttons container
                            with Horizontal(classes="button-container"):
                                yield Button("Login", id="login-btn", variant="primary", classes="auth-button")
                                yield Button("Register", id="register-btn", variant="primary", classes="auth-button")
                                
                    # Version info at bottom
                    yield Static("https://homebred-irredeemably-madie.ngrok-free.dev/test\nrolling-4b0a60e", classes="version-info")


class MainMenuScreen(Static):
    """The main menu screen after successful login."""
    
    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                with Vertical():
                    # ASCII Art Logo (green for successful login)
                    yield Static(SUCCESS_ASCII_ART, classes="ascii-art")

                    with Vertical(classes="main-content"):
                        with Center():
                            # Welcome message with username
                            yield Static("Welcome back!", id="welcome-msg", classes="welcome-back")
                            # Menu items
                            with Center(classes="menu-container"):
                                yield MenuItem("📁", "Rooms", "r", "rooms", classes="menu-item")
                                yield MenuItem("🕐", "Recent Rooms", "h", "recent_rooms", classes="menu-item") 
                                yield MenuItem("⚙️", "Settings", "s", "settings", classes="menu-item")
                                yield MenuItem("🚪", "Logout", "q", "logout", classes="menu-item")
    
    def on_menu_item_clicked(self, event: MenuItem.Clicked) -> None:
        """Handle menu item clicks."""
        try:
            # Get the splash screen via the app
            splash_screen = self.app.query_one(SplashScreen)
            
            if event.action == "rooms":
                # Get username from splash screen and switch to rooms
                username = getattr(splash_screen, 'username', 'User')
                splash_screen.switch_to_rooms(username)
            elif event.action == "recent_rooms":
                self.app.notify("Recent Rooms - Coming Soon!", severity="information")
            elif event.action == "settings":
                self.app.notify("Settings - Coming Soon!", severity="information")
            elif event.action == "logout":
                # Get the app and handle logout
                app = self.app
                if hasattr(app, '_handle_logout'):
                    app._handle_logout()
                else:
                    app.notify("Logging out...", severity="information")
        except Exception as e:
            self.app.notify(f"Navigation error: {str(e)}", severity="error")
        

class SplashScreen(Static):
    """The main splash screen container that manages login/main menu."""

    def __init__(self):
        super().__init__()
        self.current_screen = "login"  # "login" or "main"
        self.username = ""

    def compose(self) -> ComposeResult:
        # Start with login screen
        yield LoginScreen(id="login-screen")
        
        # Floating command line island (positioned outside the main flow)
        yield FloatingCommandLine(id="command-line", classes="floating-command-line hidden")
        
        # Floating result panel (positioned underneath the command line)
        yield FloatingResultPanel(id="result-panel", classes="floating-result-panel hidden")
        
        # Footer with quick commands
        yield Footer()
    
    def _create_room_content(self, username: str, api_client) -> Static:
        """Create room chat content as a widget."""
        # Create a container that holds all the room chat functionality
        room_widget = RoomChatWidget(username, api_client)
        return room_widget
    
    def switch_to_main_menu(self, username: str):
        """Switch to main menu from any screen."""
        self.username = username
        self.current_screen = "main"
        
        # Remove current content (login screen or room content)
        try:
            login_screen = self.query_one("#login-screen")
            login_screen.remove()
        except Exception:
            pass
        
        try:
            room_content = self.query_one("#room-content")
            room_content.remove()
        except Exception:
            pass
        
        # Add main menu if not already present
        try:
            self.query_one("#main-screen")
        except Exception:
            main_menu = MainMenuScreen()
            main_menu.id = "main-screen"
            self.mount(main_menu, before="#command-line")
    
    def switch_to_login(self):
        """Switch from main menu back to login screen."""
        self.current_screen = "login"
        self.username = ""

        # Remove main screen and add login screen
        try:
            main_screen = self.query_one("#main-screen")
            main_screen.remove()
        except:
            pass
        
        login_screen = LoginScreen()
        login_screen.id = "login-screen"
        self.mount(login_screen, before="#command-line")
        
    def switch_to_rooms(self, username: str):
        """Switch to room chat interface."""
        try:
            self.current_screen = "rooms"
            self.username = username
            
            # Remove main menu and add room content to this screen instead of pushing new screen
            try:
                main_screen = self.query_one("#main-screen")
                main_screen.remove()
            except Exception as e:
                # Screen might not exist yet, that's okay
                pass
            
            # Get reference to parent app to pass client
            app = self.app
            api_client = getattr(app, 'client', None)
            
            # Create room content as a widget and mount it to this screen
            room_content = self._create_room_content(username, api_client)
            room_content.id = "room-content"
            self.mount(room_content, before="#command-line")
            
        except Exception as e:
            self.app.notify(f"Error switching to rooms: {str(e)}", severity="error")


# Room management constants and classes
ROOMS_FILE = "rooms_data.json"

def load_rooms_data():
    """Load room data from JSON file."""
    if os.path.exists(ROOMS_FILE):
        try:
            with open(ROOMS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_rooms_data(rooms_data):
    """Save room data to JSON file."""
    with open(ROOMS_FILE, 'w') as f:
        json.dump(rooms_data, f, indent=4)


class CreateRoomModal(ModalScreen):
    """Modal screen for creating new rooms."""
    
    def compose(self) -> ComposeResult:
        yield Center(
            Vertical(
                Static("Create New Room", classes="modal-title"),
                Input(placeholder="Room Name", id="room-name-input", classes="modal-input"),
                Horizontal(
                    Button("Public", variant="primary", id="public-btn", classes="modal-button"),
                    Button("Private", variant="default", id="private-btn", classes="modal-button"),
                    Button("Cancel", id="cancel-btn", classes="modal-button"),
                    classes="modal-buttons"
                ),
                classes="modal-container"
            ),
            classes="modal-center"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-btn":
            self.dismiss()
        elif event.button.id in ["public-btn", "private-btn"]:
            room_name = self.query_one("#room-name-input").value.strip()
            if room_name:
                is_public = event.button.id == "public-btn"
                self.dismiss((room_name, is_public))


class ClickableRoom(Static):
    """A clickable room label that can be selected."""
    
    class Clicked(Message):
        """Message sent when the room is clicked."""
        def __init__(self, room_name: str) -> None:
            self.room_name = room_name
            super().__init__()
    
    def __init__(self, room_name: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.room_name = room_name
    
    def on_click(self) -> None:
        """Send a message when the room is clicked."""
        self.post_message(self.Clicked(self.room_name))


class RoomChatWidget(Static):
    """Main room chat interface integrated into the TUI."""
    
    BINDINGS = [
        ("m", "focus_message_box", "Focus Message Box"),
        ("up", "previous_room", "Previous Room"),
        ("down", "next_room", "Next Room"),
        ("escape", "unfocus_input", "Unfocus Input"),
        ("ctrl+h", "back_to_home", "Back to Home"),
    ]
    
    def __init__(self, username: str, api_client):
        super().__init__()
        self.api_client = api_client
        self.username = username
        self.roomBar = None
        self.room_list = []
        self.usersBar = None
        self.main_content = None
        self.chat_input = None
        self.room_counter = 0
        
        # Load rooms from JSON or create defaults
        self.rooms = load_rooms_data()
        if not self.rooms:
            self.rooms = {
                "General": {"users": [username], "messages": []},
                "Random": {"users": [], "messages": []},
                "Help": {"users": [], "messages": []}
            }
            save_rooms_data(self.rooms)

        # Ensure user is in General room
        if username not in self.rooms["General"]["users"]:
            self.rooms["General"]["users"].append(username)
            save_rooms_data(self.rooms)

        self.current_room = "General"
        self.users = self.rooms[self.current_room]["users"]

    def compose(self) -> ComposeResult:
        """Create the room chat interface layout."""
        try:
            # Room bar (left sidebar) - Create empty, will be populated in on_mount
            self.roomBar = Vertical(id="roomBar", classes="room-sidebar")
            
            # Main chat area - Create empty, will be populated in on_mount
            self.main_content = Vertical(id="main-chat", classes="chat-main")
            
            self.chat_input = Input(
                placeholder=f"Message #{self.current_room}...", 
                id="chat_input", 
                classes="chat-input"
            )
            
            # Users bar (right sidebar) - Create empty, will be populated in on_mount
            self.usersBar = Vertical(id="usersBar", classes="users-sidebar")

            # Create layout
            layout = Horizontal(
                self.roomBar,
                Vertical(
                    self.main_content,
                    self.chat_input,
                    classes="chat-column"
                ),
                self.usersBar,
                classes="room-container"
            )
            
            yield layout
            
        except Exception as e:
            self.app.notify(f"Error composing room chat layout: {str(e)}", severity="error")
            yield Static(f"Error loading chat interface: {str(e)}", classes="error-message")

    def on_mount(self) -> None:
        """Initialize the room interface."""
        try:
            # Call methods directly to populate the interface
            self._refresh_room_list()
            self._refresh_user_list()
            self._load_room_messages()
        except Exception as e:
            self.app.notify(f"Error initializing rooms: {str(e)}", severity="error")

    def _refresh_room_list(self) -> None:
        """Update the room bar with current rooms."""
        self.roomBar.remove_children()
        
        # Add header with navigation hint
        self.roomBar.mount(Static("󰋜 Rooms", classes="sidebar-header"))
        self.roomBar.mount(Static("ESC: Unfocus | ^H: Home", classes="nav-hint"))
        
        self.room_list = sorted(self.rooms.keys())
        
        # Add each room
        for room_name in self.room_list:
            is_current = room_name == self.current_room
            icon = "󰭷" if is_current else "󰋜"
            unread = len(self.rooms[room_name]["messages"])
            unread_badge = f" ({unread})" if unread > 0 else ""
            
            style = "room-current" if is_current else "room-item"
            self.room_counter += 1
            safe_room_name = room_name.lower().replace(" ", "_")
            room_id = f"room-{safe_room_name}-{self.room_counter}"
            
            room_text = f"{icon} {room_name}{unread_badge}"
            clickable_room = ClickableRoom(
                room_name,
                room_text,
                id=room_id,
                classes=style
            )
            self.roomBar.mount(clickable_room)
        
        # Add New Room button
        new_room_button = ClickableRoom(
            "new_room",
            "󰐕 New Room",
            classes="room-action"
        )
        self.roomBar.mount(new_room_button)

    def _refresh_user_list(self) -> None:
        """Update the users bar with current users."""
        self.usersBar.remove_children()
        
        # Add header
        self.usersBar.mount(Static(f"󰀄 Users ({len(self.users)})", classes="sidebar-header"))
        
        # Add each user
        for idx, user in enumerate(sorted(self.users)):
            is_self = user == self.username
            icon = "󰋗" if is_self else "󰀄"
            style = "user-self" if is_self else "user-item"
            safe_user = user.lower().replace(" ", "_")
            safe_room = self.current_room.lower().replace(" ", "_")
            user_id = f"user-{safe_room}-{safe_user}"
            self.usersBar.mount(Static(f"{icon} {user}", id=user_id, classes=style))

    def _load_room_messages(self) -> None:
        """Load and display messages for the current room."""
        self.main_content.remove_children()
        messages = self.rooms[self.current_room]["messages"]
        recent_messages = messages[-40:] if len(messages) > 40 else messages
        
        if not recent_messages:
            # Add welcome message if no messages
            self.main_content.mount(Static(f"Welcome to #{self.current_room}!", classes="welcome-message"))
            self.main_content.mount(Static("No messages yet. Start the conversation!", classes="info-message"))
        else:
            for msg in recent_messages:
                # Format message based on whether it's from current user
                if ": " in msg:
                    username, message_text = msg.split(": ", 1)
                    is_self = username == self.username
                    
                    if is_self:
                        # Current user's messages on the right - wrap in container
                        formatted_msg = f"{message_text}"
                        message_widget = Static(formatted_msg, classes="chat-bubble-self", markup=True)
                        container = Horizontal(message_widget, classes="message-container-self")
                        self.main_content.mount(container)
                    else:
                        # Other users' messages on the left
                        formatted_msg = f"[bold #89b4fa]{username}[/bold #89b4fa]: {message_text}"
                        message_widget = Static(formatted_msg, classes="chat-bubble-other", markup=True)
                        container = Horizontal(message_widget, classes="message-container-other")
                        self.main_content.mount(container)
                else:
                    formatted_msg = msg
                    self.main_content.mount(Static(formatted_msg, classes="chat-message", markup=True))

    def switch_room(self, room_name: str) -> None:
        """Switch to a different room."""
        if room_name in self.rooms and room_name != self.current_room:
            # Store current room's users
            self.rooms[self.current_room]["users"] = self.users
            
            # Switch rooms
            self.current_room = room_name
            self.users = self.rooms[room_name]["users"]
            
            # Update displays
            self._load_room_messages()
            self._refresh_user_list()
            self._refresh_room_list()
            
            # Update input placeholder
            self.chat_input.placeholder = f"Message #{room_name}..."

    def on_clickable_room_clicked(self, event: ClickableRoom.Clicked) -> None:
        """Handle room clicks."""
        if event.room_name == "new_room":
            self.app.push_screen(CreateRoomModal(), callback=self.handle_room_creation)
        else:
            self.switch_room(event.room_name)
            
    def handle_room_creation(self, result) -> None:
        """Handle room creation result."""
        if result is not None:
            room_name, is_public = result
            if room_name not in self.rooms:
                # Try to create room on server
                try:
                    if self.api_client and self.api_client.is_authenticated():
                        # Create room on server
                        response = self.api_client.create_room(room_name, private=not is_public)
                        self.app.notify(f"Room '{room_name}' created on server", severity="success")
                except Exception as e:
                    self.app.notify(f"Room created locally (server unavailable)", severity="warning")
                
                # Create room locally
                self.rooms[room_name] = {
                    "users": [self.username],
                    "messages": [],
                    "is_public": is_public
                }
                save_rooms_data(self.rooms)
                self._refresh_room_list()
                # Show success message
                self.main_content.mount(
                    Static(f"→ Room #{room_name} created ({'public' if is_public else 'private'})", 
                          classes="system-message")
                )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle message input."""
        if event.input.id == "chat_input":
            message_text = event.value.strip()
            if not message_text:
                return

            # Try to send message via API if authenticated, fallback to local storage
            try:
                if self.api_client and self.api_client.is_authenticated():
                    # Send message to server
                    response = self.api_client.send_message(self.current_room, message_text)
                    message = f"{self.username}: {message_text}"
                else:
                    # Fallback to local mode
                    message = f"{self.username}: {message_text}"
            except Exception as e:
                # If API fails, fall back to local mode
                message = f"{self.username}: {message_text}"
                self.app.notify(f"Message sent locally (server unavailable)", severity="warning")
            
            self.rooms[self.current_room]["messages"].append(message)
            save_rooms_data(self.rooms)
            
            # Refresh messages display
            self._load_room_messages()
            
            # Clear input
            event.input.value = ""
            
            # Refresh room list to update unread counts
            self._refresh_room_list()

    def action_focus_message_box(self) -> None:
        """Focus the message input."""
        self.chat_input.focus()

    def action_previous_room(self) -> None:
        """Navigate to previous room."""
        if self.room_list:
            current_index = self.room_list.index(self.current_room)
            new_index = (current_index - 1) % len(self.room_list)
            self.switch_room(self.room_list[new_index])

    def action_next_room(self) -> None:
        """Navigate to next room."""
        if self.room_list:
            current_index = self.room_list.index(self.current_room)
            new_index = (current_index + 1) % len(self.room_list)
            self.switch_room(self.room_list[new_index])

    def action_unfocus_input(self) -> None:
        """Unfocus the message input."""
        try:
            # Check if the input is focused and unfocus it
            if self.chat_input.has_focus:
                self.chat_input.blur()
            else:
                # If nothing is focused, focus the input for convenience
                self.chat_input.focus()
        except Exception:
            # Fallback - just blur any focused widget
            self.screen.set_focus(None)

    def action_back_to_home(self) -> None:
        """Return to main menu."""
        self._navigate_to_main_menu()
        
    def on_key(self, event) -> None:
        """Handle key events for room screen, including command line activation."""
        try:
            # Pass key events to the app's keyboard handler if it exists
            if hasattr(self.app, 'keyboard_handler'):
                handled = self.app.keyboard_handler.handle_key_event(event.key)
                if handled:
                    event.prevent_default()
        except Exception as e:
            # If keyboard handler fails, continue with normal key processing
            pass
    
    def _navigate_to_main_menu(self) -> None:
        """Helper method to navigate back to main menu."""
        try:
            # Get the main splash screen and switch back to main menu
            splash_screen = self.app.screen
            splash_screen.switch_to_main_menu(self.username)
        except Exception as e:
            # Fallback - send notification
            self.app.notify(f"Navigation error: {str(e)}", severity="error")
            self.app.notify("Use ':back' command or logout to return", severity="information")


class AeroStream(App):
    """LunarVim-style TUI application."""
    
    # Define bindings at the App level so Footer can display them
    # Dummy action methods prevent double execution while KeyboardHandler handles actual functionality
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
        Binding(
            key="question_mark",
            action="help",
            description="Show help screen",
            key_display="?",
        ),
        Binding(key="r", action="rooms", description="Rooms", show=False),
        Binding(key="h", action="recent", description="Recent", show=False),
        Binding(key="s", action="settings", description="Settings", show=False),
        Binding(key="l", action="login", description="Login"),
        Binding(key="r", action="register", description="Register"),
        Binding(key="p", action="rooms", description="Rooms"),
        Binding(key="t", action="recent", description="Recent Rooms"),
        Binding(key="c", action="settings", description="Settings"),
        Binding(key="colon", action="command_mode", description="Command mode"),
        Binding(key="escape", action="escape_mode", description="Exit command mode"),
        Binding(key="ctrl+h", action="home", description="Home"),
    ]
    
    CSS = """
    Screen {
        background: #1e1e2e;
        color: white;
        layers: base overlay;
    }
    
    SplashScreen {
        height: 100%;
        width: 100%;
        layer: base;
    }
    
    /* Login Screen Styles */
    .login-container {
        align: center middle;
        width: 100%;
        height: 100%;
        text-align: center;
    }
    
    .form-container {
        text-align: center;
        align: center middle;
        width: 100%;
        height: auto;
        padding: 2;
    }
    
    .welcome-text {
        color: #b4befe;
        text-align: center;
        margin: 1 0 2 0;
        text-style: bold;
    }
    
    .login-input {
        margin: 1 2;
        
        width: 80%;
        background: #45475a;
        color: #cdd6f4;
        border: solid #6c7086;
    }
    
    .login-input:focus {
        border: solid #89b4fa;
        background: #313244;
    }
    
    .button-container {
        align: center middle;
        margin: 2 0 1 0;
        width: 80%;
        height: auto;
    }
    
    .auth-button {
        align: center middle;
        text-align: center;
        margin: 1 2;
        width: 20;
        height: 1;
        color: #cdd6f4;
    }
    
    Button.auth-button.-primary {
        background: #89b4fa;
        color: #1e1e2e;
        border: none;
    }
    
    Button.auth-button.-primary:hover {
        background: #b4befe;
    }
    
    Button.auth-button.-default {
        background: #45475a;
        color: #cdd6f4;
        border: solid #6c7086;
    }
    
    Button.auth-button.-default:hover {
        background: #585b70;
        border: solid #89b4fa;
    }
    
    /* Main Menu Styles */
    .main-container {
        align: center middle;
        width: 100vw;
        height: 100vh;
        text-align: center;
    }
    
    .ascii-art {
        color: #b4befe;
        text-align: center;
        width: 100%;
        height: auto;
        align-horizontal: center;
    }
    
    .ascii-art-small {
        color: #b4befe;
        margin-top: -6;
        text-align: center;
        width: auto;
        height: auto;
        align-horizontal: center;
    }

    .main-content {
        align: center middle;
        width: 100%;
        height: auto;
        padding: 2;
    }

    .welcome-back {
        align: center middle;
        color: #a6e3a1;
        text-align: center;
        text-style: bold;
    }
    
    .menu-container {
        align: center middle;
        width: 100vw;
        height: auto;
        padding: 2;
        
    }
    
    .menu-item {
        align: center middle;
        width: 50;
        height: auto;
        padding: 1;
        margin-left: -2;
    }
    
    .menu-item:hover {
        background: #45475a;
        color: #89b4fa;
    }
    
    .logout-item {
        color: #f38ba8;
        border-top: solid #45475a;
        margin-top: 2;
        padding-top: 2;
    }
    
    .logout-item:hover {
        background: #45475a;
        color: #f38ba8;
    }
    
    .version-info {
        color: #fab387;
        text-align: center;
        margin-top: 2;
        margin-left: 0;
    }
    
    /* Floating Command Line Island Styles */
    .floating-command-line {
        layer: overlay;
        offset: 75% 15;
        width: 70;
        height: 5;
        background: #1e1e2e;
        border: thick #fab387;
        text-align: left;
        padding: 1 2;
        color: #f9e2af;
        opacity: 0.95;
    }
    
    .floating-command-line.active {
        background: #313244;
        border: thick #89b4fa;
        color: #cdd6f4;
        opacity: 1.0;
    }
    
    .floating-command-line.hidden {
        display: none;
    }
    
    .floating-command-line.inactive {
        visibility: hidden;
    }
    
    /* Floating Result Panel Styles */
    .floating-result-panel {
        layer: overlay;
        offset: 75% 15;
        width: 70;
        height: auto;
        min-height: 3;
        max-height: 15;
        background: #1e1e2e;
        border: thick #6c7086;
        text-align: left;
        padding: 1 2;
        color: #cdd6f4;
        opacity: 0.95;
        overflow: auto;
    }
    
    .floating-result-panel.result-info {
        border: thick #89b4fa;
        color: #cdd6f4;
    }
    
    .floating-result-panel.result-success {
        border: thick #a6e3a1;
        color: #a6e3a1;
    }
    
    .floating-result-panel.result-error {
        border: thick #f38ba8;
        color: #f38ba8;
    }
    
    .floating-result-panel.hidden {
        display: none;
    }
    
    /* Room Chat Interface Styles */
    .room-container {
        height: 100%;
        width: 100%;
        background: #1e1e2e;
        layer: below;
    }
    
    #room-content {
        height: 100%;
        width: 100%;
    }
    
    .room-sidebar {
        width: 25;
        height: 100%;
        background: #181825;
        border-right: solid #45475a;
        padding: 1;
    }
    
    .users-sidebar {
        width: 20;
        height: 100%;
        background: #181825;
        border-left: solid #45475a;
        padding: 1;
    }
    
    .chat-column {
        height: 100%;
        background: #1e1e2e;
    }
    
    .chat-main {
        height: 1fr;
        background: #1e1e2e;
        padding: 1;
        overflow-y: auto;
        scrollbar-background: #313244;
        scrollbar-color: #6c7086;
        scrollbar-color-hover: #89b4fa;
        scrollbar-color-active: #a6e3a1;
        scrollbar-size: 1 1;
    }
    
    .chat-input {
        height: 3;
        background: #313244;
        color: #cdd6f4;
        border: solid #6c7086;
        margin: 0 1 1 1;
    }
    
    .chat-input:focus {
        border: solid #89b4fa;
        background: #45475a;
    }
    
    .sidebar-header {
        color: #1e1e2e;
        text-style: bold;
        background: #89b4fa;
        padding: 1;
        margin-bottom: 1;
        text-align: center;
        height: 3;
    }
    
    .nav-hint {
        color: #6c7086;
        text-style: italic;
        text-align: center;
        margin-bottom: 1;
        padding: 0 1;
    }
    
    .room-item {
        padding: 1;
        margin-bottom: 1;
        color: #cdd6f4;
        background: #313244;
        border-left: solid #6c7086;
        height: 3;
    }
    
    .room-item:hover {
        background: #45475a;
        color: #89b4fa;
        border-left: solid #89b4fa;
    }
    
    .room-current {
        padding: 0 1;
        margin-bottom: 0;
        color: #1e1e2e;
        background: #89b4fa;
        text-style: bold;
    }
    
    .room-action {
        padding: 0 1;
        margin-top: 1;
        color: #a6e3a1;
        background: transparent;
        border-top: solid #45475a;
        padding-top: 1;
    }
    
    .room-action:hover {
        background: #45475a;
        color: #a6e3a1;
    }
    
    .user-item {
        padding: 1;
        margin-bottom: 1;
        color: #cdd6f4;
        background: #313244;
        border-left: solid #6c7086;
        height: 3;
    }
    
    .user-self {
        padding: 1;
        margin-bottom: 1;
        color: #a6e3a1;
        background: #45475a;
        border-left: solid #a6e3a1;
        text-style: bold;
        height: 3;
    }
    
    .chat-message {
        margin-bottom: 1;
        padding: 1 2;
        color: #cdd6f4;
        background: #313244;
        border-left: solid #89b4fa;
        text-style: none;
        height: auto;
        min-height: 2;
    }
    
    .message-container-other {
        width: 100%;
        height: auto;
        margin-bottom: 0;
        padding-bottom: 1;
        align: left middle;
    }
    
    .message-container-self {
        width: 100%;
        height: auto;
        margin-bottom: 0;
        padding-bottom: 1;
        align: right middle;
    }
    
    .chat-bubble-other {
        padding: 1;
        color: #cdd6f4;
        background: #313244;
        border-left: solid #89b4fa;
        text-style: none;
        height: auto;
        min-height: 1;
        width: 45;
        max-width: 45;
    }
    
    .chat-bubble-self {
        padding: 1;
        color: #cdd6f4;
        background: #45475a;
        border-right: solid #a6e3a1;
        text-style: none;
        height: auto;
        min-height: 1;
        width: 45;
        max-width: 45;
    }
    
    .system-message {
        margin-bottom: 0;
        padding: 0 1;
        color: #f9e2af;
        background: transparent;
        text-style: italic;
    }
    
    /* Modal Styles for Room Creation */
    .modal-center {
        align: center middle;
        width: 100%;
        height: 100%;
    }
    
    .modal-container {
        background: #1e1e2e;
        border: solid #89b4fa;
        border-title-color: #b4befe;
        padding: 2;
        width: 60;
        height: auto;
        align: center middle;
    }
    
    .modal-title {
        color: #b4befe;
        text-align: center;
        text-style: bold;
        margin-bottom: 2;
    }
    
    .modal-input {
        background: #313244;
        color: #cdd6f4;
        border: solid #6c7086;
        margin-bottom: 2;
        width: 100%;
    }
    
    .modal-input:focus {
        border: solid #89b4fa;
        background: #45475a;
    }
    
    .modal-buttons {
        align: center middle;
        width: 100%;
        height: auto;
    }
    
    .modal-button {
        margin: 0 1;
        width: 12;
        height: 1;
    }
    
    .info-message {
        padding: 1 2;
        margin: 1 0;
        color: #89b4fa;
        background: #181825;
        text-style: italic;
        text-align: center;
        border: solid #45475a;
    }
    
    .welcome-message {
        padding: 1 2;
        margin: 1 0;
        color: #a6e3a1;
        background: #181825;
        text-style: bold;
        text-align: center;
        border: solid #45475a;
    }
    """

    # KEYBOARD SHORTCUTS INTEGRATION --- DO NOT TOUCH ---
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = IgniteAPIClient()  # Each app instance gets its own client
        self.keyboard_handler = KeyboardHandler(self)
        self._setup_keyboard_callbacks()
        self._register_custom_commands()
        self.splash_screen = None
        self.is_authenticated = False
        self.command_line_should_stay_visible = False  # Track if command line should stay visible after command execution
    
    def _setup_keyboard_callbacks(self):
        """Set up callbacks for keyboard handler events."""
        self.keyboard_handler.on_mode_change = self._on_mode_change
        self.keyboard_handler.on_command_buffer_change = self._on_command_buffer_change
        self.keyboard_handler.on_command_executed = self._on_command_executed
        self.keyboard_handler.on_error = self._on_error
    
    def _connect_floating_panels(self):
        """Connect the floating command line with its result panel."""
        try:
            command_line = self.query_one("#command-line", FloatingCommandLine)
            result_panel = self.query_one("#result-panel", FloatingResultPanel)
            command_line.set_result_panel(result_panel)
        except Exception:
            # Widgets not ready yet, schedule for later
            self.call_later(self._connect_floating_panels)
    
    def _register_custom_commands(self):
        """Register application-specific commands."""
        # Authentication commands
        self.keyboard_handler.register_command("login", self._login_command, "Login to your account", ["l"])
        self.keyboard_handler.register_command("register", self._register_command, "Register a new account", ["reg"])
        self.keyboard_handler.register_command("logout", self._logout_command, "Logout from your account", ["exit"])
        
        # Menu navigation commands (with colon command support)
        self.keyboard_handler.register_command("rooms", self._rooms_command, "Go to rooms screen", ["r", "room"])
        self.keyboard_handler.register_command("recent", self._recent_command, "Go to recent rooms screen", ["h", "history"])
        self.keyboard_handler.register_command("settings", self._settings_command, "Go to settings screen", ["s", "config", "preferences"])
        
        # Room management commands with parameter support
        self.keyboard_handler.register_command(
            "join", self._join_command, 
            "Join a room with optional parameters", 
            ["j"],
            {"r": "room name to join", "p": "password for the room"}
        )
        self.keyboard_handler.register_command(
            "create", self._create_command, 
            "Create a new room with optional parameters", 
            ["new"],
            {"r": "room name to create", "p": "password for the room"}
        )
        
        # Additional Vim-style commands
        self.keyboard_handler.register_command("version", self._version_command, "Show application version", ["v", "ver"])
        self.keyboard_handler.register_command("status", self._status_command, "Show current status", ["st", "info"])
        self.keyboard_handler.register_command("refresh", self._refresh_command, "Refresh the interface", ["ref", "reload"])
        self.keyboard_handler.register_command("theme", self._theme_command, "Toggle theme", ["th"])
        self.keyboard_handler.register_command("connect", self._connect_command, "Connect to server", ["conn"])
        self.keyboard_handler.register_command("disconnect", self._disconnect_command, "Disconnect from server", ["disconn", "dc"])
        
        # Navigation commands
        self.keyboard_handler.register_command("home", self._home_command, "Go to home screen", ["start"])
        self.keyboard_handler.register_command("back", self._back_command, "Go back", ["b"])
        self.keyboard_handler.register_command("next", self._next_command, "Go to next item", ["n"])
        self.keyboard_handler.register_command("previous", self._previous_command, "Go to previous item", ["prev"])
        
        # Utility commands
        self.keyboard_handler.register_command("debug", self._debug_command, "Toggle debug mode", ["d"])
        self.keyboard_handler.register_command("log", self._log_command, "Show logs", ["logs"])
        self.keyboard_handler.register_command("save", self._save_command, "Save current state", ["w", "write"])
        
        # Override the default help command with our custom one
        self.keyboard_handler.register_command("help", self._custom_help_command, "Show help for commands and keys", ["h"])
        
        # Re-register single-key commands since Textual bindings are disabled (show=False)
        # These will now be handled exclusively by KeyboardHandler
        self.keyboard_handler.register_single_key("l", self._login_command)
        self.keyboard_handler.register_single_key("r", self._register_command)
        self.keyboard_handler.register_single_key("p", self._rooms_command)
        self.keyboard_handler.register_single_key("t", self._recent_command)
        self.keyboard_handler.register_single_key("c", self._settings_command)
        self.keyboard_handler.register_single_key("r", self._rooms_command)
        self.keyboard_handler.register_single_key("h", self._recent_command)
        self.keyboard_handler.register_single_key("s", self._settings_command)
        
        # Register back command for navigation
        self.keyboard_handler.register_command("back", self._back_command, "Go back to main menu", ["b", "menu"])
        
        # Note: q and ? are still handled by Textual's binding system
        # : (colon) is handled by KeyboardHandler in the on_key method
    
    def _on_mode_change(self, mode: KeyboardMode):
        """Handle keyboard mode changes."""
        try:
            command_line = self.query_one("#command-line", FloatingCommandLine)
            # Keep command line visible if it should stay visible or if in command mode
            should_be_active = (mode == KeyboardMode.COMMAND) or self.command_line_should_stay_visible
            command_line.set_active(should_be_active)
        except Exception as e:
            # Command line widget not available yet, schedule for next tick
            self.call_later(self._delayed_mode_change, mode)
    
    def _delayed_mode_change(self, mode: KeyboardMode):
        """Handle delayed mode changes when widget isn't ready."""
        try:
            command_line = self.query_one("#command-line", FloatingCommandLine)
            # Keep command line visible if it should stay visible or if in command mode
            should_be_active = (mode == KeyboardMode.COMMAND) or self.command_line_should_stay_visible
            command_line.set_active(should_be_active)
        except Exception:
            # Still not ready, ignore silently
            pass
    
    def _on_command_buffer_change(self, buffer: str):
        """Handle command buffer changes."""
        try:
            command_line = self.query_one("#command-line", FloatingCommandLine)
            command_line.update_buffer(buffer)
        except Exception as e:
            # Widget not available, schedule for later
            self.call_later(self._delayed_buffer_change, buffer)
    
    def _delayed_buffer_change(self, buffer: str):
        """Handle delayed buffer changes."""
        try:
            command_line = self.query_one("#command-line", FloatingCommandLine)
            command_line.update_buffer(buffer)
        except Exception:
            # Still not ready, ignore silently
            pass
    
    def _on_command_executed(self, command: str, result):
        """Handle command execution."""
        # Always hide the command line after command execution
        self.command_line_should_stay_visible = False
        
        try:
            command_line = self.query_one("#command-line", FloatingCommandLine)
            
            # Show result if there's a meaningful return value
            if result and isinstance(result, str):
                command_line.show_result(result, "success")
            
            # Always hide the command line after execution
            command_line.set_active(False)
        except Exception:
            # Fallback to notify if panels aren't ready and there's a result to show
            if result and isinstance(result, str):
                self.notify(result)
    
    def _on_error(self, error: str):
        """Handle errors from keyboard handler."""
        # Set flag to keep command line visible after error
        self.command_line_should_stay_visible = True
        
        try:
            command_line = self.query_one("#command-line", FloatingCommandLine)
            command_line.show_result(error, "error")
            
            # Ensure command line stays active after showing error
            command_line.set_active(True)
        except Exception:
            # Fallback to notify if panels aren't ready
            self.notify(error, severity="error")
    
    # Command handlers
    def _login_command(self, args=None):
        """Handle login command."""
        if not self.is_authenticated:
            self._handle_login()
        else:
            self.notify("Already logged in")
    
    def _register_command(self, args=None):
        """Handle register command."""
        if not self.is_authenticated:
            self._handle_register()
        else:
            self.notify("Please logout first to register a new account")
    
    def _logout_command(self, args=None):
        """Handle logout command."""
        if self.is_authenticated:
            self._handle_logout()
        else:
            self.notify("Not currently logged in")
    
    def _rooms_command(self, args=None):
        """Handle rooms command."""
        if self.is_authenticated:
            # Navigate to rooms if we're in the main menu
            try:
                splash_screen = self.query_one(SplashScreen)
                username = getattr(splash_screen, 'username', 'User')
                splash_screen.switch_to_rooms(username)
                return "Entering chat rooms..."
            except Exception as e:
                return f"Rooms interface error: {str(e)}"
        else:
            return "Please login first"
    
    def _recent_command(self, args=None):
        """Handle recent rooms command."""
        if self.is_authenticated:
            self.notify("Selected: Recent Rooms")
        else:
            self.notify("Please login first")
    
    def _settings_command(self, args=None):
        """Handle settings command."""
        if self.is_authenticated:
            self.notify("Selected: Settings")
        else:
            self.notify("Please login first")
    
    # TODO: Update to variable version function
    def _version_command(self, args=None):
        """Handle version command."""
        return "Ignite TUI v1.0.0 - rolling-4b0a60e"
    
    def _status_command(self, args=None):
        """Handle status command."""
        mode = "Command Mode" if self.keyboard_handler.is_in_command_mode() else "Normal Mode"
        return f"Status: {mode} | Server: Disconnected | Theme: Dark"
    
    def _refresh_command(self, args=None):
        """Handle refresh command."""
        self.refresh()
        return "Interface refreshed"
    
    def _theme_command(self, args=None):
        """Handle theme command."""
        return "Theme toggle not yet implemented"
    
    def _connect_command(self, args=None):
        """Handle connect command."""
        return "Connecting to server..."
    
    def _disconnect_command(self, args=None):
        """Handle disconnect command."""
        return "Disconnected from server"
    
    def _home_command(self, args=None):
        """Handle home command - return to main menu."""
        if self.is_authenticated:
            try:
                splash_screen = self.query_one(SplashScreen)
                username = getattr(splash_screen, 'username', 'User')
                splash_screen.switch_to_main_menu(username)
                return "Returned to home"
            except Exception as e:
                return f"Navigation Error: {str(e)}"
        else:
            return "Please login first"
    
    def _back_command(self, args=None):
        """Handle back command."""
        if self.is_authenticated:
            try:
                # Check if we're in a room screen and go back to main menu
                splash_screen = self.query_one(SplashScreen)
                if hasattr(splash_screen, 'current_screen') and splash_screen.current_screen == "rooms":
                    username = getattr(splash_screen, 'username', 'User')
                    splash_screen.switch_to_main_menu(username)
                    return "Returned to main menu"
                else:
                    return "Already at main menu"
            except:
                return "Navigation not available"
        else:
            return "Please login first"
    
    def _next_command(self, args=None):
        """Handle next command."""
        return "Moving to next item"
    
    def _previous_command(self, args=None):
        """Handle previous command."""
        return "Moving to previous item"
    
    def _debug_command(self, args=None):
        """Handle debug command."""
        return "Debug mode toggled"
    
    def _log_command(self, args=None):
        """Handle log command."""
        return "Log viewer not yet implemented"
    
    def _save_command(self, args=None):
        """Handle save command."""
        return "State saved"
    
    def _custom_help_command(self, args=None):
        """Handle custom help command with both single-key and colon commands."""
        help_text = """
Colon Commands (press : then type):
    :help, :h         - Show this help
    :login, :l        - Go to login
    :register, :r     - Go to register
    :rooms, :p        - Go to rooms
    :recent, :t       - Recent rooms
    :settings, :config - Settings
    :join, :j -r <room> -p <pass> - Join a room
    :create, :new -r <room> -p <pass> - Create a room
    :version, :v      - Show version
    :status, :st      - Show status
    :refresh, :reload - Refresh interface
"""
        return help_text.strip()
    
    def _join_command(self, args: CommandArgs):
        """Handle join room command with parameters."""
        if not self.is_authenticated:
            return "Please login first to join a room"
        
        if not args or not args.flags:
            return "Usage: :join -r <room_name> [-p <password>]\nExample: :join -r lobby -p secret123"
        
        room_name = args.flags.get('r')
        password = args.flags.get('p', '')
        
        if not room_name:
            return "Room name is required. Use -r flag to specify room name"
        
        # Simulate joining a room
        if password:
            return f"Joining room '{room_name}' with password..."
        else:
            return f"Joining room '{room_name}' (no password)..."
    
    def _create_command(self, args: CommandArgs):
        """Handle create room command with parameters."""
        if not self.is_authenticated:
            return "Please login first to create a room"
        
        if not args or not args.flags:
            return "Usage: :create -r <room_name> [-p <password>]\nExample: :create -r myroom -p secret123"
        
        room_name = args.flags.get('r')
        password = args.flags.get('p', '')
        
        if not room_name:
            return "Room name is required. Use -r flag to specify room name"
        
        # Simulate creating a room
        if password:
            return f"Creating password-protected room '{room_name}'..."
        else:
            return f"Creating public room '{room_name}'..."
    
    def compose(self) -> ComposeResult:
        self.splash_screen = SplashScreen()
        yield self.splash_screen
        # Connect the floating panels after composition
        self.call_after_refresh(self._connect_floating_panels)

    
    # Action methods for Textual bindings (dummy methods to prevent double execution)
    def action_help(self) -> None:
        """Handle help action from ? key."""
        result = self._custom_help_command()
        if result:
            try:
                command_line = self.query_one("#command-line", FloatingCommandLine)
                command_line.show_result(result, "info")
            except Exception:
                self.notify(result)
    
    def action_escape_mode(self) -> None:
        """Handle escape key to exit command mode."""
        if hasattr(self, 'keyboard_handler'):
            self.keyboard_handler.handle_key("escape")
    
    def action_login(self) -> None:
        """Dummy action - KeyboardHandler handles this."""
        pass
    
    def action_register(self) -> None:
        """Dummy action - KeyboardHandler handles this."""
        pass
    
    def action_rooms(self) -> None:
        """Dummy action - KeyboardHandler handles this."""
        pass
    
    def action_recent(self) -> None:
        """Dummy action - KeyboardHandler handles this."""
        pass
    
    def action_settings(self) -> None:
        """Dummy action - KeyboardHandler handles this."""
        pass
    
    def action_command_mode(self) -> None:
        """Dummy action - KeyboardHandler handles this."""
        pass
    
    def action_home(self) -> None:
        """Navigate back to main menu/home."""
        if self.is_authenticated:
            try:
                splash_screen = self.query_one(SplashScreen)
                username = getattr(splash_screen, 'username', 'User')
                splash_screen.switch_to_main_menu(username)
            except Exception as e:
                self.notify(f"Navigation error: {str(e)}", severity="error")

    def on_button_pressed(self, event) -> None:
        """Handle button press events."""
        if event.button.id == "login-btn":
            self._handle_login()
        elif event.button.id == "register-btn":
            self._handle_register()
    
    def _handle_login(self):
        """Handle login button press."""
        try:
            username_input = self.query_one("#username-input", Input)
            password_input = self.query_one("#password-input", Input)

            username = str(username_input.value).strip()
            password = str(password_input.value).strip()

            if not username or not password:
                self.notify("Please enter both username and password", severity="error")
                return
            
            # Show progress indicator
            self.notify("Logging in...", severity="information")
            
            # Perform login in background to avoid blocking UI
            from functools import partial
            self.run_worker(partial(self._perform_login, username, password))
            
        except Exception as e:
            # Unexpected error (UI elements not found, etc.)
            self.notify("An unexpected error occurred during login", severity="error")
            self.notify(str(e), severity="error")
    
    async def _perform_login(self, username: str, password: str):
        """Worker function for background login."""
        try:
            # Set a reasonable timeout for the request
            import requests
            old_timeout = getattr(self.client.session, 'timeout', None)
            self.client.session.timeout = 10  # 10 second timeout
            
            login_result = self.client.login(username, password)
            
            # Reset timeout
            if old_timeout:
                self.client.session.timeout = old_timeout
            
            # Check if login was successful and call handler
            if self.client.is_authenticated():
                self._handle_login_success(username)
            else:
                self._handle_login_failure("Invalid username or password")
            
        except Exception as e:
            # Reset timeout
            try:
                if old_timeout:
                    self.client.session.timeout = old_timeout
            except:
                pass
            
            # Handle error
            self._handle_login_error(str(e))
    
    async def _perform_registration(self, username: str, password: str):
        """Worker function for background registration."""
        try:
            self.notify("Connecting to server...", severity="information")
            
            # Set a reasonable timeout for the request
            import requests
            old_timeout = getattr(self.client.session, 'timeout', None)
            self.client.session.timeout = 5  # Shorter timeout for faster failure
            
            self.notify("Sending registration request...", severity="information")
            register_result = self.client.register(username, password)
            
            self.notify(f"Registration result: {register_result}", severity="information")
            
            # Reset timeout
            if old_timeout:
                self.client.session.timeout = old_timeout
            
            # Check if registration was successful
            if register_result and 'error' not in register_result:
                # Handle successful registration
                self._handle_register_success(username)
            else:
                # Handle registration failure
                error_msg = register_result.get('error', 'Registration failed') if register_result else 'Registration failed'
                self._handle_register_error(error_msg)
            
        except Exception as e:
            self.notify(f"Registration exception: {str(e)}", severity="error")
            
            # Reset timeout
            try:
                if old_timeout:
                    self.client.session.timeout = old_timeout
            except:
                pass
            
            # Handle error
            self._handle_register_error(str(e))
    
    def _login_worker(self, username: str, password: str):
        """Background worker for login to prevent UI blocking."""
        try:
            # Set a reasonable timeout for the request
            import requests
            old_timeout = getattr(self.client.session, 'timeout', None)
            self.client.session.timeout = 10  # 10 second timeout
            
            login_result = self.client.login(username, password)
            
            # Reset timeout
            if old_timeout:
                self.client.session.timeout = old_timeout
            
            # Check if login was successful
            if self.client.is_authenticated():
                # Schedule success handling on main thread
                self.call_from_thread(self._handle_login_success, username)
            else:
                # Schedule failure handling on main thread
                self.call_from_thread(self._handle_login_failure, "Invalid username or password")
            
        except Exception as e:
            # Reset timeout
            try:
                if old_timeout:
                    self.client.session.timeout = old_timeout
            except:
                pass
            
            # Schedule error handling on main thread
            self.call_from_thread(self._handle_login_error, str(e))
    
    def _handle_login_success(self, username: str):
        """Handle successful login on main thread."""
        try:
            self.is_authenticated = True
            
            # Get reference to splash screen and switch to main menu
            if not self.splash_screen:
                self.splash_screen = self.query_one(SplashScreen)
            
            self.splash_screen.switch_to_main_menu(username)
            self.notify(f"Welcome, {username}!", severity="information")
            
        except Exception as e:
            self.notify("Login succeeded but UI update failed", severity="warning")
            self.notify(str(e), severity="error")
    
    def _handle_login_failure(self, error_message: str):
        """Handle login failure on main thread."""
        try:
            password_input = self.query_one("#password-input")
            
            self.notify(error_message, severity="error")
            # Clear password field for security
            password_input.value = ""
            
        except Exception as e:
            self.notify("Login failed and UI update failed", severity="error")
    
    def _handle_login_error(self, error_message: str):
        """Handle login errors on main thread."""
        try:
            password_input = self.query_one("#password-input")
            
            if any(word in error_message.lower() for word in ["timeout", "network", "connection", "failed to establish"]):
                self.notify("Login failed. Please check your connection and try again.", severity="error")
            elif "401" in error_message or "unauthorized" in error_message.lower():
                self.notify("Invalid username or password", severity="error")
            else:
                self.notify("Login failed. Please try again.", severity="error")
                self.notify(error_message, severity="error")
            
            # Clear password field for security
            password_input.value = ""
            
        except Exception as e:
            self.notify("Login failed and UI update failed", severity="error")

    def _handle_register(self):
        """Handle register button press."""
        try:
            username_input = self.query_one("#username-input", Input)
            password_input = self.query_one("#password-input", Input)
            
            username = str(username_input.value).strip()
            password = str(password_input.value).strip()
            
            if not username or not password:
                self.notify("Please enter both username and password", severity="error")
                return
            
            # Validate password length (backend requires at least 6 characters)
            if len(password) < 6:
                self.notify("Password must be at least 6 characters long", severity="error")
                return
            
            # Show progress indicator
            self.notify("Creating account...", severity="information")
            
            # Perform registration in background to avoid blocking UI
            from functools import partial
            self.run_worker(partial(self._perform_registration, username, password))
            
        except Exception as e:
            # Unexpected error (UI elements not found, etc.)
            self.notify("An unexpected error occurred during registration", severity="error")
            self.notify(str(e), severity="error")
    
    def _register_worker(self, username: str, password: str):
        """Background worker for registration to prevent UI blocking."""
        try:
            # Set a reasonable timeout for the request
            import requests
            old_timeout = getattr(self.client.session, 'timeout', None)
            self.client.session.timeout = 10  # 10 second timeout
            
            register_result = self.client.register(username, password)
            
            # Reset timeout
            if old_timeout:
                self.client.session.timeout = old_timeout
            
            # Schedule UI updates on main thread
            self.call_from_thread(self._handle_register_success, username)
            
        except Exception as e:
            # Reset timeout
            try:
                if old_timeout:
                    self.client.session.timeout = old_timeout
            except:
                pass
            
            # Schedule error handling on main thread
            self.call_from_thread(self._handle_register_error, str(e))
    
    def _handle_register_success(self, username: str):
        """Handle successful registration on main thread."""
        try:
            username_input = self.query_one("#username-input")
            password_input = self.query_one("#password-input")
            
            # Registration successful
            self.notify(f"Account created for {username}! Please login.", severity="information")
            
            # Clear both fields after successful registration
            username_input.value = ""
            password_input.value = ""
            
            # Focus on username field for login
            username_input.focus()
            
        except Exception as e:
            self.notify("Registration succeeded but UI update failed", severity="warning")
    
    def _handle_register_error(self, error_message: str):
        """Handle registration errors on main thread."""
        try:
            # Show appropriate error message
            if "Username already taken" in error_message or "already taken" in error_message:
                self.notify("Username already exists. Please choose a different username.", severity="error")
            elif "Password must be at least 6 characters" in error_message:
                self.notify("Password must be at least 6 characters long", severity="error")
            elif any(word in error_message.lower() for word in ["timeout", "network", "connection", "failed to establish"]):
                self.notify("Registration failed. Please check your connection and try again.", severity="error")
            elif "400" in error_message:
                self.notify("Invalid registration data. Please check your input.", severity="error")
            else:
                self.notify("Registration failed. Please try again.", severity="error")
                self.notify(error_message, severity="error")
            
            # Try to clear input fields, but don't fail if they're not available
            try:
                username_input = self.query_one("#username-input")
                password_input = self.query_one("#password-input")
                
                if "Username already taken" in error_message or "already taken" in error_message:
                    # Clear username field so user can try a different one
                    username_input.value = ""
                    username_input.focus()
                else:
                    # Clear password field for security in other error cases
                    password_input.value = ""
            except:
                # Input fields not available, that's okay - just show the notification
                pass
            
        except Exception as e:
            # Fallback - just show a basic error message
            self.notify("Registration failed. Please try again.", severity="error")
    
    def _handle_logout(self):
        """Handle logout action."""
        try:
            # Clear authentication state
            self.is_authenticated = False
            
            # Logout from the client if it has a logout method
            if hasattr(self.client, 'logout'):
                try:
                    self.client.logout()
                except Exception as e:
                    # Log the error but don't prevent logout from UI perspective
                    self.notify(f"Server logout error: {str(e)}", severity="warning")
            
            # Switch back to login screen
            if self.splash_screen:
                self.splash_screen.switch_to_login()
            
            self.notify("Logged out successfully", severity="information")
            
        except Exception as e:
            # Even if there's an error, we should still logout locally
            self.is_authenticated = False
            self.notify("Logout completed with errors", severity="warning")
            self.notify(str(e), severity="error")


    def on_key(self, event) -> None:
        """Handle keyboard shortcuts using the KeyboardHandler."""
        
        # Keys that Textual bindings will handle (these will call dummy action methods)
        textual_binding_keys = {"q", "question_mark", "l", "r", "p", "t", "c", "colon", "escape"}
        
        # Special handling for q and ? - only let Textual handle them in normal mode
        if event.key in {"q", "question_mark"}:
            # If we're in command mode, let KeyboardHandler process these as regular characters
            if self.keyboard_handler.mode == KeyboardMode.COMMAND:
                self.keyboard_handler.handle_key(event.key)
                event.stop()  # Prevent further propagation
                return
            # If we're in normal mode, let Textual handle them (help/quit actions)
            else:
                return  # Let Textual's binding system handle it

        # Handle enter key to dismiss result panel in normal mode
        if event.key == "enter" and self.keyboard_handler.mode == KeyboardMode.NORMAL:
            self.command_line_should_stay_visible = False
            try:
                command_line = self.query_one("#command-line", FloatingCommandLine)
                command_line.hide_result()
                command_line.set_active(False)  # Hide the command line too
            except Exception:
                pass  # Ignore if command line not available
            return
        
        # Handle escape key specially
        if event.key == "escape":
            if self.keyboard_handler.mode == KeyboardMode.COMMAND:
                self.keyboard_handler.handle_key("escape")
                event.stop()
                return
            else:
                # In normal mode, dismiss result panel and command line
                self.command_line_should_stay_visible = False
                try:
                    command_line = self.query_one("#command-line", FloatingCommandLine)
                    command_line.hide_result()
                    command_line.set_active(False)  # Hide the command line too
                except Exception:
                    pass  # Ignore if command line not available
                return
        
        # If this key has a Textual binding, let Textual handle it first (calls dummy method)
        # then let KeyboardHandler also process it for actual functionality
        if event.key in textual_binding_keys:
            # For colon specifically, we want KeyboardHandler to handle the command mode logic
            if event.key == "colon":
                self.keyboard_handler.handle_key(":")
            elif event.key in {"l", "r", "p", "t", "c"}:
                # For other bound keys, let KeyboardHandler process them too
                self.keyboard_handler.handle_key(event.key)
            return
        
        # For all other keys, use the keyboard handler normally
        # Map special keys to their actual characters for command input
        key_to_handle = event.key
        if event.key == "space":
            key_to_handle = "space"  # Keep as "space" for handler to recognize
        elif event.key == "minus":
            key_to_handle = "minus"  # Keep as "minus" for handler to recognize
        
        handled = self.keyboard_handler.handle_key(key_to_handle)
        
        # Show current mode in debug info (only show unhandled keys in normal mode)
        if not handled and self.keyboard_handler.mode == KeyboardMode.NORMAL:
            # Only show unhandled key notifications for single character keys that aren't common navigation
            if len(event.key) == 1 and event.key.isalnum():
                if self.is_authenticated:
                    self.notify(f"Unhandled key: '{event.key}' - Try 'r' (rooms), 'h' (recent), 's' (settings), or ':' for command mode")
                else:
                    self.notify(f"Unhandled key: '{event.key}' - Please login first or try ':' for command mode")
            # For special keys, we might want to handle them silently
            pass


if __name__ == "__main__":
    app = AeroStream()
    app.run()
