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

    def compose(self) -> ComposeResult:
        yield Header()

        # Sidebar
        self.sidebar = Vertical(
            Static("Menu 1"),
            Static("Menu 2"),
            Static("Menu 3"),
            id="sidebar"
        )

        # Main chat column with messages + input
        self.main_content = Vertical(id="main")
        self.chat_input = Input(placeholder="Type your message here...")
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
        message = event.value.strip()
        if not message:
            return

        # Add message to main_content
        self.main_content.mount(Static(f"You: {message}"))

        # Clear input box
        event.input.value = ""

if __name__ == "__main__":
    TextApp().run()