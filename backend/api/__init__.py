"""
30 Segundos v3.1 - API
"""

from backend.api.routes import router
from backend.api.socket_events import register_socket_events

__all__ = ['router', 'register_socket_events']
