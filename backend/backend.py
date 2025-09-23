from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from .roomService import RoomService
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
import os
from passlib.context import CryptContext
'''
API for chat TUI using FastAPI, JWT, and SQLite

1. dbManager is a database management utility that simplifies interactions with SQLite.
2. FastAPI app handles HTTP requests and responses.
3. RoomService manages chat rooms and their participants.
4. LoginService manages user authentication and JWT issuance.
    - Passwords are hashed using bcrypt via passlib.
5. Responses are sent using JSON with status codes and messages.
'''

# app
app = FastAPI()

# JWT config

# You don;t need a .env, this isn't prod and is simply just for fun
SECRET_KEY = "SUPERSECRETKEY12345!"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
security = HTTPBearer()

# Password hashing context (recommended)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database manager (your module)
from . import dbManager

# Get the correct path to database.db (one level up from backend directory)
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.db")
db_manager = dbManager.DatabaseManager(db_path)
db_manager.create_connection()

global room_service # Room Service instance
room_service = RoomService(db_manager)


# Pydantic models
class AuthRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class RoomRequest(BaseModel):
    room_name: str

class MessageRequest(BaseModel):
    room_name: str
    message: str

# Utility: create jwt with int timestamps
def create_access_token(subject: str, expires_delta: timedelta = None):
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Verify token dependency: returns payload dict (so downstream deps can use claims)
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Resolve current user from token payload
def get_current_user(token_payload: dict = Depends(verify_token)):
    username = token_payload.get("sub")
    users = db_manager.fetch_all("SELECT * FROM users WHERE (username) = (?)", (token_payload.get("sub"),))
    if not users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    # adapt to your users table layout: e.g., (id, username, password_hash, ...)
    user_row = users[0]
    return {"id": user_row[0], "username": user_row[1]}

# Routes
@app.get("/")
async def root():
    return {"message": "Hello, FastAPI is working!"}

# this is how we create new users
# First we check if the password is long enough, we make sure the username is not taken, and then hash the password before storing
@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: AuthRequest):
    if len(data.password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 6 characters long")
    # check username exists
    existing = db_manager.fetch_all("SELECT id FROM users WHERE username = ?", (data.username,))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    hashed = pwd_context.hash(data.password)
    
    db_manager.execute_query("INSERT INTO users (username, password) VALUES (?, ?)", (data.username, hashed))
    return {"message": "User created"}

# Login route: verify password and return JWT
@app.post("/login", response_model=TokenResponse)
async def login(data: AuthRequest):
    users = db_manager.fetch_all("SELECT id, username, password FROM users WHERE username = ?", (data.username,))
    if not users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    user = users[0]
    user_id = user[0]     # id
    username = user[1]    # username  
    stored_hash = user[2] # password

    # Verify the password
    password_valid = pwd_context.verify(data.password, stored_hash)
    if not password_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=data.username, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Route to join a room (checks if room exists)
@app.post("/join_room")
async def join_room(data: RoomRequest, current_user: dict = Depends(get_current_user)):
    result = room_service.join_room(data.room_name)
    if result["success"]:
        return {"message": result["message"]}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["message"])

# Route to create a room, takes in a room name and a user then creates the room
@app.post("/create_room")
async def create_room(data: RoomRequest, current_user: dict = Depends(get_current_user)):
    result = room_service.create_room(data.room_name, current_user["id"])
    if result["success"]:
        return {"message": result["message"]}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])


# Route to send a message to a room
# Takes a room name and message, checks if the room exists, then stores the message with the user and room ids
@app.post("/send_message")
async def send_message(data: MessageRequest, current_user: dict = Depends(get_current_user)):
    room_id = room_service.get_room_id(data.room_name)
    if not room_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    
    db_manager.execute_query(
        "INSERT INTO messages (user_id, room_id, content) VALUES (?, ?, ?)",
        (current_user["id"], room_id, data.message)
    )
    return {"message": "Message sent successfully"}

@app.get("/get_messages/{room_name}")
async def get_messages(room_name: str, current_user: dict = Depends(get_current_user)):
    rooms = db_manager.fetch_all("SELECT id FROM rooms WHERE room_key = ?", (room_name,))
    if not rooms:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    room_id = rooms[0][0]
    messages = db_manager.fetch_all("SELECT content FROM messages WHERE room_id = ?", (room_id,))
    return {"messages": [msg[0] for msg in messages]}
