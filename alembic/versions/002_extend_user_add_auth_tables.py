"""extend_user_add_auth_tables

Revision ID: 002
Revises: 001
Create Date: 2026-05-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Extend users table ---
    op.add_column("users", sa.Column("cpf", sa.String(11), nullable=True))
    op.add_column("users", sa.Column("telefone", sa.String(20), nullable=True))
    op.add_column("users", sa.Column("telefone_pais", sa.String(5), nullable=True))
    op.add_column("users", sa.Column("data_nascimento", sa.Date(), nullable=True))
    op.add_column("users", sa.Column("nome_completo", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("logradouro", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("numero", sa.String(20), nullable=True))
    op.add_column("users", sa.Column("complemento", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("bairro", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("cidade", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("estado", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("cep", sa.String(10), nullable=True))
    op.add_column("users", sa.Column("pais", sa.String(50), nullable=True, server_default="Brasil"))
    op.add_column("users", sa.Column("email_verificado_em", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("telefone_verificado_em", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("ativado_em", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("codigo_ativacao_hash", sa.String(128), nullable=True))
    op.add_column("users", sa.Column("tentativas_ativacao", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("codigo_ativacao_enviado_em", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("totp_secret", sa.String(64), nullable=True))
    op.add_column("users", sa.Column("codigos_reserva", postgresql.JSONB(), nullable=True))
    op.add_column("users", sa.Column("biometria_habilitada", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("users", sa.Column("dispositivo_push_token", sa.String(255), nullable=True))

    # Indexes for new columns
    op.create_index("ix_users_cpf", "users", ["cpf"], unique=True)
    op.create_index("ix_users_telefone", "users", ["telefone"])

    # --- password_reset_tokens ---
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("token_hash", sa.String(128), unique=True, nullable=False, index=True),
        sa.Column("canal_entrega", sa.String(20), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- activation_codes ---
    op.create_table(
        "activation_codes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("codigo_hash", sa.String(128), nullable=False),
        sa.Column("canal", sa.String(20), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tentativas", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_tentativas", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("consumido_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("activation_codes")
    op.drop_table("password_reset_tokens")
    op.drop_index("ix_users_telefone", table_name="users")
    op.drop_index("ix_users_cpf", table_name="users")

    columns_to_drop = [
        "cpf", "telefone", "telefone_pais", "data_nascimento", "nome_completo",
        "logradouro", "numero", "complemento", "bairro", "cidade", "estado", "cep", "pais",
        "email_verificado_em", "telefone_verificado_em",
        "ativado_em", "codigo_ativacao_hash", "tentativas_ativacao", "codigo_ativacao_enviado_em",
        "totp_secret", "codigos_reserva", "biometria_habilitada", "dispositivo_push_token",
    ]
    for col in columns_to_drop:
        op.drop_column("users", col)
