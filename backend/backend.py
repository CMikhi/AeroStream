from fastapi import FastAPI
from pydantic import BaseModel
import threading

app = FastAPI()

@app.get("/")  # Define a route for "/"
async def root():
    return {"message": "Hello, FastAPI is working!"}