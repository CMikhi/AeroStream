from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Middle, Vertical
from textual.widgets import Static, Footer
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
        
        # Command line positioned at bottom left (outside the centered container)
        yield CommandLine(id="command-line", classes="command-line")
        
        # Footer with quick commands
        yield Footer()



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
        Binding(key="l", action="login", description="Login"),
        Binding(key="r", action="register", description="Register"),
        Binding(key="p", action="rooms", description="Rooms"),
        Binding(key="t", action="recent", description="Recent Rooms"),
        Binding(key="c", action="settings", description="Settings"),
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
    
    def _setup_keyboard_callbacks(self):
        """Set up callbacks for keyboard handler events."""
        self.keyboard_handler.on_mode_change = self._on_mode_change
        self.keyboard_handler.on_command_buffer_change = self._on_command_buffer_change
        self.keyboard_handler.on_command_executed = self._on_command_executed
        self.keyboard_handler.on_error = self._on_error
    
    def _register_custom_commands(self):
        """Register application-specific commands."""
        # Menu navigation commands (with colon command support)
        self.keyboard_handler.register_command("login", self._login_command, "Go to login screen", ["l"])
        self.keyboard_handler.register_command("register", self._register_command, "Go to register screen", ["r", "reg"])
        self.keyboard_handler.register_command("rooms", self._rooms_command, "Go to rooms screen", ["p", "projects"])
        self.keyboard_handler.register_command("recent", self._recent_command, "Go to recent rooms screen", ["t", "history"])
        self.keyboard_handler.register_command("settings", self._settings_command, "Go to settings screen", ["config", "preferences"])
        
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
        help_text = """
╭─ Ignite TUI Help ─────────────────────────────────────────────────╮
│                                                                   │
│  Single Key Commands (press directly):                           │
│    l - Login                    r - Register                     │
│    p - Rooms                    t - Recent Rooms                 │
│    c - Settings                 h/? - Help                       │
│    q - Quit                     : - Command mode                 │
│                                                                   │
│  Colon Commands (press : then type):                             │
│    :help, :h         - Show this help                           │
│    :quit, :q         - Exit application                         │
│    :login, :l        - Go to login                              │
│    :register, :r     - Go to register                           │
│    :rooms, :p        - Go to rooms                              │
│    :recent, :t       - Recent rooms                             │
│    :settings, :config - Settings                                │
│    :version, :v      - Show version                             │
│    :status, :st      - Show status                              │
│    :save, :w         - Save state                               │
│    :refresh, :reload - Refresh interface                        │
│                                                                   │
│  Command Mode Navigation:                                         │
│    Enter - Execute command      Escape - Cancel                  │
│    ↑/↓ - Command history        Backspace - Delete char         │
│                                                                   │
╰───────────────────────────────────────────────────────────────────╯
        """
        return help_text.strip()
    
    def compose(self) -> ComposeResult:
        yield SplashScreen()
    
    # Action methods for Textual bindings (dummy methods to prevent double execution)
    def action_help(self) -> None:
        """Handle help action from ? key."""
        result = self._custom_help_command()
        if result:
            self.notify(result)
    
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

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts using the KeyboardHandler."""
        
        # Keys that Textual bindings will handle (these will call dummy action methods)
        textual_binding_keys = {"q", "question_mark", "l", "r", "p", "t", "c", "colon"}
        
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
        
        # If this key has a Textual binding, let Textual handle it first (calls dummy method)
        # then let KeyboardHandler also process it for actual functionality
        if event.key in textual_binding_keys:
            # For colon specifically, we want KeyboardHandler to handle the command mode logic
            if event.key == "colon":
                self.keyboard_handler.handle_key(":")
            # For other bound keys, let KeyboardHandler process them too
            elif event.key in {"l", "r", "p", "t", "c"}:
                self.keyboard_handler.handle_key(event.key)
            return
        
        # For all other keys, use the keyboard handler normally
        handled = self.keyboard_handler.handle_key(event.key)
        
        # Show current mode in debug info (only show unhandled keys in normal mode)
        if not handled and self.keyboard_handler.mode == KeyboardMode.NORMAL:
            # Only show unhandled key notifications for single character keys that aren't common navigation
            if len(event.key) == 1 and event.key.isalnum():
                self.notify(f"Unhandled key: '{event.key}' - Try pressing ':' for command mode or 'h' for help")
            # For special keys, we might want to handle them silently
            pass


if __name__ == "__main__":
    app = AeroStream()
    app.run()