"""
Floating Command Line Island widget for the Ignite TUI application.

This module provides a floating command line interface that overlays the current page
without interfering with the main content. It supports active/inactive states and
visual feedback for command input. It also includes a result panel that displays
command output underneath the command line.
"""

from textual.widgets import Static
from textual.containers import Vertical


class FloatingResultPanel(Static):
    """A result panel that displays command output underneath the command line."""
    
    def __init__(self, **kwargs):
        super().__init__("", **kwargs)
        self.is_visible = False
        self.current_result = ""
        self.result_type = "info"  # "info", "error", "success"
    
    def show_result(self, text: str, result_type: str = "info", duration: float = 0.0):
        """Show a result with specified type. Results persist until manually dismissed."""
        self.current_result = text
        self.result_type = result_type
        self.is_visible = True
        
        # Update styling based on result type
        self.remove_class("result-info")
        self.remove_class("result-error") 
        self.remove_class("result-success")
        self.remove_class("hidden")
        
        self.add_class(f"result-{result_type}")
        self._update_content()
        
        # No longer auto-hide - results persist until manually dismissed
        # Only auto-hide if specifically requested with duration > 0
        if duration > 0:
            self.set_timer(duration, self.hide_result)
    
    def hide_result(self):
        """Hide the result panel."""
        self.is_visible = False
        self.add_class("hidden")
        self.current_result = ""
        self._update_content()
    
    def _update_content(self):
        """Update the result panel content."""
        if self.is_visible and self.current_result:
            # Format the result with appropriate icons
            icon = "💬" if self.result_type == "info" else "❌" if self.result_type == "error" else "✅"
            content = f"{icon} {self.current_result}"
        else:
            content = ""
        
        self.update(content)
        if self.app:
            self.app.refresh()


class FloatingCommandLine(Static):
    """A floating command line island that overlays the current page without interfering."""
    
    def __init__(self, **kwargs):
        super().__init__("", **kwargs)
        self.is_active = False
        self.text_buffer = ""
        self._current_content = ""
        self.can_focus = True
        self.result_panel = None  # Will be set by parent when both widgets are composed
    
    def set_result_panel(self, result_panel: FloatingResultPanel):
        """Set the associated result panel."""
        self.result_panel = result_panel
    
    def show_result(self, text: str, result_type: str = "info", duration: float = 0.0):
        """Show a result in the associated result panel. Results persist until manually dismissed."""
        if self.result_panel:
            self.result_panel.show_result(text, result_type, duration)
    
    def hide_result(self):
        """Hide the result panel."""
        if self.result_panel:
            self.result_panel.hide_result()
    
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
            new_content = f":{self.text_buffer}█"
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