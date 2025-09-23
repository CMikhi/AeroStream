#!/usr/bin/env python3
"""
Simple CLI test client for a FastAPI app.
Requires: pip install requests
Usage examples:
  python backend/fastapi_test_client.py --url http://localhost:8000 root
  python backend/fastapi_test_client.py --url http://localhost:8000 register --username bob --password hunter2
  python backend/fastapi_test_client.py --url http://localhost:8000 login --username bob --password hunter2 --save
  python backend/fastapi_test_client.py --url http://localhost:8000 create_room --room myroom
  python backend/fastapi_test_client.py --url http://localhost:8000 join_room --room myroom
  python backend/fastapi_test_client.py --url http://localhost:8000 send_message --room myroom --message "hello"
"""

import argparse
import json
import os
from pathlib import Path
import requests
from typing import Optional, Tuple

TOKEN_PATH = Path.home() / ".fastapi_test_token"

def save_token(token: str, path: Path = TOKEN_PATH):
    path.write_text(token)
    print(f"Saved token to {path}")

def load_token(path: Path = TOKEN_PATH) -> Optional[str]:
    if path.exists():
        return path.read_text().strip()
    return None

def clear_token(path: Path = TOKEN_PATH):
    if path.exists():
        path.unlink()
        print(f"Cleared token file {path}")

def pretty_print_response(resp: requests.Response):
    print(f"\nHTTP {resp.status_code} {resp.reason}")
    try:
        data = resp.json()
        print(json.dumps(data, indent=2))
    except ValueError:
        print(resp.text)

def make_headers(token: Optional[str] = None):
    h = {"Accept": "application/json", "Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

def post(url: str, path: str, json_body: dict = None, token: Optional[str] = None) -> requests.Response:
    full = url.rstrip("/") + "/" + path.lstrip("/")
    return requests.post(full, json=json_body, headers=make_headers(token))

def get(url: str, path: str = "", token: Optional[str] = None) -> requests.Response:
    full = url.rstrip("/") + ("/" + path.lstrip("/") if path else "")
    return requests.get(full, headers=make_headers(token))

def cmd_root(base_url: str):
    r = get(base_url, "")
    pretty_print_response(r)

def cmd_register(base_url: str, username: str, password: str):
    body = {"username": username, "password": password}
    r = post(base_url, "register", json_body=body)
    pretty_print_response(r)

def cmd_login(base_url: str, username: str, password: str, save: bool):
    body = {"username": username, "password": password}
    r = post(base_url, "login", json_body=body)
    pretty_print_response(r)
    if r.status_code == 200:
        try:
            token = r.json().get("access_token")
            if token:
                if save:
                    save_token(token)
                else:
                    print("\nToken (not saved):", token)
            else:
                print("No access_token found in response.")
        except ValueError:
            pass

def cmd_create_room(base_url: str, room_name: str, token: Optional[str]):
    body = {"room_name": room_name}
    r = post(base_url, "create_room", json_body=body, token=token)
    pretty_print_response(r)

def cmd_join_room(base_url: str, room_name: str, token: Optional[str]):
    body = {"room_name": room_name}
    # your API uses POST /join_room (per recommended change)
    r = post(base_url, "join_room", json_body=body, token=token)
    pretty_print_response(r)

def cmd_send_message(base_url: str, room_name: str, message: str, token: Optional[str]):
    body = {"room_name": room_name, "message": message}
    r = post(base_url, "send_message", json_body=body, token=token)
    pretty_print_response(r)

def cmd_clear_token():
    clear_token()

def parse_args():
    parser = argparse.ArgumentParser(description="FastAPI test client")
    parser.add_argument("--url", "-u", default="http://localhost:8000", help="Base URL of the FastAPI server")
    parser.add_argument("--token-file", "-t", default=str(TOKEN_PATH), help="Token file path")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("root", help="GET /")

    reg = sub.add_parser("register", help="Register a new user")
    reg.add_argument("--username", required=True)
    reg.add_argument("--password", required=True)

    log = sub.add_parser("login", help="Login and optionally save token")
    log.add_argument("--username", required=True)
    log.add_argument("--password", required=True)
    log.add_argument("--save", action="store_true", help="Save token to token file")

    cr = sub.add_parser("create_room", help="Create a room (auth required)")
    cr.add_argument("--room", required=True)

    jr = sub.add_parser("join_room", help="Join a room (auth required)")
    jr.add_argument("--room", required=True)

    sm = sub.add_parser("send_message", help="Send a message to a room (auth required)")
    sm.add_argument("--room", required=True)
    sm.add_argument("--message", required=True)

    sub.add_parser("clear_token", help="Delete saved token file")

    return parser.parse_args()

def main():
    args = parse_args()
    token_path = Path(args.token_file)
    global TOKEN_PATH
    TOKEN_PATH = token_path

    token = load_token(token_path)

    if args.command == "root":
        cmd_root(args.url)
        return

    if args.command == "register":
        cmd_register(args.url, args.username, args.password)
        return

    if args.command == "login":
        cmd_login(args.url, args.username, args.password, save=args.save)
        return

    if args.command == "create_room":
        if not token:
            print("No token found. Please login first (use --save to save token).")
            return
        cmd_create_room(args.url, args.room, token)
        return

    if args.command == "join_room":
        if not token:
            print("No token found. Please login first (use --save to save token).")
            return
        cmd_join_room(args.url, args.room, token)
        return

    if args.command == "send_message":
        if not token:
            print("No token found. Please login first (use --save to save token).")
            return
        cmd_send_message(args.url, args.room, args.message, token)
        return

    if args.command == "clear_token":
        cmd_clear_token()
        return

if __name__ == "__main__":
    main()
