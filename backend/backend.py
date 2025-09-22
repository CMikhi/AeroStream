from fastapi import FastAPI
from pydantic import BaseModel
import threading

app = FastAPI()

class CommandRequest(BaseModel):
    command: str
    



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
async def register(data: CommandRequest):
    pass

@app.post("/create_room")
async def create_room(data: CommandRequest):
    pass

@app.post("/send_message")
async def send_message(data: CommandRequest):
    pass




