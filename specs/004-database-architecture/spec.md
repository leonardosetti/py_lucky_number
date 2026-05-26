# Feature Specification: Database Architecture

**Feature Branch**: `004-database-architecture`
**Created**: 2026-05-14
**Status**: Draft
**Input**: Arquitetura de banco de dados relacional para o sistema Lucky Number,
incluindo 4 ambientes, migrações versionadas, 27 tabelas, segurança OWASP/CWE/LGPD,
e extensões de auditoria e performance.
**Version**: 2.4

---

## 1. Technical Overview

Esta especificação define a arquitetura completa do banco de dados PostgreSQL do
sistema Lucky Number, consolidando:

- **4 ambientes isolados**: produção, testes, desenvolvimento e mirror
- **28 tabelas**: 18 entidades de domínio/auditoria + 10 tabelas `loterias_resultados_{jogo}`
- **10 tabelas `loterias_resultados_{jogo}`** (uma por jogo CEF)
- **Migrações versionadas** com SQLAlchemy 2.0 + Alembic
- **Segurança**: OWASP A05/A07, CWE-89/20/200/400/73, LGPD
- **Roles segregadas**: `app_user`, `app_agent`, `migration_user`
- **Índices BRIN** em tabelas de alta volumetria
- **Backup**: pgBackRest com criptografia e verificação

---

## 2. Relationship with Other Specs

Esta spec é a fundação sobre a qual todas as demais specs se apoiam:

| Spec | Dependência |
|---|---|
| 001 – Bet Promises | Tabela `promessas`, `combinacoes_salvas` |
| 002 – Feature Toggles | Tabela `feature_toggles` |
| 003 – System Management | Tabelas `users`, `roles`, `permissions`, `audit_log`, etc. |
| 005 – Backup Automation | Tabela `backup_history`, política de retenção |
| 006 – Environment Mgmt | 4 ambientes, CI/CD, migrações |
| 007–017 – Data Collectors | 10 tabelas `loterias_resultados_{jogo}` |
| 019 – Export & Share | Tabelas `share_links`, fila de exportação |
| 020 – Web Frontend | Consome API sobre este schema |
| 021 – Mobile App | Consome API sobre este schema |
| 022 – Apostador Registration | Estende `users` com campos de perfil |
| 023 – Apostador Mobile Registration | Estende `users` com push tokens |
| 024–026 – Password Recovery | Tabelas `password_reset_tokens`, `activation_codes` |

---

## 3. Database Environments

| Ambiente | Propósito | Dados | Refresh |
|---|---|---|---|
| **Production** | Operação ao vivo | Reais | N/A |
| **Test** | Testes automatizados | Seed mínimo | Recriado por execução |
| **Development** | Desenvolvimento local | Sintéticos | Sob demanda |
| **Mirror** | Performance/load testing | Sintéticos (volume produção) | Recriação noturna |

---

## 4. Behavior

### 4.1 Environment Isolation
- Each environment MUST have its own PostgreSQL instance.
- Connection string via `DATABASE_URL` env var, never hardcoded.
- Test DB: drop + recreate before each test suite.
- Mirror DB: synthetic data only, never real production data.

### 4.2 Migration History
- Every Alembic migration execution (upgrade and downgrade) recorded in `migrations_history`.
- On failure, rollback recorded with `action = 'downgrade'`.

### 4.3 Feature Toggle Audit
- Every state change in `feature_toggles` inserts a row in `feature_toggle_audit`.
- Captures: toggle ID, changer UUID, previous/new state, origin IP hash.
- INSERT-only (immutable).

### 4.4 Performance Snapshots
- Celery Beat task every 15min collects top N queries from `pg_stat_statements`.
- Additional types: `pg_stat_activity`, `pg_stat_user_tables`.
- Partitioned by month on `created_at`.

### 4.5 Backup
- Production backups via pgBackRest with encryption, compression, verification.
- History recorded in `backup_history`.

### 4.6 Hash Lookup Strategy

A verificação de combinações já sorteadas (Princípio I) é feita diretamente
nas tabelas `loterias_resultados_{jogo}`, que já possuem `hash_combinacao`
com constraint UNIQUE (índice BTree). Cada jogo consulta sua própria tabela:
Mega-Sena → `loterias_resultados_megasena`, Lotofácil →
`loterias_resultados_lotofacil`, etc. Não existe tabela
`sorteios_historicos` centralizada — cada jogo gerencia seu próprio índice
de combinações.

