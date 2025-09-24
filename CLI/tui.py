from textual.app import App, ComposeResult
from textual.containers import Center, Middle, Vertical
from textual.widgets import Static
from PIL import Image
from PIL import ImageEnhance
from keyboard_handler import KeyboardHandler, KeyboardMode

def image_to_ascii(image_path: str, width: int = 100, contrast_factor: float = 1.5, brightness_factor: float = 1.2, threshold: int = 150) -> str:
    """Convert an image to ASCII art with increased contrast and brightness, and remove surrounding whitespace.
    Skip sections under a certain brightness or confidence."""

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
        new_height = int(aspect_ratio * width * 0.55)
        img = img.resize((width, new_height))
        pixels = img.getdata()

        ascii_str = ""
        for pixel in pixels:
            # if pixel >= min_brightness:
            ascii_str += chars[pixel // 25]
            # else:
            #ascii_str += " "  # Use space for sections below min_brightness

        ascii_lines = [ascii_str[i:i + width] for i in range(0, len(ascii_str), width)]
        return "\n".join(ascii_lines)
    except Exception as e:
        return f"Error generating ASCII art: {e}"

# Generate ASCII art from a .png file
try:
    CUSTOM_ASCII_ART = image_to_ascii("CLI/assets/ascii_art.png", width=80)
except FileNotFoundError:
    try:
        with open("CLI/assets/simple_ascii-art.txt", "r") as file:
            original_art = file.read()
            CUSTOM_ASCII_ART = original_art
    except FileNotFoundError:
        # Fallback to simple text if file not found
        CUSTOM_ASCII_ART = r"""
        ___            _ _       
        | _|__ _ _ __ (_) |_ ___ 
        | |/ _` | '_ \| | __/ _ \
        | | (_| | | | | | ||  __/
        |___\__, |_| |_|_|\__\___|
            |___/                
        """

class MenuItem(Static):
    """A menu item with icon and shortcut key."""
    
    def __init__(self, icon: str, label: str, shortcut: str, **kwargs):
        super().__init__(**kwargs)
        self.icon = icon
        self.label = label
        self.shortcut = shortcut
    
    def render(self) -> str:
        return f"[bright_white]{self.icon}[/] [white]{self.label}[/]"


class SplashScreen(Static):
    """The main splash screen container."""
    
    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                with Vertical(classes="main-container"):
                    # ASCII Art Logo
                    yield Static(CUSTOM_ASCII_ART, classes="ascii-art")
                    
                    # Menu items
                    with Vertical(classes="menu-container"):
                        yield MenuItem("⌘", "Login", "l", classes="menu-item")
                        yield MenuItem("📄", "Register", "r", classes="menu-item")
                        yield MenuItem("📁", "Rooms", "p", classes="menu-item")
                        yield MenuItem("🕐", "Recent Rooms", "t", classes="menu-item")
                        yield MenuItem("⚙️", "Settings", "c", classes="menu-item")
                    
                    # Version info at bottom
                    yield Static("https://homebred-irredeemably-madie.ngrok-free.dev/test\nrolling-4b0a60e", classes="version-info")
                    
                    # Command line (initially hidden)
                    yield Static("", id="command-line", classes="command-line")


class LunarVimApp(App):
    """LunarVim-style TUI application."""
    
    CSS = """
    Screen {
        background: #1e1e2e;
        color: white;
    }
    
    SplashScreen {
        height: 100%;
        width: 100%;
    }
    
    .main-container {
        width: auto;
        height: auto;
        text-align: center;
        align-horizontal: center;
    }
    
    .ascii-art {
        color: #b4befe;
        margin-top: -8;
        text-align: center;
        width: auto;
        height: auto;
        align-horizontal: center;
    }
    
    .menu-container {
        width: auto;
        height: auto;
        margin: 0 0 4 0;
        text-align: center;
        align-horizontal: center;
        margin-left: 20;
    }
    
    .menu-item {
        margin: 1 0;
        text-align: left;
        width: auto;
        padding: 0 2;
    }
    
    .menu-item:hover {
        background: #313244;
        color: #89b4fa;
    }
    
    .version-info {
        color: #fab387;
        text-align: center;
        margin-top: 2;
        margin-left: 0;
    }
    
    .command-line {
        color: #f9e2af;
        background: #313244;
        text-align: left;
        margin-top: 2;
        padding: 0 1;
        height: 1;
        display: none;
    }
    
    .command-line.active {
        display: block;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.keyboard_handler = KeyboardHandler(self)
        self._setup_keyboard_callbacks()
        self._register_custom_commands()
    
    def _setup_keyboard_callbacks(self):
        """Set up callbacks for keyboard handler events."""
        self.keyboard_handler.on_mode_change = self._on_mode_change
        self.keyboard_handler.on_command_buffer_change = self._on_command_buffer_change
        self.keyboard_handler.on_command_executed = self._on_command_executed
        self.keyboard_handler.on_error = self._on_error
    
    def _register_custom_commands(self):
        """Register application-specific commands."""
        # Menu navigation commands
        self.keyboard_handler.register_command("login", self._login_command, "Go to login screen", ["l"])
        self.keyboard_handler.register_command("register", self._register_command, "Go to register screen", ["r", "reg"])
        self.keyboard_handler.register_command("rooms", self._rooms_command, "Go to rooms screen", ["p"])
        self.keyboard_handler.register_command("recent", self._recent_command, "Go to recent rooms screen", ["t"])
        self.keyboard_handler.register_command("settings", self._settings_command, "Go to settings screen", ["s", "config"])
        
        # Register single-key commands for quick access
        self.keyboard_handler.register_single_key("l", self._login_command)
        self.keyboard_handler.register_single_key("r", self._register_command)
        self.keyboard_handler.register_single_key("p", self._rooms_command)
        self.keyboard_handler.register_single_key("t", self._recent_command)
        self.keyboard_handler.register_single_key("s", self._settings_command)
    
    def _on_mode_change(self, mode: KeyboardMode):
        """Handle keyboard mode changes."""
        try:
            command_line = self.query_one("#command-line", Static)
            if mode == KeyboardMode.COMMAND:
                command_line.add_class("active")
                command_line.update(":")
            else:
                command_line.remove_class("active")
                command_line.update("")
        except Exception:
            # Command line widget not available yet
            pass
    
    def _on_command_buffer_change(self, buffer: str):
        """Handle command buffer changes."""
        try:
            command_line = self.query_one("#command-line", Static)
            command_line.update(f":{buffer}")
        except Exception:
            # Command line widget not available yet
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
        self.notify("Selected: Login")
    
    def _register_command(self):
        """Handle register command."""
        self.notify("Selected: Register")
    
    def _rooms_command(self):
        """Handle rooms command."""
        self.notify("Selected: Rooms")
    
    def _recent_command(self):
        """Handle recent rooms command."""
        self.notify("Selected: Recent Rooms")
    
    def _settings_command(self):
        """Handle settings command."""
        self.notify("Selected: Settings")
    
    def compose(self) -> ComposeResult:
        yield SplashScreen()
    
    def on_key(self, event) -> None:
        """Handle keyboard shortcuts using the KeyboardHandler."""
        # Let the keyboard handler process the key
        handled = self.keyboard_handler.handle_key(event.key)
        
        # If not handled, we could add fallback behavior here
        if not handled:
            # For debugging purposes, you can uncomment the next line
            self.notify(f"Unhandled key: {event.key}")
            pass


if __name__ == "__main__":
    app = LunarVimApp()
    app.run()