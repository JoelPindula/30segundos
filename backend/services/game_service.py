"""
30 Segundos v3.1 - Serviço de Gerenciamento de Jogos
"""

import random
from typing import Dict, List, Optional
from backend.models.game import Game, Team, Player, GameConfig, RoundData, Card
from backend.services.word_service import word_service


class GameService:
    def __init__(self):
        self.games: Dict[str, Game] = {}
        self.challenges = self._load_challenges()
        self.cursed_words = self._load_cursed_words()

    def _load_challenges(self) -> List[str]:
        """Carrega desafios do word_service ou usa padrão"""
        if 'desafios' in word_service.word_banks:
            return [w['word'] for w in word_service.word_banks['desafios']]
        return [
            "Conte de 1 a 50 em 30 segundos",
            "Diga 10 capitais de países",
            "Faça 15 polichinelos",
            "Imite 5 animais diferentes",
            "Diga o alfabeto de trás para frente",
            "Nomeie 10 marcas de carro",
            "Cante um trecho de 3 músicas diferentes",
            "Diga 10 times de futebol",
            "Faça 10 flexões",
            "Diga 10 cores em inglês",
            "Nomeie 8 países da Europa",
            "Diga 10 frutas em 15 segundos",
            "Faça mímica de 3 profissões",
            "Conte de 100 a 70 de trás para frente",
            "Diga 10 verbos em inglês"
        ]

    def _load_cursed_words(self) -> List[str]:
        """
        Palavras/frases difíceis para carta amaldiçoada.
        Mistura termos desafiadores com pequenas frases de descrição.
        """
        cursed: List[str] = []

        # Pega palavras de nível alto dos bancos (se existirem)
        for theme, words in word_service.word_banks.items():
            for w in words:
                if w.get('level', 1) >= 4:
                    cursed.append(w['word'])

        # Lista padrão de "palavras amaldiçoadas" mais pronunciáveis
        default_cursed = [
            # Palavras difíceis
            "Incompreensível",
            "Arqueologia",
            "Hipótese",
            "Ecossistema",
            "Filantropia",
            "Nanotecnologia",
            "Hereditariedade",
            "Metamorfose",
            "Perpendicular",
            "Sonoridade",

            # Pequenas frases desafiadoras
            "Um lugar onde o tempo parece parar",
            "Algo que se transforma completamente",
            "Uma ideia quase impossível de acreditar",
            "Quando duas coisas ficam com a mesma temperatura",
            "Uma memória que nunca desaparece",
            "Um som que ecoa ao longe",
            "Um objeto que ninguém sabe de onde veio",
            "Uma descoberta que muda tudo",
            "Uma viagem sem destino certo",
            "Algo raríssimo de acontecer"
        ]

        # Garante que todas as palavras/frases padrão estão incluídas
        for word in default_cursed:
            if word not in cursed:
                cursed.append(word)

        return cursed

    def create_game(self, data: dict) -> Game:
        """Cria uma nova partida"""
        game_id = Game.generate_id()
        while game_id in self.games:
            game_id = Game.generate_id()

        # Cria times
        team1_players = [Player(name=n)
                         for n in data.get('team1_players', ['Jogador 1'])]
        team2_players = [Player(name=n)
                         for n in data.get('team2_players', ['Jogador 1'])]

        team1 = Team(name=data.get('team1_name', 'Time Amarelo'),
                     players=team1_players)
        team2 = Team(name=data.get('team2_name', 'Time Azul'),
                     players=team2_players)

        # Configurações
        config = GameConfig(
            round_time=data.get('round_time', 30),
            words_per_side=data.get('words_per_side', 5),
            bonus_chance=data.get('bonus_chance', 0.15),
            max_challenges_per_game=3,
            challenge_chance=0.12,
            max_cursed_per_game=2,
            cursed_chance=0.10
        )

        # Cria jogo
        game = Game(
            id=game_id,
            name=data.get('name', 'Partida 30 Segundos'),
            team1=team1,
            team2=team2,
            themes=data.get('themes', ['geral']),
            levels=data.get('levels', [1, 2]),
            config=config
        )

        self.games[game_id] = game
        word_service.init_game_pool(game_id)

        print(f"[GameService] Jogo criado: {game_id}")
        return game

    def get_game(self, game_id: str) -> Optional[Game]:
        return self.games.get(game_id.upper())

    def get_all_games(self) -> List[Game]:
        return list(self.games.values())

    def start_game(self, game_id: str) -> Optional[Game]:
        """Inicia a partida"""
        game = self.get_game(game_id)
        if game:
            game.state = 'playing'
            game.current_round = 0
            game.cursed_count = 0
            game.challenge_count = 0
            print(f"[GameService] Jogo {game_id} iniciado")
        return game

    def prepare_round(self, game_id: str) -> Optional[dict]:
        """Prepara uma nova rodada"""
        game = self.get_game(game_id)
        if not game:
            return None

        game.current_round += 1

        # DESAFIO - aleatório (máx 2-3 por partida)
        is_challenge = False
        if game.can_have_challenge():
            is_challenge = random.random() < game.config.challenge_chance

        # CARTA AMALDIÇOADA - aleatório (máx 2 por partida)
        # Só pode ser amaldiçoada se NÃO for desafio
        is_cursed = False
        if not is_challenge and game.can_have_cursed():
            is_cursed = random.random() < game.config.cursed_chance

        if is_challenge:
            # Rodada de desafio
            challenge_text = random.choice(self.challenges)
            game.challenge_count += 1
            round_data = RoundData(
                round_number=game.current_round,
                team=game.current_team,
                is_challenge=True,
                challenge_text=challenge_text
            )
            print(
                f"[GameService] Rodada {game.current_round}: DESAFIO ({game.challenge_count}/{game.config.max_challenges_per_game})")

        elif is_cursed:
            # Carta amaldiçoada
            cursed_word = random.choice(self.cursed_words)
            game.cursed_count += 1
            round_data = RoundData(
                round_number=game.current_round,
                team=game.current_team,
                is_cursed=True,
                cursed_word=cursed_word
            )
            print(
                f"[GameService] Rodada {game.current_round}: CARTA AMALDIÇOADA ({game.cursed_count}/{game.config.max_cursed_per_game})")

        else:
            # Rodada normal
            card_data = word_service.get_card_words(
                game_id=game_id,
                themes=game.themes,
                levels=game.levels,
                words_per_side=game.config.words_per_side,
                bonus_chance=game.config.bonus_chance,
                cursed_chance=0
            )

            if not card_data:
                print(f"[GameService] Erro: não conseguiu gerar carta")
                return None

            card = Card(
                yellow_words=card_data['yellow_words'],
                blue_words=card_data['blue_words']
            )

            round_data = RoundData(
                round_number=game.current_round,
                team=game.current_team,
                card=card
            )
            print(f"[GameService] Rodada {game.current_round}: Normal")

        game.current_round_data = round_data

        return {
            'game': game.to_dict(),
            'round': round_data.to_dict()
        }

    def start_timer(self, game_id: str) -> Optional[dict]:
        """Inicia o timer da rodada"""
        game = self.get_game(game_id)
        if not game or not game.current_round_data:
            return None

        game.current_round_data.started = True

        return {
            'game': game.to_dict(),
            'round': game.current_round_data.to_dict()
        }

    def register_hit(self, game_id: str, word: str, is_bonus: bool = False) -> bool:
        """Registra uma palavra acertada"""
        game = self.get_game(game_id)
        if not game or not game.current_round_data:
            return False

        if word not in game.current_round_data.player_hits:
            game.current_round_data.player_hits.append(word)

        return True

    def end_round(self, game_id: str) -> Optional[dict]:
        """Finaliza a rodada (tempo acabou)"""
        game = self.get_game(game_id)
        if not game or not game.current_round_data:
            return None

        return {
            'game': game.to_dict(),
            'round': game.current_round_data.to_dict(),
            'player_hits': game.current_round_data.player_hits
        }

    def confirm_round(self, game_id: str, confirmed_words: List[str]) -> Optional[dict]:
        """Confirma os acertos de rodada NORMAL e move o time"""
        game = self.get_game(game_id)
        if not game or not game.current_round_data:
            return None

        round_data = game.current_round_data

        # Conta acertos
        hits = len(confirmed_words)
        bonus_hits = 0

        # Verifica bônus nas palavras confirmadas
        if round_data.card:
            all_words = round_data.card.yellow_words + round_data.card.blue_words
            for word in all_words:
                if word.get('text') in confirmed_words and word.get('is_bonus'):
                    bonus_hits += 1

        # Calcula movimento
        moves = hits + bonus_hits

        # Move o time atual
        current_team = game.get_current_team()
        current_team.position = min(30, current_team.position + moves)

        # Verifica vitória
        winner = None
        if current_team.position >= 30:
            game.state = 'finished'
            winner = current_team.name

        # Avança para próximo time
        if not winner:
            game.advance_turn()

        # Limpa rodada atual
        game.current_round_data = None

        return {
            'game': game.to_dict(),
            'result': {
                'hits': hits,
                'bonus': bonus_hits,
                'moves': moves,
                'was_challenge': False,
                'was_cursed': False
            },
            'winner': winner
        }

    def resolve_challenge(self, game_id: str, completed: bool) -> Optional[dict]:
        """Resolve um desafio"""
        game = self.get_game(game_id)
        if not game or not game.current_round_data:
            return None

        current_team = game.get_current_team()

        if completed:
            # Acertou: +5 casas
            moves = 5
            current_team.position = min(30, current_team.position + moves)
        else:
            # Errou: -2 casas (mínimo 0)
            moves = -2
            current_team.position = max(0, current_team.position - 2)

        # Verifica vitória
        winner = None
        if current_team.position >= 30:
            game.state = 'finished'
            winner = current_team.name

        # Avança turno
        if not winner:
            game.advance_turn()

        # Limpa rodada
        game.current_round_data = None

        return {
            'game': game.to_dict(),
            'result': {
                'hits': 1 if completed else 0,
                'bonus': 0,
                'moves': moves,
                'was_challenge': True,
                'was_cursed': False,
                'completed': completed
            },
            'winner': winner
        }

    def resolve_cursed(self, game_id: str, guessed: bool) -> Optional[dict]:
        """Resolve uma carta amaldiçoada"""
        game = self.get_game(game_id)
        if not game or not game.current_round_data:
            return None

        current_team = game.get_current_team()

        if guessed:
            # Acertou: +2 casas
            moves = 2
            current_team.position = min(30, current_team.position + moves)
        else:
            # Errou: -5 casas (mínimo 0)
            moves = -5
            current_team.position = max(0, current_team.position - 5)

        # Verifica vitória
        winner = None
        if current_team.position >= 30:
            game.state = 'finished'
            winner = current_team.name

        # Avança turno
        if not winner:
            game.advance_turn()

        # Limpa rodada
        game.current_round_data = None

        return {
            'game': game.to_dict(),
            'result': {
                'hits': 1 if guessed else 0,
                'bonus': 0,
                'moves': moves,
                'was_challenge': False,
                'was_cursed': True,
                'guessed': guessed
            },
            'winner': winner
        }

    def delete_game(self, game_id: str) -> bool:
        """Remove uma partida"""
        if game_id in self.games:
            word_service.clear_game_pool(game_id)
            del self.games[game_id]
            return True
        return False


# Instância global
game_service = GameService()
