"""Models package for Ras's Deep Treasure backend."""

"""
Database models for Ras's Deep Treasure game.

Exports all SQLAlchemy ORM models for use throughout the application.
Import order matters for relationship resolution.
"""

from backend.src.models.user import User
from backend.src.models.match import Match
from backend.src.models.submarine import Submarine
from backend.src.models.event import Event

__all__ = [
    "User",
    "Match",
    "Submarine",
    "Event",
]
# This ensures Alembic can discover all models for migrations
