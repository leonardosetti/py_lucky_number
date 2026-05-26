"""User SQLAlchemy model with soft delete and extended profile fields."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from lucky_number.database.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False
    )
    regiao: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Extended profile fields (spec 022, 025, 026)
    cpf: Mapped[str | None] = mapped_column(String(11), unique=True, nullable=True, index=True)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    telefone_pais: Mapped[str | None] = mapped_column(String(5), nullable=True)
    data_nascimento: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    nome_completo: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Address block
    logradouro: Mapped[str | None] = mapped_column(String(255), nullable=True)
    numero: Mapped[str | None] = mapped_column(String(20), nullable=True)
    complemento: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bairro: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cidade: Mapped[str | None] = mapped_column(String(100), nullable=True)
    estado: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cep: Mapped[str | None] = mapped_column(String(10), nullable=True)
    pais: Mapped[str | None] = mapped_column(String(50), nullable=True, default="Brasil")

    # Email & phone verification
    email_verificado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    telefone_verificado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Activation flow
    ativado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    codigo_ativacao_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tentativas_ativacao: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    codigo_ativacao_enviado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # 2FA
    totp_secret: Mapped[str | None] = mapped_column(String(64), nullable=True)
    codigos_reserva: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Biometrics / push
    biometria_habilitada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dispositivo_push_token: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<User {self.email} ativo={self.ativo}>"
