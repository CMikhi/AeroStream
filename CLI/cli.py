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
                Static("Chat 1"),
                Static("Chat 2"),
                Static("Chat 3"),
                id="sidebar"
            ),
            Static("Main content here", id="main")
        )
if __name__ == "__main__":
    textApp().run()



# Importing necessary modules
import sys
from textual.app import App
from textual.widgets import Header, Footer, Button, Input, Static

# Variables for username and room name (camelCase)
userName: str = ""
roomName: str = ""
text: str = ""                  

# Main function to start the program
def main():
    login()

# Function to handle user login
def login() -> None:
    print("WELCOME!")
    print("--------")
    getUserName()
    createRoom()

# Function to get the username from the user
def getUserName() -> str:
    userName = input("Type your username: ")
    return userName

# Function to create a chat room
def createRoom() -> None:
    roomActive = True
    print("ROOM")
    print("----")
    while roomActive:
        roomName = input("Type your room name: ")
        if roomName:
            print(f"Room '{roomName}' created successfully!")
            chatRoom()
            roomActive = False
        else:
            print("Room name cannot be empty. Please try again.")
        print(f"{userName}: {text}")
        if text.lower() == "exit":
            roomActive = False

def chatRoom() -> None:
    print("CHAT ROOM")
    print("---------")
    print(f"Welcome to the chat room, {userName}!")
    print(f"Room Name: {roomName}")
    print()
    print("Type 'exit' to leave the chat room.")
    print()
    while True:
        print()
        text = input(f"{userName}: ")
        print()
        if text.lower() == "exit":
            print("Exiting chat room...")
            break
        print(f"{userName}: {text}")

# Entry point for the script
if __name__ == "__main__":
    main()

