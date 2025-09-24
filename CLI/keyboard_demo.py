"""
Example usage of the KeyboardHandler class

This demonstrates how to use the keyboard handler independently of the TUI.
"""

from typing import Any
from keyboard_handler import KeyboardHandler, KeyboardMode


class MockApp:
    """Mock app for demonstration purposes."""
    
    def __init__(self):
        self.running = True
        self.notifications = []
    
    def notify(self, message: str, severity: str = "info"):
        """Mock notification system."""
        print(f"[{severity.upper()}] {message}")
        self.notifications.append(message)
    
    def exit(self):
        """Mock exit function."""
        self.running = False
        print("Application exiting...")


def demo_keyboard_handler():
    """Demonstrate the keyboard handler functionality."""
    print("Keyboard Handler Demo")
    print("=" * 50)
    
    # Create mock app and keyboard handler
    app = MockApp()
    kb_handler = KeyboardHandler(app)
    
    # Set up callback for command results
    def on_command_executed(command: str, result: Any):
        if result is not None:
            print(f"[RESULT] {result}")
    
    kb_handler.on_command_executed = on_command_executed
    
    # Register some custom commands
    def custom_hello(name: str = "World"):
        return f"Hello, {name}!"
    
    def custom_echo(*args):
        return " ".join(args) if args else "Echo!"
    
    def list_files():
        return "Files: file1.txt, file2.txt, file3.txt"
    
    kb_handler.register_command("hello", custom_hello, "Say hello", ["hi"])
    kb_handler.register_command("echo", custom_echo, "Echo arguments")
    kb_handler.register_command("list", list_files, "List files", ["ls"])
    
    # Register the single-key commands mentioned in the demo
    def mock_menu_item(item_name: str):
        """Mock menu item handler."""
        return lambda: app.notify(f"Mock menu item '{item_name}' selected")
    
    kb_handler.register_single_key("l", mock_menu_item("List"))
    kb_handler.register_single_key("r", mock_menu_item("Refresh"))
    kb_handler.register_single_key("p", mock_menu_item("Preferences"))
    kb_handler.register_single_key("t", mock_menu_item("Toggle"))
    kb_handler.register_single_key("s", mock_menu_item("Settings"))
    
    print("Available single-key commands: q (quit), l, r, p, t, s")
    print("Available multi-character commands:")
    print("  :hello [name] - Say hello")
    print("  :echo <args> - Echo arguments")
    print("  :list - List files")
    print("  :help - Show all commands")
    print("  :quit - Exit")
    print("\nPress ':' to enter command mode, then type a command and press Enter")
    print("Press 'q' for quick quit, or 'l', 'r', 'p', 't', 's' for menu items")
    print("Press Ctrl+C to exit demo")
    print()
    
    try:
        while app.running:
            # Show current mode and prompt
            mode_indicator = "CMD" if kb_handler.is_in_command_mode() else "NORMAL"
            prompt = f"[{mode_indicator}] {kb_handler.get_command_prompt()}"
            
            # Get user input (simulating key presses)
            user_input = input(f"{prompt}> ").strip()
            
            if not user_input:
                # Handle empty input - if in command mode, simulate Enter to execute/cancel
                if kb_handler.is_in_command_mode():
                    kb_handler.handle_key("enter")
                continue
            
            # If we're in command mode, handle differently
            if kb_handler.is_in_command_mode():
                # In command mode, process each character then Enter
                for char in user_input:
                    kb_handler.handle_key(char)
                kb_handler.handle_key("enter")
            else:
                # In normal mode, handle based on input type
                if len(user_input) == 1:
                    # Single key
                    handled = kb_handler.handle_key(user_input)
                    if not handled:
                        print(f"Unhandled key: {user_input}")
                elif user_input.startswith(":"):
                    # Command input - handle specially
                    # First enter command mode with ':'
                    kb_handler.handle_key(":")
                    # Then add the rest of the command
                    command_part = user_input[1:]  # Remove the ':' prefix
                    for char in command_part:
                        kb_handler.handle_key(char)
                    # Finally simulate Enter press
                    kb_handler.handle_key("enter")
                else:
                    # Multi-character input that doesn't start with colon - process each character individually
                    for char in user_input:
                        handled = kb_handler.handle_key(char)
                        if not handled:
                            print(f"Unhandled key: {char}")
                            # Stop processing remaining characters if we hit an unhandled key
                            break
    
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except EOFError:
        print("\nDemo ended")
    
    print("Keyboard Handler Demo completed!")


if __name__ == "__main__":
    demo_keyboard_handler()