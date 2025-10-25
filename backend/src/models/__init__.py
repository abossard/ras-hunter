"""Models package for Ras's Deep Treasure backend."""

"""
Database models for Ras's Deep Treasure game.

Exports all SQLAlchemy ORM models for use throughout the application.
Import order matters for relationship resolution.
"""

from models.user import User
from models.match import Match
from models.submarine import Submarine
from models.event import Event

__all__ = [
    "User",
    "Match",
    "Submarine",
    "Event",
]
# This ensures Alembic can discover all models for migrations
