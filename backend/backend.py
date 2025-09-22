from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from roomService import RoomService
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
import os
from passlib.context import CryptContext

'''


This is a simple chat backend using FastAPI, JWT for authentication, and SQLite for storage.
I'll explain how the flow of this backend works:

1. dbManager, essentially just a thin wrapper around sqlite3 with per-op connections and some convenience methods.
   This allows for it to handle the threading, locking, and connection management for you. It also handles the creation
   of the database file if it doesn't exist.

2. FastAPI app with routes for user registration, login, room creation/joining, and message sending.
   - Registration hashes passwords before storing them.
   - Login verifies passwords and issues JWTs.
   - Protected routes require a valid JWT, verified via a dependency.
   - Rooms and messages are stored in the database with appropriate foreign keys.
   
   What is JWT? 
    JSON Web Tokens (JWT) are a compact, URL-safe means of representing claims to be transferred between two parties.
    They are commonly used for authentication and information exchange in web applications. It ensures that user data
    like raw passwords is not easily intercepted or misused. It also ensures that the users are who they say they are.
    They are created by using a secret key (the one above), and then verified using the same key. Normally you would use
    a .env and a very secure key, but this is just for demo purposes.

3. Passwords are hashed using bcrypt via passlib, which is a secure way to store passwords.
   We never store plain text passwords as that's bad practice.
   
4. We send all information as JSON over HTTP, which is standard for RESTful APIs.


'''

# app
app = FastAPI()

# JWT config

# You don;t need a .env, this isn't prod and is simply just for fun
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    # in dev this is okay, but in production fail fast so people don't run with a bad secret
    SECRET_KEY = "SUPERSECRETKEY12345!" # W
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
security = HTTPBearer()

# Password hashing context (recommended)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database manager (your module)
from . import dbManager
db_manager = dbManager.DatabaseManager("database.db")
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
    users = db_manager.fetch_all("SELECT * FROM users WHERE username = ?", (data.username,))
    if not users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    user = users[0]
    stored_hash = user[2]  # adapt index if your schema differs
    if not pwd_context.verify(data.password, stored_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=data.username, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Route to join a room (checks if room exists)
@app.post("/join_room")
async def join_room(data: RoomRequest, current_user: dict = Depends(get_current_user)):
    rooms = db_manager.fetch_all("SELECT * FROM rooms WHERE room_key = ?", (data.room_name,))
    if rooms:
        return {"message": "Joined room successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

# Route to create a room, takes in a room name and a user then creates the room
@app.post("/create_room")
async def create_room(data: RoomRequest, current_user: dict = Depends(get_current_user)):
    db_manager.execute_query("INSERT INTO rooms (room_key, created_by) VALUES (?, ?)", (data.room_name, current_user["id"]))
    return {"message": "Room created successfully"}


# Route to send a message to a room
# Takes a room name and message, checks if the room exists, then stores the message with the user and room ids
@app.post("/send_message")
async def send_message(data: MessageRequest, current_user: dict = Depends(get_current_user)):
    rooms = db_manager.fetch_all("SELECT id FROM rooms WHERE room_key = ?", (data.room_name,))
    if not rooms:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    room_id = rooms[0][0]
    db_manager.execute_query("INSERT INTO messages (user_id, room_id, content) VALUES (?, ?, ?)",
                             (current_user["id"], room_id, data.message))
    return {"message": "Message sent successfully"}
