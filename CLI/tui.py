from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Middle, Vertical, Horizontal
from textual.widgets import Static, Footer, Input, Button
from PIL import Image
from PIL import ImageEnhance
from keyboard_handler import KeyboardHandler, KeyboardMode

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
                    ocean_colors_textual = ["blue", "bright_blue", "cyan", "bright_cyan"]
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
                    fire_colors_textual = ["bright_red", "red", "yellow", "bright_yellow"]
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
                fire_colors = ["bright_red", "red", "yellow", "bright_yellow"]
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
    
    def __init__(self, icon: str, label: str, shortcut: str, **kwargs):
        super().__init__(**kwargs)
        self.icon = icon
        self.label = label
        self.shortcut = shortcut
    
    def render(self) -> str:
        main_content = f"[bright_white]{self.icon}[/] [white]{self.label}[/]"
        shortcut_part = f"[dim]{self.shortcut}[/]"
        # Add padding to create space between content and shortcut
        padding = " " * (40 - 1 - len(self.label))  # Adjust 40 to change spacing
        if self.label == 'settings':
            padding = (" " * (33 - 1 - len(self.label)))+" " # Adjust 40 to change spacing
        return f"{main_content}{padding}{shortcut_part}"

class CommandLine(Static):
    """A dedicated command line widget for handling text input display."""
    
    def __init__(self, **kwargs):
        super().__init__("", **kwargs)
        self.is_active = False
        self.text_buffer = ""
        self._current_content = ""
    
    def set_active(self, active: bool):
        """Set the command line active state."""
        self.is_active = active
        if active:
            self.add_class("active")
            self.styles.display = "block"
        else:
            self.remove_class("active")
            self.text_buffer = ""
            self.styles.display = "none"
        self._update_content()
    
    def update_buffer(self, text: str):
        """Update the command line buffer text."""
        self.text_buffer = text
        self._update_content()
    
    def _update_content(self):
        """Update the widget content."""
        if self.is_active:
            new_content = f":{self.text_buffer}█"
        else:
            new_content = ""
        
        # Only update if content has actually changed
        if new_content != self._current_content:
            self._current_content = new_content
            self.update(new_content)
            # Force a refresh of the entire screen to ensure visibility
            if self.app:
                self.app.refresh()


class LoginScreen(Static):
    """The login screen with username/password inputs."""
    
    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                with Vertical():
                    # ASCII Art Logo
                    yield Static(OCEAN_ASCII_ART, classes="ascii-art")
                    
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
                                yield MenuItem("📁", "Rooms", "r", classes="menu-item")
                                yield MenuItem("🕐", "Recent Rooms", "h", classes="menu-item") 
                                yield MenuItem("⚙️", "Settings", "s", classes="menu-item")
                                yield MenuItem("🚪", "Logout", "q", classes="menu-item")
        

