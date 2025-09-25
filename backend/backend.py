from fastapi import FastAPI
from pydantic import BaseModel
import threading
import dbManager

app = FastAPI()

global db_manager  # Database manager instance
db_manager = dbManager.DatabaseManager("database.db")
db_manager.create_connection()

# Request models
class AuthRequest(BaseModel):
    username: str

class RoomRequest(BaseModel):
    room_name: str
    
class MessageRequest(BaseModel):
    username: str
    room_name: str
    message: str

command_lock = threading.Lock()  # Prevent race conditions


# auth routes
@app.get("/")  # Define a route for "/"
async def root():
    return {"message": "Hello, FastAPI is working!"}

@app.post("/register")
async def register(data: AuthRequest):
    db_manager.execute_query("INSERT INTO users (username) VALUES (?)", (data.username,))

@app.get("/login")
async def login(data: AuthRequest):
    if any(user[1] == data.username for user in db_manager.fetch_all("SELECT * FROM users")):
        return {"message": "Login successful"}
    return {"message": "Invalid username"}

# room routes
@app.get("/join_room")
async def join_room(data: RoomRequest):
    if any(room[1] == data.room_name for room in db_manager.fetch_all("SELECT * FROM rooms")):
        return {"message": "Joined room successfully"}
    return {"message": "Room not found"}

@app.post("/create_room")
async def create_room(data: RoomRequest):
    db_manager.execute_query("INSERT INTO rooms (room_key, created_by) VALUES (?, ?)", (data.room_name, 1))

@app.post("/send_message")
async def send_message(data: MessageRequest):
    db_manager.execute_query("INSERT INTO messages (user_id, room_id, content) VALUES (?, ?, ?)", (1, 1, data.message))




