"""
30 Segundos v3.1 - Modelo de Rodada
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Round:
    number: int
    team: int  # 1 ou 2
    card: Optional[dict] = None
    starting_color: str = 'yellow'
    is_challenge: bool = False
    challenge_text: Optional[str] = None
    timer_started: bool = False
    timer_ended: bool = False
    start_time: Optional[datetime] = None
    player_hits: List[str] = field(default_factory=list)
    bonus_hits: List[str] = field(default_factory=list)
    cursed_hits: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "team": self.team,
            "card": self.card,
            "starting_color": self.starting_color,
            "is_challenge": self.is_challenge,
            "challenge_text": self.challenge_text,
            "timer_started": self.timer_started,
            "timer_ended": self.timer_ended,
            "player_hits": self.player_hits,
            "bonus_hits": self.bonus_hits,
            "cursed_hits": self.cursed_hits
        }
