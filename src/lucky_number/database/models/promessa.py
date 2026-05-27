"""Promessa model — Bet promise simulation (Principle V)."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Float, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from lucky_number.database.base import Base, TimestampMixin


class Promessa(Base, TimestampMixin):
    __tablename__ = "promessas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    titulo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    prioridade: Mapped[str] = mapped_column(String(10), default="media", nullable=False)
    valor_total: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    combinacoes_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    favorita: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hash_compartilhamento: Mapped[str | None] = mapped_column(
        String(128), unique=True, nullable=True
    )
    compartilhado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Promessa {self.titulo} user={self.user_id}>"