class SplashScreen(Static):
    """The main splash screen container that manages login/main menu."""

    def __init__(self):
        super().__init__()
        self.current_screen = "login"  # "login" or "main"
        self.username = ""

    def compose(self) -> ComposeResult:
        # Start with login screen
        yield LoginScreen(id="login-screen")
        
        # Command line positioned at bottom left (outside the centered container)
        yield CommandLine(id="command-line", classes="command-line")
        
        # Footer with quick commands
        yield Footer()
    
    def switch_to_main_menu(self, username: str):
        """Switch from login screen to main menu."""
        self.username = username
        self.current_screen = "main"
        
        # Remove login screen and add main menu
        login_screen = self.query_one("#login-screen")
        login_screen.remove()
        
        main_menu = MainMenuScreen()
        main_menu.id = "main-screen"
        self.mount(main_menu, before="#command-line")
        
        # Update welcome message
        welcome_msg = self.query_one("#welcome-msg")
        welcome_msg.update(f"Welcome back, {username}!")
    
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
        Binding(key="colon", action="command_mode", description="Command mode"),
    ]
    
    CSS = """
    Screen {
        background: #1e1e2e;
        color: white;
    }
    
    SplashScreen {
        height: 100%;
        width: 100%;
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
    
    .command-line {
        color: #f9e2af;
        background: #1e1e2e;
        border: solid #fab387;
        text-align: left;
        padding: 0 1;
        height: 3;
        width: 60;
        dock: bottom;
        display: none;
    }
    
    .command-line.active {
        display: block !important;
        background: #313244;
        border: solid #89b4fa;
        color: #cdd6f4;
    }
    """

    # KEYBOARD SHORTCUTS INTEGRATION --- DO NOT TOUCH ---
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.keyboard_handler = KeyboardHandler(self)
        self._setup_keyboard_callbacks()
        self._register_custom_commands()
        self.splash_screen = None
        self.is_authenticated = False
    
    def _setup_keyboard_callbacks(self):
        """Set up callbacks for keyboard handler events."""
        self.keyboard_handler.on_mode_change = self._on_mode_change
        self.keyboard_handler.on_command_buffer_change = self._on_command_buffer_change
        self.keyboard_handler.on_command_executed = self._on_command_executed
        self.keyboard_handler.on_error = self._on_error
    
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
        self.keyboard_handler.register_single_key("r", self._rooms_command)
        self.keyboard_handler.register_single_key("h", self._recent_command)
        self.keyboard_handler.register_single_key("s", self._settings_command)
        
        # Note: q and ? are still handled by Textual's binding system
        # : (colon) is handled by KeyboardHandler in the on_key method
    
    def _on_mode_change(self, mode: KeyboardMode):
        """Handle keyboard mode changes."""
        try:
            command_line = self.query_one("#command-line", CommandLine)
            command_line.set_active(mode == KeyboardMode.COMMAND)
        except Exception as e:
            # Command line widget not available yet, schedule for next tick
            self.call_later(self._delayed_mode_change, mode)
    
    def _delayed_mode_change(self, mode: KeyboardMode):
        """Handle delayed mode changes when widget isn't ready."""
        try:
            command_line = self.query_one("#command-line", CommandLine)
            command_line.set_active(mode == KeyboardMode.COMMAND)
        except Exception:
            # Still not ready, ignore silently
            pass
    
    def _on_command_buffer_change(self, buffer: str):
        """Handle command buffer changes."""
        try:
            command_line = self.query_one("#command-line", CommandLine)
            command_line.update_buffer(buffer)
        except Exception as e:
            # Widget not available, schedule for later
            self.call_later(self._delayed_buffer_change, buffer)
    
    def _delayed_buffer_change(self, buffer: str):
        """Handle delayed buffer changes."""
        try:
            command_line = self.query_one("#command-line", CommandLine)
            command_line.update_buffer(buffer)
        except Exception:
            # Still not ready, ignore silently
            pass
    
    def _on_command_executed(self, command: str, result):
        """Handle command execution."""
        if result and isinstance(result, str):
            self.notify(result)
        else:
            self.notify(f"Executed: {command}")
    
    def _on_error(self, error: str):
        """Handle errors from keyboard handler."""
        self.notify(error, severity="error")
    
    # Command handlers
    def _login_command(self):
        """Handle login command."""
        if not self.is_authenticated:
            self._handle_login()
        else:
            self.notify("Already logged in")
    
    def _register_command(self):
        """Handle register command."""
        if not self.is_authenticated:
            self._handle_register()
        else:
            self.notify("Please logout first to register a new account")
    
    def _logout_command(self):
        """Handle logout command."""
        if self.is_authenticated:
            self._handle_logout()
        else:
            self.notify("Not currently logged in")
    
    def _rooms_command(self):
        """Handle rooms command."""
        if self.is_authenticated:
            self.notify("Selected: Rooms")
        else:
            self.notify("Please login first")
    
    def _recent_command(self):
        """Handle recent rooms command."""
        if self.is_authenticated:
            self.notify("Selected: Recent Rooms")
        else:
            self.notify("Please login first")
    
    def _settings_command(self):
        """Handle settings command."""
        if self.is_authenticated:
            self.notify("Selected: Settings")
        else:
            self.notify("Please login first")
    
    # TODO: Update to variable version function
    def _version_command(self):
        """Handle version command."""
        return "Ignite TUI v1.0.0 - rolling-4b0a60e"
    
    def _status_command(self):
        """Handle status command."""
        mode = "Command Mode" if self.keyboard_handler.is_in_command_mode() else "Normal Mode"
        return f"Status: {mode} | Server: Disconnected | Theme: Dark"
    
    def _refresh_command(self):
        """Handle refresh command."""
        self.refresh()
        return "Interface refreshed"
    
    def _theme_command(self):
        """Handle theme command."""
        return "Theme toggle not yet implemented"
    
    def _connect_command(self):
        """Handle connect command."""
        return "Connecting to server..."
    
    def _disconnect_command(self):
        """Handle disconnect command."""
        return "Disconnected from server"
    
    def _home_command(self):
        """Handle home command."""
        return "Navigated to home screen"
    
    def _back_command(self):
        """Handle back command."""
        return "Going back"
    
    def _next_command(self):
        """Handle next command."""
        return "Moving to next item"
    
    def _previous_command(self):
        """Handle previous command."""
        return "Moving to previous item"
    
    def _debug_command(self):
        """Handle debug command."""
        return "Debug mode toggled"
    
    def _log_command(self):
        """Handle log command."""
        return "Log viewer not yet implemented"
    
    def _save_command(self):
        """Handle save command."""
        return "State saved"
    
    def _custom_help_command(self):
        """Handle custom help command with both single-key and colon commands."""
        if self.is_authenticated:
            help_text = """
╭─ Ignite TUI Help (Authenticated) ────────────────────────────────╮
│                                                                   │
│  Single Key Commands (press directly):                           │
│    r - Rooms                    h - Recent Rooms                 │
│    s - Settings                 ? - Help                         │
│    q - Quit                     : - Command mode                 │
│                                                                   │
│  Colon Commands (press : then type):                             │
│    :help                 - Show this help                       │
│    :quit, :q             - Exit application                     │
│    :rooms, :r, :room     - Go to rooms                          │
│    :recent, :h, :history - Recent rooms                         │
│    :settings, :s, :config - Settings                            │
│    :logout, :exit        - Logout                               │
│    :version, :v          - Show version                         │
│    :status, :st          - Show status                          │
│    :save, :w             - Save state                           │
│    :refresh, :reload     - Refresh interface                    │
│                                                                   │
│  Command Mode Navigation:                                         │
│    Enter - Execute command      Escape - Cancel                  │
│    ↑/↓ - Command history        Backspace - Delete char         │
│                                                                   │
╰───────────────────────────────────────────────────────────────────╯
            """
        else:
            help_text = """
╭─ Ignite TUI Help (Login Required) ───────────────────────────────╮
│                                                                   │
│  Login Interface:                                                 │
│    Tab/Shift+Tab - Navigate between username/password fields    │
│    Enter - Submit login form                                     │
│    ? - Help                     q - Quit                         │
│    : - Command mode                                               │
│                                                                   │
│  Colon Commands (press : then type):                             │
│    :help                 - Show this help                       │
│    :quit, :q             - Exit application                     │
│    :login, :l            - Attempt login with current fields    │
│    :register, :reg       - Attempt registration                 │
│    :version, :v          - Show version                         │
│    :status, :st          - Show status                          │
│    :refresh, :reload     - Refresh interface                    │
│                                                                   │
│  Command Mode Navigation:                                         │
│    Enter - Execute command      Escape - Cancel                  │
│    ↑/↓ - Command history        Backspace - Delete char         │
│                                                                   │
│  Note: Most features require login. Please authenticate first.   │
│                                                                   │
╰───────────────────────────────────────────────────────────────────╯
            """
        return help_text.strip()
    
    def compose(self) -> ComposeResult:
        self.splash_screen = SplashScreen()
        yield self.splash_screen
    
    # Action methods for Textual bindings (dummy methods to prevent double execution)
    def action_help(self) -> None:
        """Handle help action from ? key."""
        result = self._custom_help_command()
        if result:
            self.notify(result)
    
    def action_rooms(self) -> None:
        """Handle rooms action."""
        self._rooms_command()
    
    def action_recent(self) -> None:
        """Handle recent action."""
        self._recent_command()
    
    def action_settings(self) -> None:
        """Handle settings action."""
        self._settings_command()
    
    def action_command_mode(self) -> None:
        """Dummy action - KeyboardHandler handles this."""
        pass

    def on_button_pressed(self, event) -> None:
        """Handle button press events."""
        if event.button.id == "login-btn":
            self._handle_login()
        elif event.button.id == "register-btn":
            self._handle_register()
    
    def _handle_login(self):
        """Handle login button press."""
        try:
            username_input = self.query_one("#username-input")
            password_input = self.query_one("#password-input")
            
            username = username_input.value.strip()
            password = password_input.value.strip()
            
            if not username or not password:
                self.notify("Please enter both username and password", severity="error")
                return
            
            # TODO: Add actual authentication logic here
            # For now, simulate successful login
            self.is_authenticated = True
            self.splash_screen.switch_to_main_menu(username)
            self.notify(f"Welcome, {username}!", severity="information")
            
        except Exception as e:
            self.notify("Login failed. Please try again.", severity="error")
    
    def _handle_register(self):
        """Handle register button press."""
        try:
            username_input = self.query_one("#username-input")
            password_input = self.query_one("#password-input")
            
            username = username_input.value.strip()
            password = password_input.value.strip()
            
            if not username or not password:
                self.notify("Please enter both username and password", severity="error")
                return
            
            # TODO: Add actual registration logic here
            # For now, simulate successful registration
            self.notify(f"Account created for {username}! Please login.", severity="information")
            
        except Exception as e:
            self.notify("Registration failed. Please try again.", severity="error")
    
    def _handle_logout(self):
        """Handle logout action."""
        self.is_authenticated = False
        self.splash_screen.switch_to_login()
        self.notify("Logged out successfully", severity="information")

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts using the KeyboardHandler."""
        
        # Update binding keys based on current screen
        if self.is_authenticated:
            textual_binding_keys = {"q", "question_mark", "r", "h", "s", "colon"}
        else:
            textual_binding_keys = {"q", "question_mark", "colon"}
        
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
        
        # Handle authenticated screen shortcuts
        if self.is_authenticated and event.key in {"r", "h", "s"}:
            if event.key == "r":
                self._rooms_command()
            elif event.key == "h":
                self._recent_command()
            elif event.key == "s":
                self._settings_command()
            return
        
        # If this key has a Textual binding, let Textual handle it first (calls dummy method)
        # then let KeyboardHandler also process it for actual functionality
        if event.key in textual_binding_keys:
            # For colon specifically, we want KeyboardHandler to handle the command mode logic
            if event.key == "colon":
                self.keyboard_handler.handle_key(":")
            return
        
        # For all other keys, use the keyboard handler normally
        handled = self.keyboard_handler.handle_key(event.key)
        
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