### 4.7 Naming Convention for `loterias_resultados_*`
As colunas das tabelas `loterias_resultados_{jogo}` usam EXATAMENTE os nomes dos
cabeçalhos da planilha oficial da CEF, incluindo espaços, acentos e caracteres
especiais (ex: "Data do Sorteio", "Ganhadores 6 acertos", "1º prêmio"). Isso
garante mapeamento direto no parse com Polars e facilita a depuração.
Consequência: todo SQL contra estas tabelas DEVE usar aspas duplas.

---

## 5. User Scenarios & Testing *(mandatory)*

### User Story 1 — Developer Manages 4 Database Environments (Priority: P1)

**Acceptance Scenarios**:

1. **Given** the application is configured, **When** running in `development` mode,
   **Then** the system connects exclusively to the development database.
2. **Given** the CI/CD pipeline, **When** automated tests run, **Then** they use
   the test database recreated from scratch.
3. **Given** the mirror configured, **When** heavy queries are executed, **Then**
   they are directed to the mirror (never production).

### User Story 2 — Admin Validates Data Compliance (LGPD/OWASP) (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a registered user, **When** the admin inspects the database, **Then**
   `senha_hash` contains bcrypt, never plain text.
2. **Given** an API response, **When** inspected, **Then** `senha_hash`, tokens
   and `ip_hash` are never present.
3. **Given** a deletion request (right to be forgotten), **When** processed,
   **Then** personal data is anonymized within 48 hours.

### User Story 3 — CI/CD Pipeline Runs Safe Migrations (Priority: P2)

**Acceptance Scenarios**:

1. **Given** a new migration in the repository, **When** the pipeline runs for dev,
   **Then** the migration is applied automatically.
2. **Given** the same migration, **When** the pipeline tries to apply to production,
   **Then** deployment is paused requiring manual approval.
3. **Given** a migration with error, **When** applied, **Then** rollback is executed
   automatically and the pipeline fails with error log.

### User Story 4 — Synthetic Data in Mirror (Priority: P3)

**Acceptance Scenarios**:

1. **Given** the synthetic data generator script, **When** executed against mirror,
   **Then** all tables are populated with realistic fake data.
2. **Given** the populated mirror, **When** a complex query runs, **Then** response
   time is within 20% of expected production performance.

### User Story 5 — Feature Toggle Audit Trail (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a feature toggle changed by admin, **When** the audit log is queried,
   **Then** `feature_toggle_audit` contains toggle UUID, changer UUID, previous
   state, new state, and IP hash.
2. **Given** an unauthorized toggle change, **When** investigated, **Then** the
   audit trail contains the complete change history.

### User Story 6 — DBA Monitors Performance (Priority: P2)

**Acceptance Scenarios**:

1. **Given** the performance collector configured, **When** it runs every 15 minutes,
   **Then** a snapshot of the top 10 slowest queries is inserted.
2. **Given** historical snapshots exist, **When** analyzed, **Then** trends in
   query performance can be identified over time.

### User Story 7 — Admin Reviews Migration History (Priority: P2)

**Acceptance Scenarios**:

1. **Given** a successful migration, **When** `migrations_history` is queried,
   **Then** a row exists with `action = 'upgrade'`, `duration_ms`, and `executed_by`.
2. **Given** a failed migration with rollback, **When** queried, **Then** two rows
   exist: one `upgrade` (failed) and one `downgrade` (rollback).

---

## 6. Database Schema

### 6.1 Core Tables (from specs 002, 003, 001)

#### `feature_toggles`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `slug` | VARCHAR(100) | NOT NULL, UNIQUE |
| `nome` | VARCHAR(150) | NOT NULL |
| `descricao` | TEXT | NULLABLE |
| `ativa` | BOOLEAN | NOT NULL, DEFAULT false |
| `version` | INTEGER | NOT NULL, DEFAULT 1 |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

