"""AuditLog SQLAlchemy model — immutable INSERT-only audit trail."""
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from lucky_number.database.base import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    admin_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    acao: Mapped[str] = mapped_column(
        String(20), nullable=False
    )
    entidade_tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    entidade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    detalhes: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict, server_default=func.cast("{}", JSON)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        {"postgresql_partition_by": "RANGE (created_at)"}
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.acao} {self.entidade_tipo} by {self.admin_id}>"
