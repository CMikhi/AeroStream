import json
import os
from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Header, Footer, Button
from textual.containers import Horizontal, Vertical, Center
from textual.screen import Screen, ModalScreen
from textual.message import Message

ROOMS_FILE = "rooms_data.json"

"""Create New room"""
class CreateRoomModal(ModalScreen):
    

    def compose(self) -> ComposeResult:
        yield Center(
            Vertical(
                Static("Create New Room"),
                Input(placeholder="Room Name", id="room-name-input"),
                Horizontal(
                    Button("Public", variant="primary"),
                    Button("Private", variant="default"),
                    Button("Cancel"),
                ),
            )
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.label == "Cancel":
            self.dismiss()
        elif event.button.label in ["Public", "Private"]:
            room_name = self.query_one("#room-name-input").value
            if room_name:
                is_public = event.button.label == "Public"
                self.dismiss((room_name, is_public))        


"""Selectable room"""
class ClickableRoom(Static):
    """A clickable room label that can be selected."""
    
    class Clicked(Message):
        """Message sent when the room is clicked."""
        def __init__(self, room_name: str) -> None:
            self.room_name = room_name
            super().__init__()
    
    def __init__(self, room_name: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.room_name = room_name
    
    def on_click(self) -> None:
        """Send a message when the room is clicked."""
        self.post_message(self.Clicked(self.room_name))




""""JSON file handling"""
def load_rooms_data():
    if os.path.exists(ROOMS_FILE):
        try:
            with open(ROOMS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_rooms_data(rooms_data):
    with open(ROOMS_FILE, 'w') as f:
        json.dump(rooms_data, f, indent=4)


""""Username input screen"""
class UsernameScreen(Screen):
    def compose(self) -> ComposeResult:
        self.username_input = Input(id="username_input")

        #verts/horiz act like divs
        yield Vertical(
            Static("Enter your username:", id="username_prompt"),
            self.username_input,
            Button("Next", id="next_button"),
            id="username_container"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "next_button":
            username = self.username_input.value
            self.app.push_screen(WelcomeScreen(username))


class WelcomeScreen(Screen):
    BINDINGS = [
        ("m", "focus_message_box", "Focus Message Box"),
        ("up", "previous_room", "Previous Room"),
        ("down", "next_room", "Next Room"),
    ]
    
    def __init__(self, username: str = "You"):
        super().__init__()
        self.roomBar = None
        self.room_list = []  # Store list of room names for navigation
        self.usersBar = None
        self.main_content = None
        self.chat_input = None
        self.username_input = None
        self.username_display = None
        self.username = username
        self.room_counter = 0
        

        # Load rooms from JSON file or create default rooms if file doesn't exist
        self.rooms = load_rooms_data()
        if not self.rooms:
            self.rooms = {
                "General": {"users": [username], "messages": []},
                "Random": {"users": [], "messages": []},
                "Help": {"users": [], "messages": []}
            }
            save_rooms_data(self.rooms)

        # Re-add user to all their previous rooms and ensure they're in General
        need_save = False
        for room_name, room_data in self.rooms.items():
            # If user was in this room before, add them back
            if username in room_data["messages"]:  # Check if user has sent messages in this room
                if username not in room_data["users"]:
                    room_data["users"].append(username)
                    need_save = True
            # Always ensure user is in General room
            elif room_name == "General" and username not in room_data["users"]:
                room_data["users"].append(username)
                need_save = True
        
        if need_save:
            save_rooms_data(self.rooms)

        self.current_room = "General"  # Start in General room
        self.users = self.rooms[self.current_room]["users"]  # Reference to current room's users



    def compose(self) -> ComposeResult:
        # roomBar (dynamic room list)
        self.roomBar = Vertical(id="roomBar")
        
        # Main chat column with messages + input
        self.main_content = Vertical(id="main")
        self.chat_input = Input(placeholder=f"Message #{self.current_room}...", id="chat_input")
        self.main_column = Vertical(
            self.main_content,
            self.chat_input,
        )

        
        # usersBar (dynamic user list)
        self.usersBar = Vertical(id="usersBar")

        # Horizontal container: roomBar + main column + usersBar
        yield Horizontal(
            self.roomBar,
            self.main_column,
            self.usersBar,
        )

        yield Footer()

    def _refresh_user_list(self) -> None:
        """Update the users bar with current users."""
        # Clear existing users
        self.usersBar.remove_children()
        
        # Add header with icon and count
        self.usersBar.mount(Static(f"󰀄 Users ({len(self.users)})", classes="users-header"))
        
        # Add each user with an icon
        for idx, user in enumerate(sorted(self.users)):
            is_self = user == self.username
            icon = "󰋗" if is_self else "󰀄"  # Different icon for current user
            style = "user-self" if is_self else "user-other"
            # Make user IDs unique by including room name and username
            safe_user = user.lower().replace(" ", "_")
            safe_room = self.current_room.lower().replace(" ", "_")
            user_id = f"user-{safe_room}-{safe_user}"
            self.usersBar.mount(Static(f"{icon} {user}", id=user_id, classes=style))

    def add_user(self, username: str) -> None:
        """Add a user to the room and update the display."""
        if username not in self.users:
            self.users.append(username)
            self._refresh_user_list()

            # Notify in chat
            self.main_content.mount(Static(f"→ {username} joined the room", id="system-message"))

    def remove_user(self, username: str) -> None:
        """Remove a user from the room and update the display."""
        if username in self.users:
            self.users.remove(username)
            self._refresh_user_list()
            # Notify in chat
            self.main_content.mount(Static(f"← {username} left the room", id="system-message"))
            
    def _refresh_room_list(self) -> None:
        """Update the room bar with current rooms."""
        self.roomBar.remove_children()
        
        # Add header with icon
        self.roomBar.mount(Static("󰋜 Rooms", classes="rooms-header"))
        
        # Update room list for navigation
        self.room_list = sorted(self.rooms.keys())
        
        # Add each room with an icon and unread count
        for room_name in self.room_list:
            is_current = room_name == self.current_room
            icon = "󰭷" if is_current else "󰋜"
            unread = len(self.rooms[room_name]["messages"])
            unread_badge = f" ({unread})" if unread > 0 else ""
            
            style = "room-current" if is_current else "room-other"
            self.room_counter += 1
            # Create a valid ID by replacing spaces with underscores
            safe_room_name = room_name.lower().replace(" ", "_")
            room_id = f"room-{safe_room_name}-{self.room_counter}"
            
            room_text = f"{icon} {room_name}{unread_badge}"
            clickable_room = ClickableRoom(
                room_name,
                room_text,
                id=room_id,
                classes=style
            )
            self.roomBar.mount(clickable_room)
        
        # Add New Room button at bottom
        new_room_button = ClickableRoom(
            "new_room",
            "󰐕 New Room",
            classes="room-action"
        )
        self.roomBar.mount(new_room_button)

    def switch_room(self, room_name: str) -> None:
        """Switch to a different room."""
        if room_name in self.rooms and room_name != self.current_room:
            # Store current room's users and messages
            self.rooms[self.current_room]["users"] = self.users
            
            # Switch rooms
            self.current_room = room_name
            self.users = self.rooms[room_name]["users"]
            
            # Clear and update display
            self.main_content.remove_children()
            # Get only the 40 most recent messages
            messages = self.rooms[room_name]["messages"]
            recent_messages = messages[-40:] if len(messages) > 40 else messages
            for msg in recent_messages:
                self.main_content.mount(Static(msg))
            
            # Update user and room lists
            self._refresh_user_list()
            self._refresh_room_list()
            
            # Update input placeholder
            self.chat_input.placeholder = f"Message #{room_name}..."

    # def add_room(self, room_name: str) -> None:
    #     """Add a new room."""
    #     if room_name not in self.rooms:
    #         self.rooms[room_name] = {"users": [], "messages": []}
    #         save_rooms_data(self.rooms)
    #         self._refresh_room_list()
    #         # Show success message in current room
    #         self.main_content.mount(
    #             Static(f"→ Room #{room_name} created", id="system-message")
    #         )



    def on_clickable_room_clicked(self, event: ClickableRoom.Clicked) -> None:
        """Handle room clicks for room switching and new room creation."""
        if event.room_name == "new_room":
            # Show the create room modal
            self.app.push_screen(CreateRoomModal(), callback=self.handle_room_creation)
        else:
            self.switch_room(event.room_name)
            
    def handle_room_creation(self, result) -> None:
        """Handle the result from the room creation modal."""
        if result is not None:
            room_name, is_public = result
            if room_name not in self.rooms:
                # Create the new room with appropriate visibility
                self.rooms[room_name] = {
                    "users": [self.username],
                    "messages": [],
                    "is_public": is_public
                }
                save_rooms_data(self.rooms)
                self._refresh_room_list()
                # Show success message in current room
                self.main_content.mount(
                    Static(f"→ Room #{room_name} created ({'public' if is_public else 'private'})", 
                          id="system-message")
                )

    def on_mount(self) -> None:
        """Called when screen is mounted, initialize lists."""
        self.app.call_after_refresh(self._refresh_room_list)  # Initialize rooms first
        self.app.call_after_refresh(self._refresh_user_list)  # Then users
        
        # Mount initial room messages (most recent 40)
        messages = self.rooms[self.current_room]["messages"]
        recent_messages = messages[-40:] if len(messages) > 40 else messages
        for msg in recent_messages:
            self.main_content.mount(Static(msg))



    # Handle input submission
    def on_input_submitted(self, event: Input.Submitted) -> None:
        input_id = getattr(event.input, "id", None)
        value = event.value.strip()

        # Chat input submitted
        if input_id == "chat_input" or input_id is None:
            if not value:
                return

            message = f"{self.username}: {value}"
            
            self.rooms[self.current_room]["messages"].append(message)
            save_rooms_data(self.rooms)
            
            # Clear and show the most recent 40 messages
            self.main_content.remove_children()
            messages = self.rooms[self.current_room]["messages"]
            recent_messages = messages[-40:] if len(messages) > 40 else messages
            for msg in recent_messages:
                self.main_content.mount(Static(msg))
            
            event.input.value = ""
            
            self._refresh_room_list()

    def action_focus_message_box(self) -> None:
        """Action to focus the message input box when 'm' is pressed."""
        self.chat_input.focus()

    def action_previous_room(self) -> None:
        """Navigate to the previous room in the list."""
        if not self.room_list:
            return
            
        current_index = self.room_list.index(self.current_room)
        new_index = (current_index - 1) % len(self.room_list)
        self.switch_room(self.room_list[new_index])

    def action_next_room(self) -> None:
        """Navigate to the next room in the list."""
        if not self.room_list:
            return
            
        current_index = self.room_list.index(self.current_room)
        new_index = (current_index + 1) % len(self.room_list)
        self.switch_room(self.room_list[new_index])


class TextApp(App):
    CSS_PATH = "roomPage.css"

    def on_mount(self):
        self.push_screen(UsernameScreen())


if __name__ == "__main__":
    TextApp().run()
