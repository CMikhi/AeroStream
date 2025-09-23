from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Header, Footer
from textual.containers import Horizontal, Vertical

class textApp(App):

    CSS_PATH = "cli.css"
    def compose(self) -> ComposeResult:

        yield Header()
        yield Static("Hello, world!")
        yield Input(placeholder="Type here...")
        yield Footer()

        yield Horizontal(
            Vertical(  # sidebar
                Static("Menu 1"),
                Static("Menu 2"),
                Static("Menu 3"),
                id="sidebar"
            ),
            Static("Main content here", id="main")
        )
if __name__ == "__main__":
    textApp().run()