#### `users`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `nome` | VARCHAR(255) | NOT NULL |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE |
| `senha_hash` | VARCHAR(255) | NOT NULL (bcrypt cost 12) |
| `role_id` | UUID | NOT NULL, FK → roles.id, ON DELETE RESTRICT |
| `regiao` | VARCHAR(100) | NULLABLE |
| `ativo` | BOOLEAN | NOT NULL, DEFAULT true |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| `deleted_at` | TIMESTAMPTZ | NULLABLE (soft delete) |
| `cpf` | VARCHAR(11) | NULLABLE, UNIQUE (Brazilian taxpayer ID) |
| `telefone` | VARCHAR(20) | NULLABLE (BR format, indexed) |
| `telefone_pais` | VARCHAR(5) | NULLABLE (country code, e.g., "+55") |
| `data_nascimento` | DATE | NULLABLE |
| `nome_completo` | VARCHAR(255) | NULLABLE |
| `logradouro` | VARCHAR(255) | NULLABLE |
| `numero` | VARCHAR(20) | NULLABLE |
| `complemento` | VARCHAR(100) | NULLABLE |
| `bairro` | VARCHAR(100) | NULLABLE |
| `cidade` | VARCHAR(100) | NULLABLE |
| `estado` | VARCHAR(50) | NULLABLE |
| `cep` | VARCHAR(10) | NULLABLE |
| `pais` | VARCHAR(50) | NULLABLE, DEFAULT 'Brasil' |
| `email_verificado_em` | TIMESTAMPTZ | NULLABLE |
| `telefone_verificado_em` | TIMESTAMPTZ | NULLABLE |
| `ativado_em` | TIMESTAMPTZ | NULLABLE |
| `codigo_ativacao_hash` | VARCHAR(128) | NULLABLE (SHA-256 do código) |
| `tentativas_ativacao` | INTEGER | NOT NULL, DEFAULT 0 |
| `codigo_ativacao_enviado_em` | TIMESTAMPTZ | NULLABLE |
| `totp_secret` | VARCHAR(64) | NULLABLE (2FA) |
| `codigos_reserva` | JSONB | NULLABLE (10 backup codes) |
| `biometria_habilitada` | BOOLEAN | NOT NULL, DEFAULT false |
| `dispositivo_push_token` | VARCHAR(255) | NULLABLE (FCM/APNs) |

#### `roles`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `nome` | VARCHAR(100) | NOT NULL, UNIQUE |
| `descricao` | TEXT | NOT NULL |
| `parent_role_id` | UUID | NULLABLE, FK → roles.id, ON DELETE RESTRICT |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

#### `permissions`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `slug` | VARCHAR(150) | NOT NULL, UNIQUE |
| `nome` | VARCHAR(150) | NOT NULL |
| `recurso` | VARCHAR(100) | NOT NULL |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

#### `role_permissions`
| Column | Type | Constraints |
|---|---|---|
| `role_id` | UUID | NOT NULL, FK → roles.id, ON DELETE CASCADE |
| `permission_id` | UUID | NOT NULL, FK → permissions.id, ON DELETE CASCADE |
| `granted` | BOOLEAN | NOT NULL, DEFAULT true |
| PK | | (role_id, permission_id) |

#### `combinacoes_salvas`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() |
| `user_id` | UUID | NOT NULL, FK → users.id, ON DELETE CASCADE |
| `jogo` | VARCHAR(50) | NOT NULL |
| `dezenas` | INTEGER[] | NOT NULL |
| `dezenas_por_aposta` | INTEGER | NOT NULL |
| `favorita` | BOOLEAN | NOT NULL, DEFAULT false |
| `hash_combinacao` | VARCHAR(64) | NOT NULL, UNIQUE |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Limite**: Max 200 per user. FIFO: when limit reached, oldest non-favorite
  records are removed to accommodate new inserts.
- **Isolamento**: `user_id` scoped — no user can see another user's records.
- **Notificação**: user is notified when approaching the 200 limit.
- **Índices**: `(user_id, created_at)` (btree), `(user_id, favorita)` (btree),
  `hash_combinacao` (btree, UNIQUE).

#### `promessas`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `user_id` | UUID | NOT NULL, FK → users.id, ON DELETE CASCADE |
| `session_id` | VARCHAR(255) | NULLABLE |
| `titulo` | VARCHAR(200) | NULLABLE |
| `prioridade` | VARCHAR(10) | NOT NULL, CHECK IN ('alta','media','baixa') |
| `valor_total` | DECIMAL(12,2) | NOT NULL |
| `combinacoes_snapshot` | JSONB | NOT NULL |
| `favorita` | BOOLEAN | NOT NULL, DEFAULT false |
| `compartilhavel` | BOOLEAN | NOT NULL, DEFAULT false |
| `hash_compartilhamento` | VARCHAR(64) | NULLABLE, UNIQUE |
| `data_expiracao` | TIMESTAMPTZ | NULLABLE |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Limite FIFO**: Max 50 promessas por usuário. Ao atingir o limite, a
  promessa mais antiga não-favoritada é removida automaticamente.
  Enforcement via application logic, com CHECK constraint como safety net.

