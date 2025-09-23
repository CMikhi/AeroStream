#!/usr/bin/env python3
"""
Debug script for decoding JWT tokens.
Usage: python script.py <token>
"""

from jose import jwt, JWTError
import sys, os

if len(sys.argv) < 2:
    print("Usage: python decode_token_debug.py <token>")
    sys.exit(1)

token = sys.argv[1].strip()

print("=== Unverified header ===")
try:
    print(jwt.get_unverified_header(token))
except Exception as e:
    print("Failed to read header:", e)

print("\n=== Unverified claims (no signature check) ===")
try:
    print(jwt.get_unverified_claims(token))
except Exception as e:
    print("Failed to read claims:", e)

# Try to verify if user provided SECRET_KEY env var
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    print("\nNo SECRET_KEY set in environment. To verify signature set SECRET_KEY env var to the same secret your app uses.")
else:
    print("\nAttempting verification using SECRET_KEY from environment...")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print("Verified payload:", payload)
    except Exception as e:
        print("Verification failed:", type(e).__name__, e)
