"""
30 Segundos v3.1 - Modelos de Dados
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
import random
import string


@dataclass
class Player:
    name: str

    def to_dict(self):
        return {"name": self.name}


@dataclass
class Team:
    name: str
    players: List[Player] = field(default_factory=list)
    position: int = 0
    current_player_index: int = 0

    @property
    def current_player(self) -> Optional[Player]:
        if self.players:
            return self.players[self.current_player_index % len(self.players)]
        return None

    def next_player(self):
        if self.players:
            self.current_player_index = (
                self.current_player_index + 1) % len(self.players)

    def to_dict(self):
        return {
            "name": self.name,
            "players": [p.to_dict() for p in self.players],
            "position": self.position,
            "current_player": self.current_player.to_dict() if self.current_player else None
        }


@dataclass
class Card:
    yellow_words: List[dict] = field(default_factory=list)
    blue_words: List[dict] = field(default_factory=list)

    def to_dict(self):
        return {
            "yellow_words": self.yellow_words,
            "blue_words": self.blue_words
        }


@dataclass
class RoundData:
    round_number: int
    team: int
    card: Optional[Card] = None
    is_challenge: bool = False
    challenge_text: str = ""
    is_cursed: bool = False
    cursed_word: str = ""
    player_hits: List[str] = field(default_factory=list)
    started: bool = False

    def to_dict(self):
        return {
            "round_number": self.round_number,
            "team": self.team,
            "card": self.card.to_dict() if self.card else None,
            "is_challenge": self.is_challenge,
            "challenge_text": self.challenge_text,
            "is_cursed": self.is_cursed,
            "cursed_word": self.cursed_word,
            "player_hits": self.player_hits,
            "started": self.started
        }


@dataclass
class GameConfig:
    round_time: int = 30
    words_per_side: int = 5
    bonus_chance: float = 0.15
    # DESAFIO - aleatório, 2-3 por partida
    max_challenges_per_game: int = 3
    challenge_chance: float = 0.12  # 12% de chance por rodada
    # AMALDIÇOADA - aleatório, máx 2 por partida
    max_cursed_per_game: int = 2
    cursed_chance: float = 0.10  # 10% de chance por rodada

    def to_dict(self):
        return {
            "round_time": self.round_time,
            "words_per_side": self.words_per_side,
            "bonus_chance": self.bonus_chance,
            "max_challenges_per_game": self.max_challenges_per_game,
            "challenge_chance": self.challenge_chance,
            "max_cursed_per_game": self.max_cursed_per_game,
            "cursed_chance": self.cursed_chance
        }


@dataclass
class Game:
    id: str
    name: str
    team1: Team
    team2: Team
    themes: List[str] = field(default_factory=list)
    levels: List[int] = field(default_factory=list)
    config: GameConfig = field(default_factory=GameConfig)
    state: str = "waiting"  # waiting, playing, finished
    current_team: int = 1
    current_round: int = 0
    current_round_data: Optional[RoundData] = None
    cursed_count: int = 0      # Contador de cartas amaldiçoadas usadas
    challenge_count: int = 0   # Contador de desafios usados
    created_at: datetime = field(default_factory=datetime.now)

    @staticmethod
    def generate_id() -> str:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

    def get_current_team(self) -> Team:
        return self.team1 if self.current_team == 1 else self.team2

    def get_other_team(self) -> Team:
        return self.team2 if self.current_team == 1 else self.team1

    def advance_turn(self):
        """Avança para o próximo time e jogador"""
        current = self.get_current_team()
        current.next_player()
        self.current_team = 2 if self.current_team == 1 else 1

    def can_have_cursed(self) -> bool:
        """Verifica se ainda pode ter carta amaldiçoada"""
        return self.cursed_count < self.config.max_cursed_per_game

    def can_have_challenge(self) -> bool:
        """Verifica se ainda pode ter desafio"""
        return self.challenge_count < self.config.max_challenges_per_game

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "team1": self.team1.to_dict(),
            "team2": self.team2.to_dict(),
            "themes": self.themes,
            "levels": self.levels,
            "config": self.config.to_dict(),
            "state": self.state,
            "current_team": self.current_team,
            "current_round": self.current_round,
            "current_round_data": self.current_round_data.to_dict() if self.current_round_data else None,
            "cursed_count": self.cursed_count,
            "challenge_count": self.challenge_count
        }
