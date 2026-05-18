"""Immutable audit log for feature toggle state changes."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from lucky_number.database.base import Base


class FeatureToggleAudit(Base):
    """Immutable audit record for every feature toggle change.
    INSERT only — no UPDATE or DELETE allowed (enforced at application level).
    """
    __tablename__ = "feature_toggle_audit"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feature_toggle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("feature_toggles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    changed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    previous_state: Mapped[bool] = mapped_column(Boolean, nullable=False)
    new_state: Mapped[bool] = mapped_column(Boolean, nullable=False)
    source_ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<FeatureToggleAudit toggle={self.feature_toggle_id} {self.previous_state}→{self.new_state}>"
