"""
Keyboard Handler for TUI Application

This module provides a comprehensive keyboard handling system that supports:
- Single-key commands (like 'q' to quit)
- Multi-character command mode (like vim's ':' commands)
- Command parsing and validation
- Extensible command registration system
"""

from typing import Dict, Callable, Optional, Any, List
from dataclasses import dataclass, field
from enum import Enum


class KeyboardMode(Enum):
    """Different modes of keyboard input."""
    NORMAL = "normal"
    COMMAND = "command"


@dataclass
class Command:
    """Represents a command that can be executed."""
    name: str
    handler: Callable
    description: str
    aliases: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []


class KeyboardHandler:
    """
    Handles keyboard input for both single-key commands and multi-character commands.
    
    Features:
    - Normal mode: Single key presses trigger immediate actions
    - Command mode: Type commands after pressing ':' and execute with Enter
    - Extensible command system with aliases
    - Command history and validation
    """
    
    def __init__(self, app_instance: Any = None):
        self.app = app_instance
        self.mode = KeyboardMode.NORMAL
        self.command_buffer = ""
        self.command_history: List[str] = []
        self.history_index = -1
        
        # Single-key command mappings
        self.single_key_commands: Dict[str, Callable] = {}
        
        # Multi-character commands
        self.commands: Dict[str, Command] = {}
        
        # Callbacks for mode changes and command buffer updates
        self.on_mode_change: Optional[Callable[[KeyboardMode], None]] = None
        self.on_command_buffer_change: Optional[Callable[[str], None]] = None
        self.on_command_executed: Optional[Callable[[str, Any], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        
        # Initialize default commands
        self._setup_default_commands()
    
    def _setup_default_commands(self):
        """Set up default commands that are commonly used."""
        # Register basic commands
        self.register_command("quit", self._quit_command, "Exit the application", ["q", "exit"])
        self.register_command("help", self._help_command, "Show available commands", ["h"])
        self.register_command("clear", self._clear_command, "Clear command history", ["cls"])
        
        # Register basic single-key commands
        self.register_single_key("q", self._quit_command)
        self.register_single_key("escape", self._cancel_command)
    
    def register_single_key(self, key: str, handler: Callable) -> None:
        """Register a single-key command."""
        self.single_key_commands[key] = handler
    
    def register_command(self, name: str, handler: Callable, description: str, aliases: Optional[List[str]] = None) -> None:
        """Register a multi-character command."""
        command = Command(name, handler, description, aliases)
        self.commands[name] = command
        
        # Register aliases
        if command.aliases:
            for alias in command.aliases:
                self.commands[alias] = command
    
    def unregister_command(self, name: str) -> None:
        """Unregister a command and its aliases."""
        if name in self.commands:
            command = self.commands[name]
            # Remove main command and all aliases
            keys_to_remove = [name]
            if command.aliases:
                keys_to_remove.extend(command.aliases)
            for key in keys_to_remove:
                self.commands.pop(key, None)
    
    def handle_key(self, key: str) -> bool:
        """
        Handle a key press based on the current mode.
        
        Args:
            key: The key that was pressed
            
        Returns:
            bool: True if the key was handled, False otherwise
        """
        if self.mode == KeyboardMode.NORMAL:
            return self._handle_normal_mode(key)
        elif self.mode == KeyboardMode.COMMAND:
            return self._handle_command_mode(key)
        return False
    
    def _handle_normal_mode(self, key: str) -> bool:
        """Handle key presses in normal mode."""
        # Check for command mode trigger
        if key == ":":
            self._enter_command_mode()
            return True
        
        # Check for single-key commands
        if key in self.single_key_commands:
            try:
                self.single_key_commands[key]()
                return True
            except Exception as e:
                self._notify_error(f"Error executing command: {str(e)}")
                return True
        
        return False
    
    def _handle_command_mode(self, key: str) -> bool:
        """Handle key presses in command mode."""
        if key == "enter":
            self._execute_command()
            return True
        elif key == "escape":
            self._cancel_command()
            return True
        elif key == "backspace":
            if self.command_buffer:
                self.command_buffer = self.command_buffer[:-1]
                self._notify_buffer_change()
            return True
        elif key == "up":
            self._navigate_history(-1)
            return True
        elif key == "down":
            self._navigate_history(1)
            return True
        elif len(key) == 1 and key.isprintable():
            # Allow all printable characters including space
            self.command_buffer += key
            self._notify_buffer_change()
            return True
        
        return False
    
    def _enter_command_mode(self) -> None:
        """Enter command input mode."""
        self.mode = KeyboardMode.COMMAND
        self.command_buffer = ""
        self.history_index = -1
        self._notify_mode_change()
    
    def _exit_command_mode(self) -> None:
        """Exit command input mode."""
        self.mode = KeyboardMode.NORMAL
        self.command_buffer = ""
        self.history_index = -1
        self._notify_mode_change()
    
    def _execute_command(self) -> None:
        """Execute the command in the buffer."""
        if not self.command_buffer.strip():
            self._exit_command_mode()
            return
        
        command_text = self.command_buffer.strip()
        parts = command_text.split()
        command_name = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Add to history
        if command_text not in self.command_history:
            self.command_history.append(command_text)
        
        # Find and execute command
        if command_name in self.commands:
            try:
                command = self.commands[command_name]
                result = command.handler(*args) if args else command.handler()
                self._notify_command_executed(command_text, result)
            except Exception as e:
                self._notify_error(f"Error executing '{command_text}': {str(e)}")
        else:
            self._notify_error(f"Unknown command: '{command_name}'")
        
        self._exit_command_mode()
    
    def _cancel_command(self) -> None:
        """Cancel command input and return to normal mode."""
        self._exit_command_mode()
    
    def _navigate_history(self, direction: int) -> None:
        """Navigate through command history."""
        if not self.command_history:
            return
        
        new_index = self.history_index + direction
        
        if new_index < -1:
            new_index = len(self.command_history) - 1
        elif new_index >= len(self.command_history):
            new_index = -1
        
        self.history_index = new_index
        
        if self.history_index == -1:
            self.command_buffer = ""
        else:
            self.command_buffer = self.command_history[self.history_index]
        
        self._notify_buffer_change()
    
    def _notify_mode_change(self) -> None:
        """Notify about mode change."""
        if self.on_mode_change:
            self.on_mode_change(self.mode)
    
    def _notify_buffer_change(self) -> None:
        """Notify about command buffer change."""
        if self.on_command_buffer_change:
            self.on_command_buffer_change(self.command_buffer)
    
    def _notify_command_executed(self, command: str, result: Any) -> None:
        """Notify about command execution."""
        if self.on_command_executed:
            self.on_command_executed(command, result)
    
    def _notify_error(self, error: str) -> None:
        """Notify about an error."""
        if self.on_error:
            self.on_error(error)
        elif self.app and hasattr(self.app, 'notify'):
            self.app.notify(error)
    
    # Default command handlers
    def _quit_command(self) -> None:
        """Default quit command."""
        if self.app and hasattr(self.app, 'exit'):
            self.app.exit()
    
    def _help_command(self) -> str:
        """Default help command."""
        help_text = "Available commands:\n"
        unique_commands = {}
        
        # Get unique commands (filter out aliases)
        for name, command in self.commands.items():
            if command.name not in unique_commands:
                unique_commands[command.name] = command
        
        for command in unique_commands.values():
            aliases_str = f" ({', '.join(command.aliases)})" if command.aliases else ""
            help_text += f"  {command.name}{aliases_str} - {command.description}\n"
        
        return help_text
    
    def _clear_command(self) -> str:
        """Default clear history command."""
        self.command_history.clear()
        return "Command history cleared"
    
    def get_mode(self) -> KeyboardMode:
        """Get the current keyboard mode."""
        return self.mode
    
    def get_command_buffer(self) -> str:
        """Get the current command buffer."""
        return self.command_buffer
    
    def get_command_prompt(self) -> str:
        """Get the formatted command prompt for display."""
        if self.mode == KeyboardMode.COMMAND:
            return f":{self.command_buffer}"
        return ""
    
    def is_in_command_mode(self) -> bool:
        """Check if currently in command mode."""
        return self.mode == KeyboardMode.COMMAND