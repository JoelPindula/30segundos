"""
30 Segundos v3.1 - Servidor Principal
"""

import os
import socketio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.api.routes import router
from backend.api.socket_events import register_socket_events

# Cria app FastAPI
app = FastAPI(title="30 Segundos", version="3.1")

# Cria Socket.IO
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

# Registra eventos do Socket.IO
register_socket_events(sio)

# Registra rotas da API
app.include_router(router, prefix="/api")

# Caminho para os arquivos estáticos
FRONTEND_DIR = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), "frontend", "src")

# Monta arquivos estáticos (CSS, JS)
if os.path.exists(os.path.join(FRONTEND_DIR, "css")):
    app.mount(
        "/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")

if os.path.exists(os.path.join(FRONTEND_DIR, "js")):
    app.mount(
        "/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")


@app.get("/")
async def home():
    """Página inicial"""
    file_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "index.html não encontrado", "path": file_path}


@app.get("/admin")
async def admin():
    """Página de administração"""
    file_path = os.path.join(FRONTEND_DIR, "admin.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "admin.html não encontrado", "path": file_path}


@app.get("/board")
async def board():
    """Página do tabuleiro (TV)"""
    file_path = os.path.join(FRONTEND_DIR, "board.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "board.html não encontrado", "path": file_path}


@app.get("/player")
async def player():
    """Página do jogador (celular)"""
    file_path = os.path.join(FRONTEND_DIR, "player.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "player.html não encontrado", "path": file_path}


# Exporta o app com Socket.IO
app_with_socket = socket_app
