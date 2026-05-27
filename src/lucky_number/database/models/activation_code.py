"""Activation code model — 6-digit code for account activation."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from lucky_number.database.base import Base


class ActivationCode(Base):
    __tablename__ = "activation_codes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    codigo_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    canal: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'email' | 'sms' | 'whatsapp'
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    tentativas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_tentativas: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    consumido_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ActivationCode user={self.user_id} channel={self.canal}>"
