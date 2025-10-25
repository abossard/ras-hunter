"""
User model for player authentication and account management.

Per data-model.md:
- username: VARCHAR(20), PRIMARY KEY, regex validation ^[a-zA-Z0-9_]{3,20}$
- password_hash: VARCHAR(255), bcrypt with work factor 12
- created_at: TIMESTAMP, NOT NULL, DEFAULT NOW()
- last_login_at: TIMESTAMP, NULLABLE
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.src.database import Base

if TYPE_CHECKING:
    from backend.src.models.submarine import Submarine


class User(Base):
    """
    User entity representing a registered player.
    
    Relationships:
    - One user → many submarines (across different matches)
    
    Validation:
    - Username must match ^[a-zA-Z0-9_]{3,20}$ (enforced at API layer)
    - password_hash created via bcrypt with work factor 12 (enforced at service layer)
    """
    
    __tablename__ = "users"
    
    # Primary key
    username: Mapped[str] = mapped_column(
        String(20),
        primary_key=True,
        nullable=False,
        comment="Unique player identifier (3-20 alphanumeric + underscore)"
    )
    
    # Authentication
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="bcrypt password hash (work factor 12)"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Account creation timestamp"
    )
    
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Most recent successful login timestamp"
    )
    
    # Relationships (lazy='selectin' for async compatibility)
    submarines: Mapped[list["Submarine"]] = relationship(
        "Submarine",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(username='{self.username}', created_at='{self.created_at}')>"