#### `system_notifications`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `titulo` | VARCHAR(200) | NOT NULL |
| `mensagem` | TEXT | NOT NULL |
| `prioridade` | VARCHAR(10) | NOT NULL, CHECK IN ('alta','media','baixa') |
| `destinatario_user_id` | UUID | NULLABLE, FK → users.id, ON DELETE SET NULL |
| `destinatario_role_id` | UUID | NULLABLE, FK → roles.id, ON DELETE SET NULL |
| `data_expiracao` | TIMESTAMPTZ | NULLABLE |
| `created_by` | UUID | NOT NULL, FK → users.id, ON DELETE RESTRICT |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

#### `notification_deliveries`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `notification_id` | UUID | NOT NULL, FK → system_notifications.id, ON DELETE CASCADE |
| `user_id` | UUID | NOT NULL, FK → users.id, ON DELETE CASCADE |
| `lida` | BOOLEAN | NOT NULL, DEFAULT false |
| `lida_em` | TIMESTAMPTZ | NULLABLE |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| **UNIQUE** | | (notification_id, user_id) |

#### `usage_events`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `user_id` | UUID | NULLABLE, FK → users.id, ON DELETE SET NULL |
| `session_id` | VARCHAR(255) | NULLABLE |
| `event_type` | VARCHAR(50) | NOT NULL |
| `metadata` | JSONB | NOT NULL, DEFAULT '{}' |
| `regiao` | VARCHAR(100) | NULLABLE |
| `ip_hash` | VARCHAR(64) | NULLABLE (SHA-256 of IP, never raw IP) |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| **Partitioning** | | Monthly on `created_at` |

#### `audit_log`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `admin_id` | UUID | NULLABLE, FK → users.id, ON DELETE SET NULL |
| `acao` | VARCHAR(20) | NOT NULL, CHECK IN ('create','update','delete','clone','toggle') |
| `entidade_tipo` | VARCHAR(50) | NOT NULL |
| `entidade_id` | UUID | NOT NULL |
| `detalhes` | JSONB | NOT NULL, DEFAULT '{}' |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| **Immutable** | | INSERT only |
| **Partitioning** | | Monthly on `created_at` |

### 6.2 Lottery Results Tables (10 tables, one per game)

Padrão: `loterias_resultados_{jogo}`. Cada tabela contém colunas específicas
da mecânica do jogo. Ver specs 007–017 para definições detalhadas de colunas.

Todas as tabelas `loterias_resultados_{jogo}` compartilham:
- `id` UUID PK
- Coluna-chave do concurso (nome varia por jogo):
  - `Concurso` INTEGER UNIQUE — para todos os jogos EXCETO Federal
  - `Extração` INTEGER UNIQUE — para Federal (spec 012)
- `hash_combinacao` VARCHAR(64) UNIQUE — exceto Federal, que usa `hash_extracao`
  Este hash é usado para consulta O(1) de combinações já sorteadas (Princípio I).
- `coletado_em` TIMESTAMPTZ
- Índice GIN em `dezenas_ordenadas` — **exceto** Federal, Super Sete e Loteca
  (estes jogos não possuem bolas sorteadas, apenas prêmios/colunas)

### 6.3 Audit & Performance Tables

#### `migrations_history`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `revision` | VARCHAR(20) | NOT NULL |
| `action` | VARCHAR(20) | NOT NULL, CHECK IN ('upgrade', 'downgrade') |
| `duration_ms` | INTEGER | NOT NULL |
| `executed_by` | VARCHAR(100) | NOT NULL |
| `log_output` | TEXT | NULLABLE |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| **Immutable** | | INSERT only |

#### `feature_toggle_audit`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `feature_toggle_id` | UUID | NOT NULL, FK → feature_toggles.id, ON DELETE CASCADE |
| `changed_by` | UUID | NULLABLE, FK → users.id, ON DELETE SET NULL |
| `previous_state` | BOOLEAN | NOT NULL |
| `new_state` | BOOLEAN | NOT NULL |
| `source_ip_hash` | VARCHAR(64) | NULLABLE |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| **Immutable** | | INSERT only |

