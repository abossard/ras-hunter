"""
Event model for travel log and game event audit trail.

Per data-model.md:
- event_id: UUID, PRIMARY KEY
- match_id: UUID, FOREIGN KEY → Match.match_id
- sub_id: VARCHAR(30), FOREIGN KEY → Submarine.sub_id
- position_x/y: INT, event coordinates
- event_type: VARCHAR(30), event category
- event_details: JSONB, type-specific data
- occurred_at: TIMESTAMP, DEFAULT NOW()
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.src.database import Base

if TYPE_CHECKING:
    from backend.src.models.match import Match
    from backend.src.models.submarine import Submarine


class Event(Base):
    """
    Event entity representing game actions and state changes.
    
    Relationships:
    - Many events → one match
    - Many events → one submarine
    
    Event Types (FR-035, FR-051):
    - player_spawned: New submarine created at home_base
    - tile_discovered: Fog-of-war tile revealed
    - treasure_found: Player discovered treasure tile
    - emp_hit: EMP tool used on target
    - frequency_exchanged: Communication frequency shared
    - player_surfaced: Submarine completed surfacing
    - player_inactive_timeout: Player inactive for 10+ minutes
    - match_won: Player returned treasure to home_base
    - match_reset: Match ended and new match started
    """
    
    __tablename__ = "events"
    
    # Primary key
    event_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
        comment="Unique event identifier"
    )
    
    # Foreign keys
    match_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("matches.match_id", ondelete="CASCADE"),
        nullable=False,
        comment="Associated match"
    )
    
    sub_id: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("submarines.sub_id", ondelete="CASCADE"),
        nullable=False,
        comment="Event generator"
    )
    
    # Position
    position_x: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Event x coordinate"
    )
    
    position_y: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Event y coordinate"
    )
    
    # Event data
    event_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Event category: 'discovered', 'emp_hit', 'surfaced', etc."
    )
    
    event_details: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="Type-specific data: {'tile_content': 'tool', 'tool_type': 'sonar'}"
    )
    
    # Timestamp
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Event timestamp"
    )
    
    # Relationships (lazy='selectin' for async compatibility)
    match: Mapped["Match"] = relationship(
        "Match",
        back_populates="events",
        lazy="selectin"
    )
    
    submarine: Mapped["Submarine"] = relationship(
        "Submarine",
        back_populates="events",
        lazy="selectin"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_event_match_sub_time", "match_id", "sub_id", "occurred_at"),
        Index("idx_event_match_time", "match_id", "occurred_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Event(event_id='{self.event_id}', event_type='{self.event_type}', occurred_at='{self.occurred_at}')>"
