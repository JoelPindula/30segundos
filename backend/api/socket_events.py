"""
30 Segundos v3.1 - Eventos Socket.IO
"""

from socketio import AsyncServer
from backend.services.game_service import game_service


def register_socket_events(sio: AsyncServer):
    """Registra todos os eventos do Socket.IO"""

    player_counts = {}

    @sio.event
    async def connect(sid, environ):
        print(f"[Socket] Cliente conectado: {sid}")

    @sio.event
    async def disconnect(sid):
        print(f"[Socket] Cliente desconectado: {sid}")

    @sio.event
    async def join_game(sid, data):
        """Jogador ou board entra em uma partida"""
        game_id = data.get('game_id', '').upper()
        client_type = data.get('type', 'player')

        game = game_service.get_game(game_id)
        if not game:
            await sio.emit('error', {'message': 'Partida não encontrada'}, to=sid)
            return

        await sio.enter_room(sid, game_id)
        print(f"[Socket] {client_type} entrou na partida {game_id}")

        if game_id not in player_counts:
            player_counts[game_id] = {'board': 0, 'player': 0}

        player_counts[game_id][client_type] += 1

        await sio.emit('game_state', game.to_dict(), to=sid)

        if client_type == 'player':
            await sio.emit('player_connected', {
                'player_count': player_counts[game_id]['player'],
                'message': 'Jogador conectado!'
            }, room=game_id)
            print(f"[Socket] Notificando board: jogador conectou em {game_id}")

        if game.current_round_data:
            await sio.emit('round_ready', {
                'game': game.to_dict(),
                'round': game.current_round_data.to_dict()
            }, to=sid)

    @sio.event
    async def start_game(sid, data):
        """Inicia uma partida"""
        game_id = data.get('game_id', '').upper()
        print(f"[Socket] Iniciando jogo {game_id}")

        game = game_service.start_game(game_id)
        if not game:
            await sio.emit('error', {'message': 'Erro ao iniciar partida'}, to=sid)
            return

        await sio.emit('game_started', game.to_dict(), room=game_id)

        result = game_service.prepare_round(game_id)
        if result:
            await sio.emit('round_ready', result, room=game_id)
            print(f"[Socket] Rodada pronta enviada para {game_id}")

    @sio.event
    async def request_round(sid, data):
        """Solicita uma nova rodada"""
        game_id = data.get('game_id', '').upper()

        result = game_service.prepare_round(game_id)
        if not result:
            await sio.emit('error', {'message': 'Erro ao preparar rodada'}, to=sid)
            return

        await sio.emit('round_ready', result, room=game_id)

    @sio.event
    async def player_view_card(sid, data):
        """Jogador visualizou a carta"""
        game_id = data.get('game_id', '').upper()
        await sio.emit('player_viewing_card', {}, room=game_id)

    @sio.event
    async def start_timer(sid, data):
        """Inicia o timer da rodada"""
        game_id = data.get('game_id', '').upper()

        result = game_service.start_timer(game_id)
        if not result:
            await sio.emit('error', {'message': 'Erro ao iniciar timer'}, to=sid)
            return

        await sio.emit('timer_started', result, room=game_id)

    @sio.event
    async def word_hit(sid, data):
        """Jogador marcou uma palavra como acertada"""
        game_id = data.get('game_id', '').upper()
        word = data.get('word', '')
        is_bonus = data.get('is_bonus', False)

        success = game_service.register_hit(game_id, word, is_bonus)

        if success:
            await sio.emit('player_hit', {
                'word': word,
                'is_bonus': is_bonus
            }, room=game_id)

    @sio.event
    async def timer_ended(sid, data):
        """Timer acabou"""
        game_id = data.get('game_id', '').upper()

        result = game_service.end_round(game_id)
        if not result:
            return

        await sio.emit('time_up', result, room=game_id)

    @sio.event
    async def confirm_round(sid, data):
        """Board confirma os acertos da rodada NORMAL"""
        game_id = data.get('game_id', '').upper()
        confirmed_words = data.get('confirmed_words', [])

        result = game_service.confirm_round(game_id, confirmed_words)
        if not result:
            await sio.emit('error', {'message': 'Erro ao confirmar rodada'}, to=sid)
            return

        if result.get('winner'):
            await sio.emit('game_finished', {
                'game': result['game'],
                'winner': result['winner']
            }, room=game_id)
        else:
            await sio.emit('round_confirmed', result, room=game_id)

    @sio.event
    async def challenge_result(sid, data):
        """Board informa resultado do DESAFIO"""
        game_id = data.get('game_id', '').upper()
        completed = data.get('completed', False)

        result = game_service.resolve_challenge(game_id, completed)
        if not result:
            await sio.emit('error', {'message': 'Erro ao resolver desafio'}, to=sid)
            return

        if result.get('winner'):
            await sio.emit('game_finished', {
                'game': result['game'],
                'winner': result['winner']
            }, room=game_id)
        else:
            await sio.emit('round_confirmed', result, room=game_id)

    @sio.event
    async def cursed_result(sid, data):
        """Board informa resultado da CARTA AMALDIÇOADA"""
        game_id = data.get('game_id', '').upper()
        guessed = data.get('guessed', False)

        result = game_service.resolve_cursed(game_id, guessed)
        if not result:
            await sio.emit('error', {'message': 'Erro ao resolver carta amaldiçoada'}, to=sid)
            return

        if result.get('winner'):
            await sio.emit('game_finished', {
                'game': result['game'],
                'winner': result['winner']
            }, room=game_id)
        else:
            await sio.emit('round_confirmed', result, room=game_id)
