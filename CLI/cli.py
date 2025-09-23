#!/usr/bin/env python3
"""
CLI interface for the IgniteDemoRepo chat application.
This is a placeholder implementation that would connect to the FastAPI backend.
"""

from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Header, Footer
from textual.containers import Horizontal, Vertical

__all__ = ["ChatApp"]


class ChatApp(App):
    """A Textual app for the chat interface."""
    
    CSS_PATH = "cli.css"  # Optional CSS file for styling
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Static("Welcome to IgniteDemo Chat!", id="welcome")
        
        yield Horizontal(
            Vertical(  # sidebar
                Static("Available Rooms:", classes="sidebar-title"),
                Static("• General", classes="room-item"),
                Static("• Tech Talk", classes="room-item"),
                Static("• Random", classes="room-item"),
                id="sidebar"
            ),
            Vertical(  # main chat area
                Static("Select a room to start chatting", id="chat-display"),
                Input(placeholder="Type your message here...", id="message-input"),
                id="main"
            )
        )
        yield Footer()

    def on_mount(self) -> None:
        """Called when app starts."""
        self.title = "IgniteDemo Chat"
        self.sub_title = "Terminal-based messaging"


def main() -> None:
    """Entry point for the CLI application."""
    app = ChatApp()
    app.run()


if __name__ == "__main__":
    main()
