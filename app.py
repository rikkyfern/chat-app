# main.py (FastAPI)

from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from typing import Dict, List
import uvicorn
import json, os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS_DB = "data/users.json"
CHATS_DIR = "data/chats"
os.makedirs(CHATS_DIR, exist_ok=True)

active_connections: Dict[str, WebSocket] = {}

def load_users():
    if not os.path.exists(USERS_DB): return {}
    with open(USERS_DB, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_DB, "w") as f:
        json.dump(users, f, indent=2)

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(password, hashed):
    return pwd_context.verify(password, hashed)

def chat_filename(user1, user2):
    return os.path.join(CHATS_DIR, f"{min(user1, user2)}__{max(user1, user2)}.json")

def load_chat(user1, user2):
    path = chat_filename(user1, user2)
    if not os.path.exists(path): return []
    with open(path, "r") as f:
        return json.load(f)

def save_chat(user1, user2, messages):
    path = chat_filename(user1, user2)
    with open(path, "w") as f:
        json.dump(messages, f, indent=2)

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    users = load_users()
    if username in users and verify_password(password, users[username]):
        response = RedirectResponse(url="/chat", status_code=302)
        response.set_cookie("username", username)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Login gagal"})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...)):
    users = load_users()
    if username in users:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username sudah ada"})
    users[username] = get_password_hash(password)
    save_users(users)
    return RedirectResponse(url="/", status_code=302)

@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse(url="/", status_code=302)
    users = load_users()
    target_users = [u for u in users if u != username]
    return templates.TemplateResponse("chat.html", {"request": request, "name": username, "users": target_users})

@app.websocket("/ws/{receiver}")
async def websocket_endpoint(websocket: WebSocket, receiver: str):
    sender = websocket.cookies.get("username")
    await websocket.accept()
    key = f"{sender}__{receiver}"
    active_connections[key] = websocket

    chat_history = load_chat(sender, receiver)
    for msg in chat_history:
        await websocket.send_text(f"[{msg['sender']}] {msg['text']}")

    try:
        while True:
            data = await websocket.receive_text()
            message = {"sender": sender, "text": data}
            chat_history.append(message)
            save_chat(sender, receiver, chat_history)
            formatted = f"[{sender}] {data}"

            await websocket.send_text(formatted)
            key_rev = f"{receiver}__{sender}"
            if key_rev in active_connections:
                await active_connections[key_rev].send_text(formatted)
    except WebSocketDisconnect:
        del active_connections[key]

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
