"""
Match model for game session tracking.

Per data-model.md:
- match_id: UUID, PRIMARY KEY
- start_time: TIMESTAMP, NOT NULL, DEFAULT NOW()
- end_time: TIMESTAMP, NULLABLE (NULL = active)
- status: VARCHAR(10), CHECK IN ('active', 'ended')
- winner_username: VARCHAR(20), FOREIGN KEY → User.username, NULLABLE
- map_configuration: JSONB, NOT NULL (treasure location, home bases, tile content)
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.src.database import Base

if TYPE_CHECKING:
    from backend.src.models.submarine import Submarine
    from backend.src.models.event import Event
    from backend.src.models.user import User


class Match(Base):
    """
    Match entity representing a 20-player game session.
    
    Relationships:
    - One match → many submarines (max 20)
    - One match → many events
    - Many matches → one winner (user)
    
    Validation:
    - status: 'active' or 'ended'
    - map_configuration JSONB schema per FR-007, FR-008, FR-009, FR-022:
      - dimensions: max_x, max_y (default 32×32)
      - treasure_tile: {x, y}
      - home_bases: array of 20 {player_index, x, y}
      - tiles: array of {x, y, content, [tool_type|hazard_type]}
    """
    
    __tablename__ = "matches"
    
    # Primary key
    match_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
        comment="Unique match identifier"
    )
    
    # Timestamps
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Match start timestamp"
    )
    
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Match completion timestamp (NULL = active)"
    )
    
    # Status
    status: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="active",
        comment="Match lifecycle state: 'active' or 'ended'"
    )
    
    # Winner
    winner_username: Mapped[str | None] = mapped_column(
        String(20),
        ForeignKey("users.username", ondelete="SET NULL"),
        nullable=True,
        comment="Winning player (NULL if no winner yet)"
    )
    
    # Map data
    map_configuration: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="Initial map state (treasure, home bases, tile content)"
    )
    
    # Relationships (lazy='selectin' for async compatibility)
    submarines: Mapped[list["Submarine"]] = relationship(
        "Submarine",
        back_populates="match",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    
    events: Mapped[list["Event"]] = relationship(
        "Event",
        back_populates="match",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    
    winner: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[winner_username],
        lazy="selectin"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'ended')",
            name="match_status_check"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<Match(match_id='{self.match_id}', status='{self.status}', start_time='{self.start_time}')>"