#### `password_reset_tokens`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `user_id` | UUID | NOT NULL, FK → users.id, ON DELETE CASCADE |
| `token_hash` | VARCHAR(128) | NOT NULL, UNIQUE (SHA-256 do token) |
| `canal_entrega` | VARCHAR(20) | NOT NULL, CHECK IN ('email','whatsapp') |
| `expires_at` | TIMESTAMPTZ | NOT NULL (20 min após criação) |
| `consumed_at` | TIMESTAMPTZ | NULLABLE (preenchido ao usar) |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Single-use**: Após o consumo, `consumed_at` é preenchido. Tokens com `consumed_at IS NOT NULL` são rejeitados.
- **Expiração**: Tokens com `expires_at < NOW()` são rejeitados.
- **Último token válido**: Se múltiplos tokens forem gerados para o mesmo usuário, apenas o mais recente (não-consumido, não-expirado) é válido. Tokens anteriores são implicitamente invalidados.

#### `activation_codes`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `user_id` | UUID | NOT NULL, FK → users.id, ON DELETE CASCADE |
| `codigo_hash` | VARCHAR(128) | NOT NULL (SHA-256 do código de 6 dígitos) |
| `canal` | VARCHAR(20) | NOT NULL, CHECK IN ('email','sms','whatsapp') |
| `expires_at` | TIMESTAMPTZ | NOT NULL (24h após criação) |
| `tentativas` | INTEGER | NOT NULL, DEFAULT 0 |
| `max_tentativas` | INTEGER | NOT NULL, DEFAULT 5 |
| `consumido_em` | TIMESTAMPTZ | NULLABLE |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Limite de tentativas**: Após `max_tentativas` falhas, o código é invalidado e um novo deve ser solicitado.
- **Expiração**: Códigos expirados (>24h) são rejeitados. A conta pendente associada pode ser removida.

#### `synthetic_data_generation_runs`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `script_name` | VARCHAR(255) | NOT NULL |
| `status` | VARCHAR(20) | NOT NULL, CHECK IN ('running','success','failed') |
| `records_generated` | INTEGER | NULLABLE |
| `duration_ms` | INTEGER | NOT NULL |
| `error_log` | TEXT | NULLABLE |
| `started_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| `finished_at` | TIMESTAMPTZ | NULLABLE |

#### `database_performance_snapshots`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `snapshot_type` | VARCHAR(50) | NOT NULL |
| `metric_data` | JSONB | NOT NULL |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| **Partitioning** | | Monthly on `created_at` |

#### `backup_history`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `tool` | VARCHAR(50) | NOT NULL, DEFAULT 'pgbackrest' |
| `backup_type` | VARCHAR(20) | NOT NULL, CHECK IN ('full','incremental','diff') |
| `status` | VARCHAR(20) | NOT NULL, CHECK IN ('running','success','failed') |
| `size_bytes` | BIGINT | NULLABLE |
| `duration_ms` | INTEGER | NULLABLE |
| `checksum` | VARCHAR(64) | NULLABLE |
| `error_log` | TEXT | NULLABLE |
| `started_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| `finished_at` | TIMESTAMPTZ | NULLABLE |

### 6.4 BRIN Index Coverage

BRIN (Block Range INdex) é escolhido sobre BTree para colunas
`created_at` / `sorteado_em` em tabelas append-only onde o padrão de
consulta primário é busca por intervalo (ex: "eventos do último mês").
BRIN ocupa significativamente menos espaço que BTree em tabelas grandes
e mantém performance adequada para range scans. Tabelas pequenas ou com
consultas de igualdade (PKs, FKs, slugs) continuam usando BTree.

| Tabela | Coluna | Tipo Índice | Rationale |
|---|---|---|---|
| `usage_events` | `created_at` | BRIN | Alta volumetria, consultas por período |
| `audit_log` | `created_at` | BRIN | Alta volumetria, consultas por período |
| `migrations_history` | `created_at` | BRIN | Append-only, consultas por revisão |
| `database_performance_snapshots` | `created_at` | BRIN | Append-only, particionada por mês |

---

## 7. Functional Requirements

### Database Environments
- **FR-001**: System MUST support 4 independent database environments:
  production, test, development, and mirror.
- **FR-002**: Each environment MUST have its own connection string defined
  exclusively via `DATABASE_URL` environment variable, never hardcoded.
