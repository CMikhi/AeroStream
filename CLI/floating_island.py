"""
Floating Command Line Island widget for the Ignite TUI application.

This module provides a floating command line interface that overlays the current page
without interfering with the main content. It supports active/inactive states and
visual feedback for command input.
"""

from textual.widgets import Static


class FloatingCommandLine(Static):
    """A floating command line island that overlays the current page without interfering."""
    
    def __init__(self, **kwargs):
        super().__init__("", **kwargs)
        self.is_active = False
        self.text_buffer = ""
        self._current_content = ""
        self.can_focus = True
    
    def set_active(self, active: bool):
        """Set the command line active state."""
        self.is_active = active
        if active:
            self.add_class("active")
            self.remove_class("hidden")
            # Auto-focus when activated
            self.call_after_refresh(self.focus)
        else:
            self.remove_class("active")
            self.add_class("hidden")
            self.text_buffer = ""
        self._update_content()
    
    def update_buffer(self, text: str):
        """Update the command line buffer text."""
        self.text_buffer = text
        self._update_content()
    
    def _update_content(self):
        """Update the widget content."""
        if self.is_active:
            # Add visual indicators for the floating island
            new_content = f"🏝️ :{self.text_buffer}█"
        else:
            new_content = ""
        
        # Only update if content has actually changed
        if new_content != self._current_content:
            self._current_content = new_content
            self.update(new_content)
            # Force a refresh to ensure visibility
            if self.app:
                self.app.refresh()
    
    def toggle_visibility(self):
        """Toggle the visibility of the command island."""
        self.set_active(not self.is_active)