"""
Submarine model for player avatar state within a match.

Per data-model.md:
- sub_id: VARCHAR(30), PRIMARY KEY, FORMAT 'sub-{username}'
- match_id: UUID, FOREIGN KEY → Match.match_id
- username: VARCHAR(20), FOREIGN KEY → User.username
- position_x/y: INT, within map bounds
- home_base_x/y: INT, spawn/return coordinates
- oxygen: INT, CHECK >= 0 AND <= 20, DEFAULT 20
- status: VARCHAR(10), CHECK IN ('submerged', 'surfaced', 'disabled', 'destroyed')
- last_action_timestamp: TIMESTAMP, for inactivity timeout
- inventory: JSONB, array of tool names
- treasure_held: BOOLEAN, DEFAULT FALSE
- disabled_count: INT, cumulative EMP hits
- frequency_secret: VARCHAR(36), UNIQUE UUID
- known_frequencies: JSONB, array of discovered frequencies
- known_fields: JSONB, map of discovered tiles
- travel_log: JSONB, array of events
- cooldowns: JSONB, map of action → remaining_ms
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.src.database import Base

if TYPE_CHECKING:
    from backend.src.models.user import User
    from backend.src.models.match import Match
    from backend.src.models.event import Event


class Submarine(Base):
    """
    Submarine entity representing a player's avatar in a match.
    
    Relationships:
    - Many submarines → one user
    - Many submarines → one match
    - One submarine → many events
    
    Validation:
    - oxygen: 0-20 range, 0 triggers disabled status (FR-013, FR-014)
    - position: within map bounds (0 ≤ x,y ≤ MAX_X/MAX_Y) (FR-016)
    - last_action_timestamp > 10 min → status becomes 'destroyed' (FR-046)
    - disabled_count resets to 0 on surface (FR-026)
    - treasure_held → FALSE if disabled_count >= 4 (FR-033)
    """
    
    __tablename__ = "submarines"
    
    # Primary key
    sub_id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
        nullable=False,
        comment="Unique submarine identifier per match (format: 'sub-{username}')"
    )
    
    # Foreign keys
    match_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("matches.match_id", ondelete="CASCADE"),
        nullable=False,
        comment="Associated match"
    )
    
    username: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("users.username", ondelete="CASCADE"),
        nullable=False,
        comment="Owning player"
    )
    
    # Position
    position_x: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Current x coordinate"
    )
    
    position_y: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Current y coordinate"
    )
    
    home_base_x: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Spawn and return x coordinate"
    )
    
    home_base_y: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Spawn and return y coordinate"
    )
    
    # Oxygen
    oxygen: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=20,
        comment="Current oxygen level (0-20)"
    )
    
    # Status
    status: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="submerged",
        comment="Submarine state: 'submerged', 'surfaced', 'disabled', 'destroyed'"
    )
    
    # Activity tracking
    last_action_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Last action received (for inactivity timeout)"
    )
    
    # Inventory & treasure
    inventory: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
        comment="Array of tool names: ['EMP', 'sonar', 'repair_kit']"
    )
    
    treasure_held: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether carrying treasure"
    )
    
    disabled_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Cumulative EMP hits (resets on surface)"
    )
    
    # Communication
    frequency_secret: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        unique=True,
        comment="UUID assigned at spawn for frequency-based communication"
    )
    
    known_frequencies: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
        comment="Array of discovered frequencies: ['freq-abc', 'freq-xyz']"
    )
    
    # Fog-of-war & exploration
    known_fields: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
        comment="Map of discovered tiles: {'5,7': 'empty', '6,7': 'tool'}"
    )
    
    travel_log: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
        comment="Array of events: [{'x': 5, 'y': 7, 'timestamp': '...', 'event': 'discovered'}]"
    )
    
    # Cooldowns
    cooldowns: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
        comment="Map of action → remaining_ms: {'discover': 8500}"
    )
    
    # Relationships (lazy='selectin' for async compatibility)
    user: Mapped["User"] = relationship(
        "User",
        back_populates="submarines",
        lazy="selectin"
    )
    
    match: Mapped["Match"] = relationship(
        "Match",
        back_populates="submarines",
        lazy="selectin"
    )
    
    events: Mapped[list["Event"]] = relationship(
        "Event",
        back_populates="submarine",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "oxygen >= 0 AND oxygen <= 20",
            name="submarine_oxygen_check"
        ),
        CheckConstraint(
            "position_x >= 0",
            name="submarine_position_x_check"
        ),
        CheckConstraint(
            "position_y >= 0",
            name="submarine_position_y_check"
        ),
        CheckConstraint(
            "status IN ('submerged', 'surfaced', 'disabled', 'destroyed')",
            name="submarine_status_check"
        ),
        Index("idx_submarine_match_status", "match_id", "status"),
        Index("idx_submarine_match_position", "match_id", "position_x", "position_y"),
        Index("idx_submarine_last_action", "last_action_timestamp"),
    )
    
    def __repr__(self) -> str:
        return f"<Submarine(sub_id='{self.sub_id}', username='{self.username}', status='{self.status}', oxygen={self.oxygen})>"