- **FR-003**: Test database MUST be recreated from scratch (drop + migrate)
  before each test suite execution.
- **FR-004**: Mirror database MUST be populated exclusively with synthetic
  data, never real production data.

### Schema & Migrations
- **FR-005**: All schema changes MUST be managed via versioned, reversible
  migrations (with `up` and `down` methods).
- **FR-006**: Migrations MUST be applied automatically in dev/test via CI/CD,
  and require manual approval in production.
- **FR-007**: Concurrent migrations MUST use PostgreSQL advisory lock
  (`pg_try_advisory_lock`) to prevent conflicts.
- **FR-008**: Every failed migration MUST execute automatic rollback to
  the previous state.

### Data Integrity & Constraints
- **FR-009**: All foreign keys MUST have `ON DELETE` actions defined
  (RESTRICT, CASCADE, or SET NULL per entity).
- **FR-010**: Critical entity tables (`audit_log`, `migrations_history`,
  `feature_toggle_audit`) MUST be immutable (INSERT only).
- **FR-011**: Each `loterias_resultados_{jogo}` table MUST have a unique
  SHA-256 hash (`hash_combinacao` or `hash_extracao` for Federal) of the
  combination for O(1) lookup across all games.
- **FR-012**: User record deletion MUST use soft delete (`deleted_at` column).
- **FR-013**: `combinacoes_salvas` MUST enforce a limit of 200 records per
  user with FIFO eviction (oldest non-favorite first). User MUST be notified
  when limit is reached. Each user MUST only see their own records.
- **FR-014**: Limit of 50 promises per user MUST be enforced via application
  logic (FIFO: oldest non-favorite removed first), with database CHECK
  constraint as safety net.

### Security & Compliance (OWASP, CWE, LGPD)
- **FR-015**: Passwords MUST be stored exclusively as bcrypt hash
  (minimum cost 12).
- **FR-016**: API MUST NEVER return `senha_hash`, `ip_hash`, or any
  sensitive fields in responses.
- **FR-017**: IP addresses MUST be stored as SHA-256 one-way hash
  (`ip_hash`), never the raw IP.
- **FR-018**: User personal data (name, email) MUST be anonymized within
  48 hours of deletion request (LGPD Art. 18).
- **FR-019**: Mirror database MUST NOT contain real personal data —
  only synthetic data.
- **FR-020**: All database connections MUST use TLS 1.2+ in production
  and mirror.
- **FR-021**: Connection pooling MUST have a configurable maximum limit
  (default 20) to prevent connection exhaustion.
- **FR-022**: Connection strings MUST NEVER be included in logs, traces,
  or error messages returned to the client.
- **FR-023**: The database role used by the application MUST have only
  necessary privileges (least privilege principle): CRUD on application
  tables, no access to other databases or `pg_catalog` beyond required.

### Containerization & CI/CD
- **FR-024**: Database MUST run in a persistent container with a separate
  data volume (`pgdata`).
- **FR-025**: Database container MUST NOT be recreated automatically
  during application deploys — only schema migrations execute.
- **FR-026**: CI/CD pipeline MUST include migration validation step
  (dry-run on test database) before applying to production.
- **FR-027**: Production backups MUST be automated (daily) with 5-year
  retention and off-site storage.

### Session & Cache Infrastructure
- **FR-028**: Anonymous user sessions MUST be stored in Redis with a
  configurable TTL (default 30 days). Session ID MUST be a UUID v4.
- **FR-029**: Application cache for feature toggles (spec 002 FR-008)
  MUST use Redis as backend with configurable TTL (default 60 seconds),
  invalidated on toggle state change.

### Audit & Performance Extensions
- **FR-030**: System MUST record every migration execution (upgrade and
  downgrade) in `migrations_history` with revision, action, duration,
  executor, and log output.
- **FR-031**: System MUST collect performance snapshots from PostgreSQL
  (`pg_stat_statements`, `pg_stat_activity`) every 15 minutes and store
  in `database_performance_snapshots` partitioned by month.
- **FR-032**: Every feature toggle state change MUST be recorded in
  `feature_toggle_audit` with user UUID, IP hash, and previous/new state.
- **FR-033**: Every synthetic data generation run MUST be recorded in
  `synthetic_data_generation_runs` with status, record count, and duration.
- **FR-034**: A database role `app_agent` MUST be created with read-only
  access to `pg_stat_statements` and metric tables for AI agent tooling.
