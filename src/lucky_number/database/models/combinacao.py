"""Combinacao model — FIFO user combination history (Principle IV)."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from lucky_number.database.base import Base, TimestampMixin


class Combinacao(Base, TimestampMixin):
    __tablename__ = "combinacoes_salvas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    jogo: Mapped[str] = mapped_column(String(50), nullable=False)
    dezenas: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    dezenas_por_aposta: Mapped[int] = mapped_column(Integer, nullable=False)
    favorita: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hash_combinacao: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Combinacao {self.jogo} user={self.user_id}>"
