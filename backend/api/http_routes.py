"""Rotas HTTP da API"""

import os
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# Caminho do frontend
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
FRONTEND_PATH = os.path.join(PROJECT_ROOT, 'frontend', 'src')


# ============================================
# MODELOS DE REQUEST
# ============================================

class CreateGameRequest(BaseModel):
    name: str = "Partida 30 Segundos"
    team1_name: str = "Time Amarelo"
    team1_color: str = "#f1c40f"
    team1_players: List[str] = ["Jogador 1"]
    team2_name: str = "Time Azul"
    team2_color: str = "#3498db"
    team2_players: List[str] = ["Jogador 1"]
    themes: List[str] = ["geral"]
    levels: List[int] = [1, 2]
    round_time: int = 30
    words_per_side: int = 5
    challenge_frequency: int = 3


# ============================================
# ROTAS DE CONFIGURAÇÃO
# ============================================

@router.get("/api/config/themes")
async def get_themes():
    """Retorna temas disponíveis"""
    from backend.services.word_service import word_service
    themes = word_service.get_available_themes()
    return themes


@router.get("/api/config/levels")
async def get_levels():
    """Retorna níveis disponíveis"""
    from backend.services.word_service import word_service
    levels = word_service.get_levels()
    return levels


# ============================================
# ROTAS DE JOGOS
# ============================================

@router.get("/api/games")
async def list_games():
    """Lista todas as partidas"""
    from backend.services.game_service import game_service
    games = game_service.get_all_games()
    return [g.to_dict() for g in games]


@router.post("/api/games")
async def create_game(request: CreateGameRequest):
    """Cria uma nova partida"""
    from backend.services.game_service import game_service

    game = game_service.create_game(
        name=request.name,
        team1_name=request.team1_name,
        team1_color=request.team1_color,
        team1_players=request.team1_players,
        team2_name=request.team2_name,
        team2_color=request.team2_color,
        team2_players=request.team2_players,
        config={
            'themes': request.themes,
            'levels': request.levels,
            'round_time': request.round_time,
            'words_per_side': request.words_per_side,
            'challenge_frequency': request.challenge_frequency
        }
    )

    return game.to_dict()


@router.get("/api/games/{game_id}")
async def get_game(game_id: str):
    """Obtém dados de uma partida"""
    from backend.services.game_service import game_service

    game = game_service.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    return game.to_dict()


@router.delete("/api/games/{game_id}")
async def delete_game(game_id: str):
    """Exclui uma partida"""
    from backend.services.game_service import game_service

    if game_service.delete_game(game_id):
        return {"success": True, "message": "Partida excluída"}
    raise HTTPException(status_code=404, detail="Partida não encontrada")


@router.get("/api/games/{game_id}/qrcode")
async def get_qrcode(game_id: str, request: Request):
    """Gera QR Code para acesso dos jogadores"""
    from backend.services.game_service import game_service
    from backend.services.qr_service import qr_service

    game = game_service.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    # Monta URL completa do jogador
    base_url = str(request.base_url).rstrip('/')
    player_url = f"{base_url}/player?game={game_id}"

    qr_base64 = qr_service.generate_qr_base64(player_url)

    return {
        "game_id": game_id,
        "player_url": player_url,
        "qr_code": qr_base64
    }


# ============================================
# ROTAS DE RODADAS
# ============================================

@router.get("/api/games/{game_id}/round")
async def get_current_round(game_id: str):
    """Obtém a rodada atual"""
    from backend.services.game_service import game_service

    game = game_service.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    round_obj = game_service.get_current_round(game_id)
    if not round_obj:
        return {"round": None, "game": game.to_dict()}

    return {"round": round_obj.to_dict(), "game": game.to_dict()}


# ============================================
# PÁGINAS HTML
# ============================================

def serve_html(filename: str):
    """Serve um arquivo HTML"""
    filepath = os.path.join(FRONTEND_PATH, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)
    return HTMLResponse(
        content=f"<h1>Arquivo não encontrado: {filename}</h1>",
        status_code=404
    )


@router.get("/", response_class=HTMLResponse)
async def page_index():
    """Página inicial / Menu"""
    return serve_html('index.html')


@router.get("/admin", response_class=HTMLResponse)
async def page_admin():
    """Página de administração"""
    return serve_html('admin.html')


@router.get("/board", response_class=HTMLResponse)
async def page_board():
    """Página do tabuleiro (TV)"""
    return serve_html('board.html')


@router.get("/player", response_class=HTMLResponse)
async def page_player():
    """Página do jogador (celular)"""
    return serve_html('player.html')


# ============================================
# ARQUIVOS ESTÁTICOS
# ============================================

@router.get("/css/{filename}")
async def serve_css(filename: str):
    """Serve arquivos CSS"""
    filepath = os.path.join(FRONTEND_PATH, 'css', filename)
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type='text/css')
    raise HTTPException(status_code=404, detail="CSS não encontrado")


@router.get("/js/{filename}")
async def serve_js(filename: str):
    """Serve arquivos JavaScript"""
    filepath = os.path.join(FRONTEND_PATH, 'js', filename)
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type='application/javascript')
    raise HTTPException(status_code=404, detail="JS não encontrado")


@router.get("/assets/{path:path}")
async def serve_assets(path: str):
    """Serve arquivos de assets"""
    filepath = os.path.join(FRONTEND_PATH, 'assets', path)
    if os.path.exists(filepath):
        return FileResponse(filepath)
    raise HTTPException(status_code=404, detail="Asset não encontrado")


@router.get("/sounds/{filename}")
async def serve_sounds(filename: str):
    """Serve arquivos de som"""
    filepath = os.path.join(FRONTEND_PATH, 'sounds', filename)
    if os.path.exists(filepath):
        return FileResponse(filepath)
    raise HTTPException(status_code=404, detail="Som não encontrado")
