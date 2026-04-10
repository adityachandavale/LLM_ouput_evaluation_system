import hashlib
import json
import os


USERS_PATH = "data/users.json"


def _ensure_user_store():
    os.makedirs(os.path.dirname(USERS_PATH), exist_ok=True)
    if not os.path.exists(USERS_PATH):
        with open(USERS_PATH, "w", encoding="utf-8") as file:
            json.dump({}, file)


def _load_users():
    _ensure_user_store()
    with open(USERS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def _save_users(users):
    with open(USERS_PATH, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=2)


def _hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register_user(username, password):
    username = username.strip()
    if not username or not password:
        return False, "Username and password are required."

    users = _load_users()
    if username in users:
        return False, "That username already exists. Please log in instead."

    users[username] = {"password_hash": _hash_password(password)}
    _save_users(users)
    return True, "Account created successfully. Please log in."


def authenticate_user(username, password):
    username = username.strip()
    if not username or not password:
        return False, "Username and password are required."

    users = _load_users()
    user = users.get(username)
    if not user:
        return False, "User not found. Please sign up first."

    if user["password_hash"] != _hash_password(password):
        return False, "Incorrect password."

    return True, "Login successful."
