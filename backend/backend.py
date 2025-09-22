from fastapi import FastAPI
from pydantic import BaseModel
import threading

app = FastAPI()

class AuthRequest(BaseModel):
    username: str

class RoomRequest(BaseModel):
    room_name: str
    
class MessageRequest(BaseModel):
    username: str
    room_name: str
    message: str

command_lock = threading.Lock()  # Prevent race conditions

@app.get("/")  # Define a route for "/"
async def root():
    return {"message": "Hello, FastAPI is working!"}

@app.get("/login")
async def login():
    pass

@app.get("/join_room")
async def join_room():
    pass
      
@app.post("/register")
async def register(data: AuthRequest):
    pass

@app.post("/create_room")
async def create_room(data: AuthRequest):
    pass

@app.post("/send_message")
async def send_message(data: MessageRequest):
    pass