- **FR-035**: A dedicated `migration_user` role MUST be used exclusively
  for DDL operations, without INSERT privileges on application tables.
- **FR-036**: BRIN indexes MUST be used on `created_at` columns of
  high-volume tables to reduce index size and maintain range-scan
  performance.
- **FR-037**: Production backups MUST use pgBackRest for physical backup
  (WAL archiving) with encryption, compression, and integrity verification.
  History recorded in `backup_history`. Logical backups (pg_dump for
  selective export and mirror population) are delegated to the backup-tool
  (spec 005), which is complementary, not redundant.

---

## 8. Role Privileges

| Role | Privileges |
|---|---|
| `app_user` | CRUD on all application tables. No DDL. Minimal `pg_catalog`. |
| `app_agent` | SELECT on `pg_stat_statements`, `database_performance_snapshots`, metric views. |
| `migration_user` | CREATE/ALTER/DROP on schema. No INSERT/UPDATE/DELETE on application tables. |

---

## 9. Mandatory Stack

| Layer | Component |
|---|---|
| ORM / Migrations | SQLAlchemy 2.0 + Alembic |
| Database | PostgreSQL 16+ |
| DB Driver | asyncpg (`copy_from` for bulk insert) |
| Backup | pgBackRest (production) |
| Performance | pg_stat_statements |
| Scheduler | Celery Beat (15min snapshots) |
| Session/Cache | Redis (anonymous sessions + feature toggle cache) |
| Container | Docker + docker-compose |
| Monitoring | Prometheus + Grafana |

---

## 10. Error Handling

| Failure | Action |
|---|---|
| Migration failure | Automatic rollback via Alembic. Record both in `migrations_history`. |
| Performance snapshot failure | Log ERROR. Skip. Retry next cycle. |
| Sync data generation failure | Update status to `failed` with `error_log`. |
| Backup failure | Record in `backup_history`. Retry with backoff. |

---

## 11. Success Criteria *(mandatory)*

- **SC-001**: 4 environments startable with single command (`make db-up`),
  completely isolated.
- **SC-002**: Full test suite (90%+ coverage) runs in under 2 minutes
  against recreated test database.
- **SC-003**: SHA-256 hash lookups in `loterias_resultados_{jogo}` return in
  <5ms with 100k+ records per table.
- **SC-004**: Dashboard loads aggregate metrics in <3s with 1M+ events.
- **SC-005**: No plain-text passwords, raw IPs, or personal data exposed —
  verified by automated scanner.
- **SC-006**: Migrations in dev/test applied in <30s without manual
  intervention.
- **SC-007**: Failed migration rollback completes in <10s without
  corrupting data.
- **SC-008**: Mirror contains 100k+ synthetic records, zero real data.
- **SC-009**: Feature toggle audit contains 100% of state changes,
  immutable and queryable.
- **SC-010**: Performance snapshots collected every 15min with <5%
  database overhead.
- **SC-011**: Failed synthetic data generation always recorded with
  `status = 'failed'` and error log.
- **SC-012**: pgBackRest recovery completes in under 5 minutes for
  10GB database.

---

## 12. Assumptions

- **pg_stat_statements enabled**: Required for performance snapshots.
  Configured in `shared_preload_libraries`.
- **pgBackRest installed**: Production backups with S3-compatible storage.
- **BRIN over BTree**: BRIN for `created_at` on append-only tables; BTree
  for PKs, FKs, slugs (equality lookups).
- **Celery Beat available**: 15-minute snapshot collection as periodic task.
- **Naming convention**: Columns in `loterias_resultados_*` match CEF
  spreadsheet headers exactly (spaces, accents, special chars preserved).
- **Sessão anônima**: Especificado no FR-028. Redis obrigatório.
- **GeoIP**: Region inferred from IP address via MaxMind GeoLite2
  (free database). IPs não identificáveis agrupados como
  "Região não identificada".
- **Engine configuration**: Connection pool size (default 20), health
  check interval, and session factory setup are defined in plan Phase 0
  (`src/lucky_number/database/engine.py`). This spec defines the schema,
  the plan defines the runtime configuration.
- **Specs 019–026**: Export & Share, Web Frontend, Mobile App,
  Registration Flow e Password Recovery podem requerer tabelas adicionais
  não definidas nesta spec (ex: `share_links`, `export_jobs`). Estas serão
  adicionadas quando as respectivas specs forem implementadas.
