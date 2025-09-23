from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Header, Footer
from textual.containers import Horizontal, Vertical

class TextApp(App):

    CSS_PATH = "cli.css"

    def __init__(self):
        super().__init__()
        self.sidebar = None
        self.main_content = None
        self.chat_input = None
        self.username_input = None
        self.username_display = None
        self.username = "You"

    def compose(self) -> ComposeResult:
        yield Header()

        # Username input + display in the sidebar
        self.username_input = Input(placeholder="Enter username and press Enter...", id="username_input")
        self.username_display = Static(f"Username: {self.username}", id="username_display")

        # Sidebar
        self.sidebar = Vertical(
            self.username_display,
            self.username_input,
            Static("Menu 1"),
            Static("Menu 2"),
            Static("Menu 3"),
            id="sidebar"
        )

        # Main chat column with messages + input
        self.main_content = Vertical(id="main")
        self.chat_input = Input(placeholder="Type your message here...", id="chat_input")
        self.main_column = Vertical(
            self.main_content,
            self.chat_input,
        )

        # Horizontal container: sidebar + main column
        yield Horizontal(
            self.sidebar,
            self.main_column,
        )

        yield Footer()

    # Handle input submission
    def on_input_submitted(self, event: Input.Submitted) -> None:
        input_id = getattr(event.input, "id", None)
        value = event.value.strip()

        # Username input submitted
        if input_id == "username_input":
            if value:
                self.username = value
                if self.username_display:
                    self.username_display.update(f"Username: {self.username}")
            # Clear username input
            event.input.value = ""
            return

        # Chat input submitted
        if input_id == "chat_input" or input_id is None:
            if not value:
                return
            # Add message to main_content using the chosen username
            self.main_content.mount(Static(f"{self.username}: {value}"))
            # Clear chat input
            event.input.value = ""

if __name__ == "__main__":
    TextApp().run()