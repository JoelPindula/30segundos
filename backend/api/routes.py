"""
30 Segundos v3.1 - Rotas da API REST
"""

import qrcode
import base64
from io import BytesIO
from fastapi import APIRouter, HTTPException, Request
from backend.services.game_service import game_service

router = APIRouter()


@router.get("/games")
async def list_games():
    """Lista todas as partidas"""
    games = game_service.get_all_games()
    return {"games": [g.to_dict() for g in games]}


@router.post("/games")
async def create_game(data: dict):
    """Cria uma nova partida"""
    game = game_service.create_game(data)
    return game.to_dict()


@router.get("/games/{game_id}")
async def get_game(game_id: str):
    """Obtém uma partida específica"""
    game = game_service.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    return game.to_dict()


@router.delete("/games/{game_id}")
async def delete_game(game_id: str):
    """Remove uma partida"""
    success = game_service.delete_game(game_id)
    if not success:
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    return {"success": True}


@router.get("/games/{game_id}/qrcode")
async def get_qrcode(game_id: str, request: Request):
    """Gera QR Code para o jogador acessar"""
    game = game_service.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    # Obtém o host da requisição
    host = request.headers.get("host", "localhost:8000")

    # URL do jogador
    player_url = f"http://{host}/player?game={game_id}"

    # Gera QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(player_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Converte para base64
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return {
        "qr_code": f"data:image/png;base64,{img_str}",
        "player_url": player_url
    }


@router.get("/themes")
async def list_themes():
    """Lista temas disponíveis"""
    from backend.services.word_service import word_service

    themes = []
    for theme_id, words in word_service.word_banks.items():
        if theme_id != 'desafios':
            themes.append({
                "id": theme_id,
                "name": theme_id.replace("_", " ").title(),
                "word_count": len(words)
            })

    return {"themes": themes}
