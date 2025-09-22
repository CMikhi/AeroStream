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
    pass

@app.get("/login")
async def login():
    pass

# room routes
@app.get("/join_room")
async def join_room(data: RoomRequest):
    pass
      
@app.post("/create_room")
async def create_room(data: RoomRequest):
    pass

@app.post("/send_message")
async def send_message(data: MessageRequest):
    pass




