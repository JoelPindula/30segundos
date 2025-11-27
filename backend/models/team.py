"""
30 Segundos v3.1 - Modelo de Time
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Team:
    name: str
    color: str
    players: List[str] = field(default_factory=list)
    position: int = 0
    current_player_index: int = 0

    @property
    def current_player(self) -> Optional[dict]:
        if not self.players:
            return None
        return {
            "name": self.players[self.current_player_index],
            "index": self.current_player_index
        }

    def advance_player(self):
        """Avança para o próximo jogador"""
        if self.players:
            self.current_player_index = (
                self.current_player_index + 1) % len(self.players)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "color": self.color,
            "players": self.players,
            "position": self.position,
            "current_player": self.current_player
        }
