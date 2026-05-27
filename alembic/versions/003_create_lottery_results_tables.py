"""create_lottery_results_tables

Creates 10 loterias_resultados_{jogo} tables + audit_log.

Revision ID: 003
Revises: 002
Create Date: 2026-05-26
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ─── audit_log ───────────────────────────────────────────────
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("admin_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("acao", sa.String(20), nullable=False),
        sa.Column("entidade_tipo", sa.String(50), nullable=False),
        sa.Column("entidade_id", sa.Uuid(), nullable=False),
        sa.Column("detalhes", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.CheckConstraint("acao IN ('create','update','delete','clone','toggle')", name="ck_audit_acao"),
    )
    op.create_index("idx_audit_created_at", "audit_log", ["created_at"], postgresql_using="brin")

    # ─── loterias_resultados_megasena ────────────────────────────
    op.execute("""
        CREATE TABLE loterias_resultados_megasena (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            "Concurso" INTEGER NOT NULL,
            "Data do Sorteio" DATE NOT NULL,
            "Bola1" INTEGER NOT NULL, "Bola2" INTEGER NOT NULL,
            "Bola3" INTEGER NOT NULL, "Bola4" INTEGER NOT NULL,
            "Bola5" INTEGER NOT NULL, "Bola6" INTEGER NOT NULL,
            "Ganhadores 6 acertos" INTEGER DEFAULT 0,
            "Cidade / UF" VARCHAR(150),
            "Rateio 6 acertos" DECIMAL(14,2),
            "Ganhadores 5 acertos" INTEGER DEFAULT 0,
            "Rateio 5 acertos" DECIMAL(14,2),
            "Ganhadores 4 acertos" INTEGER DEFAULT 0,
            "Rateio 4 acertos" DECIMAL(14,2),
            "Acumulado 6 acertos" BOOLEAN DEFAULT false,
            "Arrecada\u00e7\u00e3o Total" DECIMAL(14,2),
            "Estimativa pr\u00eamio" DECIMAL(14,2),
            "Acumulado Sorteio Especial Mega da Virada" BOOLEAN DEFAULT false,
            "Observa\u00e7\u00e3o" TEXT,
            coletado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            hash_combinacao VARCHAR(64) NOT NULL,
            dezenas_ordenadas INTEGER[] NOT NULL,
            CONSTRAINT uq_megasena_concurso UNIQUE ("Concurso"),
            CONSTRAINT uq_megasena_hash UNIQUE (hash_combinacao)
        );
    """)
    op.create_index("idx_megasena_data", "loterias_resultados_megasena", ["Data do Sorteio"])
    op.create_index("idx_megasena_dezenas", "loterias_resultados_megasena", ["dezenas_ordenadas"], postgresql_using="gin")

    # ─── loterias_resultados_lotofacil ────────────────────────────
    op.execute("""
        CREATE TABLE loterias_resultados_lotofacil (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            "Concurso" INTEGER NOT NULL,
            "Data Sorteio" DATE NOT NULL,
            "Bola1" INTEGER NOT NULL,  "Bola2" INTEGER NOT NULL,
            "Bola3" INTEGER NOT NULL,  "Bola4" INTEGER NOT NULL,
            "Bola5" INTEGER NOT NULL,  "Bola6" INTEGER NOT NULL,
            "Bola7" INTEGER NOT NULL,  "Bola8" INTEGER NOT NULL,
            "Bola9" INTEGER NOT NULL,  "Bola10" INTEGER NOT NULL,
            "Bola11" INTEGER NOT NULL, "Bola12" INTEGER NOT NULL,
            "Bola13" INTEGER NOT NULL, "Bola14" INTEGER NOT NULL,
            "Bola15" INTEGER NOT NULL,
            "Ganhadores 15 acertos" INTEGER DEFAULT 0,
            "Cidade / UF" VARCHAR(150),
            "Rateio 15 acertos" DECIMAL(14,2),
            "Ganhadores 14 acertos" INTEGER DEFAULT 0,
            "Rateio 14 acertos" DECIMAL(14,2),
            "Ganhadores 13 acertos" INTEGER DEFAULT 0,
            "Rateio 13 acertos" DECIMAL(14,2),
            "Ganhadores 12 acertos" INTEGER DEFAULT 0,
            "Rateio 12 acertos" DECIMAL(14,2),
            "Ganhadores 11 acertos" INTEGER DEFAULT 0,
            "Rateio 11 acertos" DECIMAL(14,2),
            "Acumulado 15 acertos" BOOLEAN DEFAULT false,
            "Arrecadacao Total" DECIMAL(14,2),
            "Estimativa Premio" DECIMAL(14,2),
            "Acumulado sorteio especial Lotofacil da Independencia" BOOLEAN DEFAULT false,
            "Observacao" TEXT,
            coletado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            hash_combinacao VARCHAR(64) NOT NULL,
            dezenas_ordenadas INTEGER[] NOT NULL,
            CONSTRAINT uq_lotofacil_concurso UNIQUE ("Concurso"),
            CONSTRAINT uq_lotofacil_hash UNIQUE (hash_combinacao)
        );
    """)
    op.create_index("idx_lotofacil_data", "loterias_resultados_lotofacil", ["Data Sorteio"])
    op.create_index("idx_lotofacil_dezenas", "loterias_resultados_lotofacil", ["dezenas_ordenadas"], postgresql_using="gin")

    # ─── loterias_resultados_quina ────────────────────────────────
    op.execute("""
        CREATE TABLE loterias_resultados_quina (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            "Concurso" INTEGER NOT NULL,
            "Data Sorteio" DATE NOT NULL,
            "Bola1" INTEGER NOT NULL, "Bola2" INTEGER NOT NULL,
            "Bola3" INTEGER NOT NULL, "Bola4" INTEGER NOT NULL,
            "Bola5" INTEGER NOT NULL,
            "Ganhadores 5 acertos" INTEGER DEFAULT 0,
            "Cidade / UF" VARCHAR(150),
            "Rateio 5 acertos" DECIMAL(14,2),
            "Ganhadores 4 acertos" INTEGER DEFAULT 0,
            "Rateio 4 acertos" DECIMAL(14,2),
            "Ganhadores 3 acertos" INTEGER DEFAULT 0,
            "Rateio 3 acertos" DECIMAL(14,2),
            "Ganhadores 2 acertos" INTEGER DEFAULT 0,
            "Rateio 2 acertos" DECIMAL(14,2),
            "Acumulado 5 acertos" BOOLEAN DEFAULT false,
            "Arrecadacao Total" DECIMAL(14,2),
            "Estimativa Premio" DECIMAL(14,2),
            "Acumulado Sorteio Especial Quina de Sao Joao" BOOLEAN DEFAULT false,
            "Observacao" TEXT,
            coletado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            hash_combinacao VARCHAR(64) NOT NULL,
            dezenas_ordenadas INTEGER[] NOT NULL,
            CONSTRAINT uq_quina_concurso UNIQUE ("Concurso"),
            CONSTRAINT uq_quina_hash UNIQUE (hash_combinacao)
        );
    """)
    op.create_index("idx_quina_data", "loterias_resultados_quina", ["Data Sorteio"])
    op.create_index("idx_quina_dezenas", "loterias_resultados_quina", ["dezenas_ordenadas"], postgresql_using="gin")

    # ─── loterias_resultados_duplasena ────────────────────────────
    op.execute("""
        CREATE TABLE loterias_resultados_duplasena (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            "Concurso" INTEGER NOT NULL,
            "Data Sorteio" DATE NOT NULL,
            "Bola1 sorteio 1" INTEGER NOT NULL,
            "Bola2 sorteio 1" INTEGER NOT NULL,
            "Bola3 sorteio 1" INTEGER NOT NULL,
            "Bola4 Sorteio 1" INTEGER NOT NULL,
            "Bola5 sorteio 1" INTEGER NOT NULL,
            "Bola6 sorteio 1" INTEGER NOT NULL,
            "Ganhadores 6 acertos  Sorteio 1" INTEGER DEFAULT 0,
            "Cidade / UF" VARCHAR(150),
            "Rateio 6 acertos  Sorteio 1" DECIMAL(14,2),
            "Ganhadores 5 acertos Sorteio 1" INTEGER DEFAULT 0,
            "Rateio 5 acertos Sorteio 1" DECIMAL(14,2),
            "Ganhadores 4 acertos Sorteio 1" INTEGER DEFAULT 0,
            "Rateio 4 acertos Sorteio 1" DECIMAL(14,2),
            "Ganhadores 3 acertos Sorteio 1" INTEGER DEFAULT 0,
            "Rateio 3 acertos Sorteio 1" DECIMAL(14,2),
            "Bola1 sorteio 2" INTEGER NOT NULL,
            "Bola2 sorteio 2" INTEGER NOT NULL,
            "Bola3 sorteio 2" INTEGER NOT NULL,
            "Bola4 Sorteio 2" INTEGER NOT NULL,
            "Bola5 sorteio 2" INTEGER NOT NULL,
            "Bola6 sorteio 2" INTEGER NOT NULL,
            "Ganhadores 6 acertos Sorteio2" INTEGER DEFAULT 0,
            "Rateio 6 acertos  Sorteio 2" DECIMAL(14,2),
            "Ganhadores 5 acertos Sorteio2" INTEGER DEFAULT 0,
            "Rateio 5 acertos Sorteio 2" DECIMAL(14,2),
            "Ganhadores 4 acertos Sorteio2" INTEGER DEFAULT 0,
            "Rateio 4 acertos Sorteio 2" DECIMAL(14,2),
            "Ganhadores 3 acertos Sorteio2" INTEGER DEFAULT 0,
            "Rateio 3 acertos Sorteio 2" DECIMAL(14,2),
            "Acumulado 6 acertos sorteio 1" BOOLEAN DEFAULT false,
            "Arrecadacao Total" DECIMAL(14,2),
            "Estimativa Premio" DECIMAL(14,2),
            "Acumulado Sorteio Especial Dupla de Pascoa" BOOLEAN DEFAULT false,
            "Observacao" TEXT,
            coletado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            hash_combinacao VARCHAR(64) NOT NULL,
            dezenas_ordenadas INTEGER[] NOT NULL,
            CONSTRAINT uq_duplasena_concurso UNIQUE ("Concurso"),
            CONSTRAINT uq_duplasena_hash UNIQUE (hash_combinacao)
        );
    """)
    op.create_index("idx_duplasena_data", "loterias_resultados_duplasena", ["Data Sorteio"])
    op.create_index("idx_duplasena_dezenas", "loterias_resultados_duplasena", ["dezenas_ordenadas"], postgresql_using="gin")

    # ─── loterias_resultados_diadesorte ───────────────────────────
    op.execute("""
        CREATE TABLE loterias_resultados_diadesorte (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            "Concurso" INTEGER NOT NULL,
            "Data Sorteio" DATE NOT NULL,
            "Bola1" INTEGER NOT NULL, "Bola2" INTEGER NOT NULL,
            "Bola3" INTEGER NOT NULL, "Bola4" INTEGER NOT NULL,
            "Bola5" INTEGER NOT NULL, "Bola6" INTEGER NOT NULL,
            "Bola7" INTEGER NOT NULL,
            "M\u00eas da Sorte" INTEGER NOT NULL,
            "Ganhadores 7 acertos" INTEGER DEFAULT 0,
            "Cidade / UF" VARCHAR(150),
            "Rateio 7 acertos" DECIMAL(14,2),
            "Ganhadores 6 acertos" INTEGER DEFAULT 0,
            "Rateio 6 acertos" DECIMAL(14,2),
            "Ganhadores 5 acertos" INTEGER DEFAULT 0,
            "Rateio 5 acertos" DECIMAL(14,2),
            "Ganhadores 4 acertos" INTEGER DEFAULT 0,
            "Rateio 4 acertos" DECIMAL(14,2),
            "Ganhadores mes da sorte" INTEGER DEFAULT 0,
            "Rateio mes da sorte" DECIMAL(14,2),
            "Acumulado 7 acertos" BOOLEAN DEFAULT false,
            "Arrecadacao Total" DECIMAL(14,2),
            "Estimativa Premio" DECIMAL(14,2),
            "Observacao" TEXT,
            coletado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            hash_combinacao VARCHAR(64) NOT NULL,
            dezenas_ordenadas INTEGER[] NOT NULL,
            CONSTRAINT uq_diadesorte_concurso UNIQUE ("Concurso"),
            CONSTRAINT uq_diadesorte_hash UNIQUE (hash_combinacao)
        );
    """)
    op.create_index("idx_diadesorte_data", "loterias_resultados_diadesorte", ["Data Sorteio"])
    op.create_index("idx_diadesorte_dezenas", "loterias_resultados_diadesorte", ["dezenas_ordenadas"], postgresql_using="gin")

    # ─── loterias_resultados_federal ──────────────────────────────
    op.execute("""
        CREATE TABLE loterias_resultados_federal (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            "Extra\u00e7\u00e3o" INTEGER NOT NULL,
            "Data Sorteio" DATE NOT NULL,
            "1\u00ba pr\u00eamio" INTEGER NOT NULL,
            "Valor 1\u00ba pr\u00eamio" DECIMAL(14,2),
            "2\u00ba pr\u00eamio" INTEGER NOT NULL,
            "Valor 2\u00ba pr\u00eamio" DECIMAL(14,2),
            "3\u00ba pr\u00eamio" INTEGER NOT NULL,
            "Valor 3\u00ba pr\u00eamio" DECIMAL(14,2),
            "4\u00ba pr\u00eamio" INTEGER NOT NULL,
            "Valor 4\u00ba pr\u00eamio" DECIMAL(14,2),
            "5\u00ba pr\u00eamio" INTEGER NOT NULL,
            "Valor 5\u00ba pr\u00eamio" DECIMAL(14,2),
            coletado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            hash_extracao VARCHAR(64) NOT NULL,
            CONSTRAINT uq_federal_extracao UNIQUE ("Extra\u00e7\u00e3o"),
            CONSTRAINT uq_federal_hash UNIQUE (hash_extracao)
        );
    """)
    op.create_index("idx_federal_data", "loterias_resultados_federal", ["Data Sorteio"])

    # ─── loterias_resultados_lotomania ────────────────────────────
    op.execute("""
        CREATE TABLE loterias_resultados_lotomania (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            "Concurso" INTEGER NOT NULL,
            "Data Sorteio" DATE NOT NULL,
            "Bola1" INTEGER NOT NULL,  "Bola2" INTEGER NOT NULL,
            "Bola3" INTEGER NOT NULL,  "Bola4" INTEGER NOT NULL,
            "Bola5" INTEGER NOT NULL,  "Bola6" INTEGER NOT NULL,
            "Bola7" INTEGER NOT NULL,  "Bola8" INTEGER NOT NULL,
            "Bola9" INTEGER NOT NULL,  "Bola10" INTEGER NOT NULL,
            "Bola11" INTEGER NOT NULL, "Bola12" INTEGER NOT NULL,
            "Bola13" INTEGER NOT NULL, "Bola14" INTEGER NOT NULL,
            "Bola15" INTEGER NOT NULL, "Bola16" INTEGER NOT NULL,
            "Bola17" INTEGER NOT NULL, "Bola18" INTEGER NOT NULL,
            "Bola19" INTEGER NOT NULL, "Bola20" INTEGER NOT NULL,
            "Ganhadores 20 acertos" INTEGER DEFAULT 0,
            "Cidade / UF" VARCHAR(150),
            "Rateio 20 acertos" DECIMAL(14,2),
            "Ganhadores 19 acertos" INTEGER DEFAULT 0,
            "Rateio 19 acertos" DECIMAL(14,2),
            "Ganhadores 18 acertos" INTEGER DEFAULT 0,
            "Rateio 18 acertos" DECIMAL(14,2),
            "Ganhadores 17 acertos" INTEGER DEFAULT 0,
            "Rateio 17 acertos" DECIMAL(14,2),
            "Ganhadores 16 acertos" INTEGER DEFAULT 0,
            "Rateio 16 acertos" DECIMAL(14,2),
            "Ganhadores 15 acertos" INTEGER DEFAULT 0,
            "Rateio 15 acertos" DECIMAL(14,2),
            "Ganhadores Nenhum Numero" INTEGER DEFAULT 0,
            "Rateio Nenhum Numero" DECIMAL(14,2),
            "Acumulado 20 acertos" BOOLEAN DEFAULT false,
            "Arrecadacao Total" DECIMAL(14,2),
            "Estimativa Premio" DECIMAL(14,2),
            "Observacao" TEXT,
            coletado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            hash_combinacao VARCHAR(64) NOT NULL,
            dezenas_ordenadas INTEGER[] NOT NULL,
            CONSTRAINT uq_lotomania_concurso UNIQUE ("Concurso"),
            CONSTRAINT uq_lotomania_hash UNIQUE (hash_combinacao)
        );
    """)
    op.create_index("idx_lotomania_data", "loterias_resultados_lotomania", ["Data Sorteio"])
    op.create_index("idx_lotomania_dezenas", "loterias_resultados_lotomania", ["dezenas_ordenadas"], postgresql_using="gin")

    # ─── loterias_resultados_timemania ────────────────────────────
    op.execute("""
        CREATE TABLE loterias_resultados_timemania (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            "Concurso" INTEGER NOT NULL,
            "Data Sorteio" DATE NOT NULL,
            "Bola1" INTEGER NOT NULL, "Bola2" INTEGER NOT NULL,
            "Bola3" INTEGER NOT NULL, "Bola4" INTEGER NOT NULL,
            "Bola5" INTEGER NOT NULL, "Bola6" INTEGER NOT NULL,
            "Bola7" INTEGER NOT NULL,
            "Time Coracao" INTEGER NOT NULL,
            "Ganhadores 7 acertos" INTEGER DEFAULT 0,
            "Cidade / UF" VARCHAR(150),
            "Rateio 7 acertos" DECIMAL(14,2),
            "Ganhadores 6 acertos" INTEGER DEFAULT 0,
            "Rateio 6 acertos" DECIMAL(14,2),
            "Ganhadores 5 acertos" INTEGER DEFAULT 0,
            "Rateio 5 acertos" DECIMAL(14,2),
            "Ganhadores 4 acertos" INTEGER DEFAULT 0,
            "Rateio 4 acertos" DECIMAL(14,2),
            "Ganhadores 3 acertos" INTEGER DEFAULT 0,
            "Rateio 3 acertos" DECIMAL(14,2),
            "Ganhadores Time Coracao" INTEGER DEFAULT 0,
            "Rateio Time Coracao" DECIMAL(14,2),
            "Acumulado 7 acertos" BOOLEAN DEFAULT false,
            "Arrecadacao Total" DECIMAL(14,2),
            "Estimativa Premio" DECIMAL(14,2),
            "Observacao" TEXT,
            coletado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            hash_combinacao VARCHAR(64) NOT NULL,
            dezenas_ordenadas INTEGER[] NOT NULL,
            CONSTRAINT uq_timemania_concurso UNIQUE ("Concurso"),
            CONSTRAINT uq_timemania_hash UNIQUE (hash_combinacao)
        );
    """)
    op.create_index("idx_timemania_data", "loterias_resultados_timemania", ["Data Sorteio"])
    op.create_index("idx_timemania_dezenas", "loterias_resultados_timemania", ["dezenas_ordenadas"], postgresql_using="gin")

    # ─── loterias_resultados_maismilionaria ────────────────────────
    op.execute("""
        CREATE TABLE loterias_resultados_maismilionaria (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            "Concurso" INTEGER NOT NULL,
            "Data Sorteio" DATE NOT NULL,
            "Bola1" INTEGER NOT NULL,  "Bola2" INTEGER NOT NULL,
            "Bola3" INTEGER NOT NULL,  "Bola4" INTEGER NOT NULL,
            "Bola5" INTEGER NOT NULL,  "Bola6" INTEGER NOT NULL,
            "Trevo1" INTEGER NOT NULL,
            "Trevo2" INTEGER NOT NULL,
            "Ganhadores 6 Numeros + 2 Trevos" INTEGER DEFAULT 0,
            "Cidade / UF" VARCHAR(150),
            "Rateio 6 acertos + 2 Trevos" DECIMAL(14,2),
            "Ganhadores 6 acertos + 1 ou nenhum Trevo" INTEGER DEFAULT 0,
            "Rateio 6 acertos + 1 ou nenhum Trevo" DECIMAL(14,2),
            "Ganhadores 5 acertos + 2 Trevos" INTEGER DEFAULT 0,
            "Rateio 5 acertos + 2 Trevos" DECIMAL(14,2),
            "Ganhadores 5 acertos + 1 ou nenhum Trevo" INTEGER DEFAULT 0,
            "Rateio 5 acertos + 1 ou nenhum Trevo" DECIMAL(14,2),
            "Ganhadores 4 acertos + 2 Trevos" INTEGER DEFAULT 0,
            "Rateio 4 acertos + 2 Trevos" DECIMAL(14,2),
            "Ganhadores 4 acertos + 1 ou nenhum Trevo" INTEGER DEFAULT 0,
            "Rateio 4 acertos + 1 ou nenhum Trevo" DECIMAL(14,2),
            "Ganhadores 3 acertos + 2 Trevos" INTEGER DEFAULT 0,
            "Rateio 3 acertos + 2 Trevos" DECIMAL(14,2),
            "Ganhadores 3 acertos + 1 Trevo" INTEGER DEFAULT 0,
            "Rateio 3 acertos + 1 Trevo" DECIMAL(14,2),
            "Ganhadores 2 acertos + 2 Trevos" INTEGER DEFAULT 0,
            "Rateio 2 acertos + 2 Trevos" DECIMAL(14,2),
            "Ganhadores 2 acertos + 1 Trevo" INTEGER DEFAULT 0,
            "Rateio 2 acertos + 1 Trevo" DECIMAL(14,2),
            "Acumulado 6 acertos + 2 Trevos" BOOLEAN DEFAULT false,
            "Arrecadacao Total" DECIMAL(14,2),
            "Estimativa Premio" DECIMAL(14,2),
            "Observacao" TEXT,
            coletado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            hash_combinacao VARCHAR(64) NOT NULL,
            dezenas_ordenadas INTEGER[] NOT NULL,
            trevos_ordenados INTEGER[] NOT NULL,
            CONSTRAINT uq_maismilionaria_concurso UNIQUE ("Concurso"),
            CONSTRAINT uq_maismilionaria_hash UNIQUE (hash_combinacao)
        );
    """)
    op.create_index("idx_maismilionaria_data", "loterias_resultados_maismilionaria", ["Data Sorteio"])
    op.create_index("idx_maismilionaria_dezenas", "loterias_resultados_maismilionaria", ["dezenas_ordenadas"], postgresql_using="gin")

    # ─── loterias_resultados_supersete ─────────────────────────────
    op.execute("""
        CREATE TABLE loterias_resultados_supersete (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            "Concurso" INTEGER NOT NULL,
            "Data Sorteio" DATE NOT NULL,
            "Coluna 1" INTEGER NOT NULL,
            "Coluna 2" INTEGER NOT NULL,
            "Coluna 3" INTEGER NOT NULL,
            "Coluna 4" INTEGER NOT NULL,
            "Coluna 5" INTEGER NOT NULL,
            "Coluna 6" INTEGER NOT NULL,
            "Coluna 7" INTEGER NOT NULL,
            "Ganhadores 7 acertos" INTEGER DEFAULT 0,
            "Cidade / UF" VARCHAR(150),
            "Rateio 7 acertos" DECIMAL(14,2),
            "Ganhadores 6 acertos" INTEGER DEFAULT 0,
            "Rateio 6 acertos" DECIMAL(14,2),
            "Ganhadores 5 acertos" INTEGER DEFAULT 0,
            "Rateio 5 acertos" DECIMAL(14,2),
            "Ganhadores 4 acertos" INTEGER DEFAULT 0,
            "Rateio 4 acertos" DECIMAL(14,2),
            "Ganhadores 3 acertos" INTEGER DEFAULT 0,
            "Rateio 3 acertos" DECIMAL(14,2),
            "Acumulado 7 acertos" BOOLEAN DEFAULT false,
            "Arrecadacao Total" DECIMAL(14,2),
            "Estimativa Premio" DECIMAL(14,2),
            "Observacao" TEXT,
            coletado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            hash_combinacao VARCHAR(64) NOT NULL,
            CONSTRAINT uq_supersete_concurso UNIQUE ("Concurso"),
            CONSTRAINT uq_supersete_hash UNIQUE (hash_combinacao)
        );
    """)
    op.create_index("idx_supersete_data", "loterias_resultados_supersete", ["Data Sorteio"])

    # ─── loterias_resultados_loteca ────────────────────────────────
    op.execute("""
        CREATE TABLE loterias_resultados_loteca (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            "Concurso" INTEGER NOT NULL,
            "Data Sorteio" DATE NOT NULL,
            "Coluna 1" INTEGER NOT NULL,
            "Coluna 2" INTEGER NOT NULL,
            "Coluna 3" INTEGER NOT NULL,
            "Coluna 4" INTEGER NOT NULL,
            "Coluna 5" INTEGER NOT NULL,
            "Coluna 6" INTEGER NOT NULL,
            "Coluna 7" INTEGER NOT NULL,
            "Ganhadores 7 acertos" INTEGER DEFAULT 0,
            "Cidade / UF" VARCHAR(150),
            "Rateio 7 acertos" DECIMAL(14,2),
            "Ganhadores 6 acertos" INTEGER DEFAULT 0,
            "Rateio 6 acertos" DECIMAL(14,2),
            "Ganhadores 5 acertos" INTEGER DEFAULT 0,
            "Rateio 5 acertos" DECIMAL(14,2),
            "Ganhadores 4 acertos" INTEGER DEFAULT 0,
            "Rateio 4 acertos" DECIMAL(14,2),
            "Ganhadores 3 acertos" INTEGER DEFAULT 0,
            "Rateio 3 acertos" DECIMAL(14,2),
            "Acumulado 7 acertos" BOOLEAN DEFAULT false,
            "Arrecadacao Total" DECIMAL(14,2),
            "Estimativa Premio" DECIMAL(14,2),
            "Observacao" TEXT,
            coletado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            hash_combinacao VARCHAR(64) NOT NULL,
            CONSTRAINT uq_loteca_concurso UNIQUE ("Concurso"),
            CONSTRAINT uq_loteca_hash UNIQUE (hash_combinacao)
        );
    """)
    op.create_index("idx_loteca_data", "loterias_resultados_loteca", ["Data Sorteio"])


def downgrade() -> None:
    tables = [
        "loterias_resultados_megasena",
        "loterias_resultados_lotofacil",
        "loterias_resultados_quina",
        "loterias_resultados_duplasena",
        "loterias_resultados_diadesorte",
        "loterias_resultados_federal",
        "loterias_resultados_lotomania",
        "loterias_resultados_timemania",
        "loterias_resultados_maismilionaria",
        "loterias_resultados_supersete",
        "loterias_resultados_loteca",
        "audit_log",
    ]
    for table in tables:
        op.drop_table(table)
