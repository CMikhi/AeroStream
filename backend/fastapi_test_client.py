#!/usr/bin/env python3
"""
Sequential test runner for a FastAPI app.
Requires: pip install requests
"""

import json
import os
from pathlib import Path
import requests
from typing import Optional

TOKEN_PATH = Path.home() / ".fastapi_test_token"

def save_token(token: str, path: Path = TOKEN_PATH):
    path.write_text(token)

def load_token(path: Path = TOKEN_PATH) -> Optional[str]:
    if path.exists():
        return path.read_text().strip()
    return None

def clear_token(path: Path = TOKEN_PATH):
    if path.exists():
        path.unlink()

def make_headers(token: Optional[str] = None):
    h = {"Accept": "application/json", "Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

def post(url: str, path: str, json_body: Optional[dict] = None, token: Optional[str] = None) -> requests.Response:
    full = url.rstrip("/") + "/" + path.lstrip("/")
    return requests.post(full, json=json_body, headers=make_headers(token))

def get(url: str, path: str = "", token: Optional[str] = None) -> requests.Response:
    full = url.rstrip("/") + ("/" + path.lstrip("/") if path else "")
    return requests.get(full, headers=make_headers(token))

def pretty_print_response(resp: requests.Response) -> bool:
    try:
        data = resp.json()
        print(json.dumps(data, indent=2))
    except ValueError:
        print(resp.text)
    return resp.status_code == 200 or resp.status_code == 201

def run_test(description: str, func, *args, **kwargs):
    print(f"\nRunning test: {description}")
    try:
        response = func(*args, **kwargs)
        if pretty_print_response(response):
            print(f"Test '{description}' PASSED")
        else:
            print(f"Test '{description}' FAILED")
    except Exception as e:
        print(f"Test '{description}' FAILED with error: {e}")

def main():
    base_url = "http://localhost:8000"

    # Test 1: Root endpoint
    run_test("GET /", get, base_url)

    # Test 2: Register a new user
    username = "bob"
    password = "hunter2"
    run_test("POST /register", post, base_url, "register", json_body={"username": username, "password": password})

    # Test 3: Login and save token
    run_test("POST /login", post, base_url, "login", json_body={"username": username, "password": password})
    token_response = post(base_url, "login", json_body={"username": username, "password": password})
    if token_response.status_code == 200:
        token = token_response.json().get("access_token")
        if token:
            save_token(token)
        else:
            print("Login test failed: No token received.")
            return
    else:
        print("Login test failed.")
        return

    # Test 4: Create a room
    room_name = "myroom"
    token = load_token()
    run_test("POST /create_room", post, base_url, "create_room", json_body={"room_name": room_name}, token=token)

    # Test 5: Join the room
    run_test("POST /join_room", post, base_url, "join_room", json_body={"room_name": room_name}, token=token)

    # Test 6: Send a message
    message = "hello"
    run_test("POST /send_message", post, base_url, "send_message", json_body={"room_name": room_name, "message": message}, token=token)

    # Cleanup: Clear token
    clear_token()
    print("\nAll tests completed.")

if __name__ == "__main__":
    main()
