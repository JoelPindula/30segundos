"""
30 Segundos v3.1 - Services
"""

from backend.services.game_service import game_service
from backend.services.word_service import word_service
from backend.services.challenge_service import challenge_service

__all__ = ['game_service', 'word_service', 'challenge_service']
