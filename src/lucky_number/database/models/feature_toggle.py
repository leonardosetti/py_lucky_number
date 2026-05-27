"""Feature toggle SQLAlchemy model with optimistic locking."""

import uuid

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from lucky_number.database.base import Base, TimestampMixin


class FeatureToggle(Base, TimestampMixin):
    __tablename__ = "feature_toggles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativa: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    version: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False
    )  # optimistic locking

    def __repr__(self) -> str:
        return f"<FeatureToggle slug={self.slug} ativa={self.ativa}>"
