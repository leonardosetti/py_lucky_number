/speckit.specify

# Feature Specification: Database Architecture (v2.0)

**Feature Branch**: `004-database-architecture-v2`
**Created**: 2026-05-14
**Status**: Draft
**Input**: User description: "Revisão e extensão da arquitetura de banco de dados para atender aos pilares open‑source, performance e segurança (OWASP, CWE, LGPD), incluindo histórico de migrações, auditoria de feature toggles, métricas de performance, e geração de dados sintéticos rastreável."

## User Scenarios & Testing *(mandatory)*

### User Story 1 – Desenvolvedor Gerencia 4 Ambientes de Banco (Priority: P1)
Como um desenvolvedor do time, quero dispor de 4 ambientes de banco de dados isolados (produção, testes, desenvolvimento, mirror), cada um com seu próprio ciclo de vida e propósito, para que eu possa desenvolver, testar e validar alterações sem risco de corromper dados reais ou impactar usuários finais.

**Acceptance Scenarios**:
1. `Given` a aplicação configurada, `When` o desenvolvedor a executa em modo `development`, `Then` o sistema conecta-se exclusivamente ao banco de desenvolvimento.
2. `Given` a pipeline CI/CD, `When` os testes automatizados rodam, `Then` eles usam o banco de testes recriado do zero a cada execução.
3. `Given` o mirror configurado, `When` consultas pesadas ou testes de carga são executados, `Then` eles são direcionados ao mirror (nunca à produção).

---

### User Story 2 – Administrador Valida Conformidade de Dados (LGPD/OWASP) (Priority: P1)
Como um administrador de segurança, quero garantir que senhas sejam armazenadas com bcrypt (custo 12), dados pessoais sejam anonimizados em até 48h após solicitação de exclusão, e a API nunca exponha campos sensíveis.

**Acceptance Scenarios**:
1. `Given` um usuário registrado, `When` o admin inspeciona o banco, `Then` a coluna `senha_hash` contém bcrypt, nunca texto plano.
2. `Given` uma consulta à API, `When` a resposta é inspecionada, `Then` `senha_hash`, tokens e `ip_hash` nunca estão presentes.
3. `Given` um pedido de exclusão (direito ao esquecimento), `When` processado, `Then` os dados pessoais do usuário são anonimizados em até 48 horas.

---

### User Story 3 – Pipeline CI/CD Executa Migrações com Segurança (Priority: P2)
Como um DevOps, quero que a pipeline de CI/CD aplique migrações automaticamente em dev/test e exija aprovação em produção, com advisory lock e rollback automático em caso de falha.

**Acceptance Scenarios**:
1. `Given` uma nova migração no repositório, `When` a pipeline roda para dev, `Then` a migração é aplicada automaticamente.
2. `Given` a mesma migração, `When` a pipeline tenta aplicar em produção, `Then` o deploy é pausado e exige aprovação manual.
3. `Given` uma migração com erro (ex: violação de constraint), `When` aplicada, `Then` o rollback é executado automaticamente e a pipeline falha com log do erro.

---

### User Story 4 – Desenvolvedor Trabalha com Dados Sintéticos no Mirror (Priority: P3)
Como um analista de performance, quero um banco mirror populado com dados sintéticos realistas e volumosos, com registro detalhado de cada geração, para realizar testes de carga sem expor dados reais.

**Acceptance Scenarios**:
1. `Given` o script gerador de dados sintéticos, `When` executado contra o mirror, `Then` popula todas as tabelas com dados realistas (nomes fictícios, emails fictícios, apostas aleatórias).
2. `Given` o mirror populado, `When` uma query complexa de relatório é executada, `Then` o tempo de resposta é similar ao esperado em produção (diferença máxima de 20%).

---

### User Story 5 – Administrador Audita Mudanças em Feature Toggles (Priority: P1)
Como um administrador de sistema, quero que toda ativação/desativação de feature toggle seja registrada imutavelmente (quem, quando, estado anterior/novo, IP hash), para auditoria de segurança e rastreabilidade de mudanças críticas.

**Acceptance Scenarios**:
1. `Given` um feature toggle alterado, `When` o admin consulta o histórico, `Then` vê o registro com o UUID do usuário, o timestamp e o hash do IP de origem.
2. `Given` uma alteração indevida de toggle, `When` o admin investiga, `Then` a tabela `feature_toggle_audit` contém a trilha completa da mudança.

---

### User Story 6 – DBA Monitora Performance e Diagnostica Gargalos (Priority: P2)
Como um DBA ou administrador, quero armazenar snapshots periódicos das métricas de performance do PostgreSQL (`pg_stat_statements`, `pg_stat_activity`) em tabelas imutáveis, para análise de tendências e otimização de consultas.

**Acceptance Scenarios**:
1. `Given` o coletor de métricas configurado, `When` executado a cada 15 minutos, `Then` insere um snapshot das top 10 queries mais lentas em `database_performance_snapshots`.
2. `Given` um snapshot histórico, `When` uma ferramenta de IA ou um script analisa, `Then` pode gerar recomendações de índices ou ajustes de `postgresql.conf`.

---

### User Story 7 – Administrador Revisa Histórico Completo de Migrações (Priority: P2)
Como um administrador de banco, quero que cada execução de migração (upgrade/downgrade) seja registrada em uma tabela imutável com duração, status e log, para auditoria e diagnóstico de problemas.

**Acceptance Scenarios**:
1. `Given` uma migração executada com sucesso, `When` o admin consulta `migrations_history`, `Then` vê o registro com `action = 'upgrade'`, `duration_ms` e `executed_by`.
2. `Given` uma migração que falhou, `When` o rollback é executado, `Then` um novo registro com `action = 'downgrade'` é inserido com o log do erro.

---

## Requirements *(mandatory)*

### Functional Requirements (extensão do conjunto original)

#### Database Environments
*   **FR‑001**: O sistema deve suportar 4 ambientes de banco de dados independentes: production, test, development e mirror.
*   **FR‑002**: Cada ambiente deve ter sua própria string de conexão definida exclusivamente via variável de ambiente (`DATABASE_URL`), nunca hardcoded.
*   **FR‑003**: O banco de testes deve ser recriado do zero (drop all + migrate) antes de cada execução da suite de testes.
*   **FR‑004**: O banco mirror deve ser populado exclusivamente com dados sintéticos, sem qualquer dado real de produção.

#### Schema & Migrations
*   **FR‑005**: Todas as alterações de esquema devem ser gerenciadas via migrações versionadas e reversíveis (com `up` e `down`).
*   **FR‑006**: Migrações devem ser aplicadas automaticamente em dev/test via CI/CD, e exigir aprovação manual em produção.
*   **FR‑007**: Migrations concorrentes devem usar advisory lock do PostgreSQL (`pg_try_advisory_lock`) para evitar conflitos.
*   **FR‑008**: Toda migration com erro deve executar rollback automático ao estado anterior.
*   **FR‑028 (novo)**: O sistema deve registrar cada execução de migration (upgrade e downgrade) na tabela imutável `migrations_history` com revisão, ação, duração, executor e log.
*   **FR‑029 (novo)**: O sistema deve armazenar snapshots de métricas de performance (ex: `pg_stat_statements`) a cada N minutos na tabela `database_performance_snapshots`, particionada por mês.

#### Data Integrity & Constraints (mantidos + novos)
*   **FR‑009**: Chaves estrangeiras devem ter ações `ON DELETE` definidas (RESTRICT, CASCADE, SET NULL conforme a entidade).
*   **FR‑010**: Tabelas de entidades críticas (`sorteios_historicos`, `audit_log`, `migrations_history`, `feature_toggle_audit`) devem ser imutáveis (apenas INSERT).
*   **FR‑011**: A tabela `sorteios_historicos` deve ter hash único (SHA‑256) da combinação para consulta O(1).
*   **FR‑012**: A deleção de registros de usuário deve ser soft delete (coluna `deleted_at`).
*   **FR‑013**: Limite de 200 combinações salvas por usuário deve ser enforced via constraint.
*   **FR‑014**: Limite de 50 promessas por usuário deve ser enforced via constraint.
*   **FR‑030 (novo)**: Toda alteração de estado de feature toggle deve ser registrada na tabela `feature_toggle_audit`, incluindo o UUID do usuário, o hash do IP de origem e o estado anterior/novo.
*   **FR‑031 (novo)**: Cada execução do script de geração de dados sintéticos deve registrar na tabela `synthetic_data_generation_runs` o status, número de registros gerados e duração, facilitando a depuração e a confiabilidade do mirror.

#### Security & Compliance (OWASP, CWE, LGPD)
*   **FR‑015**: Senhas devem ser armazenadas exclusivamente como hash bcrypt (custo mínimo 12).
*   **FR‑016**: A API nunca deve retornar `senha_hash`, `ip_hash` ou qualquer campo sensível.
*   **FR‑017**: Endereços IP devem ser armazenados como hash SHA‑256 unidirecional (`ip_hash`), nunca o IP bruto.
*   **FR‑018**: Dados pessoais de usuários (nome, email) devem ser anonimizados em até 48 horas após solicitação de exclusão (LGPD Art. 18).
*   **FR‑019**: O banco mirror não deve conter dados pessoais reais — apenas dados sintéticos.
*   **FR‑020**: Todas as conexões com o banco de dados devem usar TLS 1.2+ em produção e mirror.
*   **FR‑021**: O pooling de conexões deve ter limite máximo configurável (default 20) para evitar exaustão de conexões.
*   **FR‑022**: Strings de conexão nunca devem ser incluídas em logs, traces ou mensagens de erro retornadas ao cliente.
*   **FR‑023**: A role de banco usada pela aplicação deve ter apenas os privilégios necessários (princípio do menor privilégio): CRUD nas tabelas de aplicação, sem acesso a outras databases ou `pg_catalog` além do necessário.
*   **FR‑032 (novo)**: Deve ser criada uma role `app_agent` com permissão de leitura em `pg_stat_statements` e nas tabelas de métricas, para uso pelos agentes de IA (Hermes, OpenCode).
*   **FR‑033 (novo)**: Deve ser utilizada a role `migration_user` exclusiva para DDL, sem permissão de INSERT em tabelas de aplicação.
*   **FR‑034 (novo)**: Para tabelas de alta volumetria (ex: `usage_events`, `audit_log`), devem ser utilizados índices BRIN em colunas `created_at` para reduzir espaço e manter performance de busca por intervalo.
*   **FR‑035 (novo)**: O backup de produção deve ser realizado via `pgBackRest` com criptografia, compressão e verificação de integridade, e o histórico de backups armazenado em `backup_history`.

---

## Success Criteria *(mandatory)*

*   **SC‑001**: Os 4 ambientes são iniciáveis com um único comando (`make db-up`) completamente isolados.
*   **SC‑002**: Suite de testes completa (cobertura ≥ 90%) executa em menos de 2 minutos contra o banco de testes recriado.
*   **SC‑003**: Consultas por hash de combinação em `sorteios_historicos` retornam em <5ms com 100.000+ registros.
*   **SC‑004**: Dashboard de tracking carrega métricas agregadas em <3s com 1 milhão+ eventos em `usage_events`.
*   **SC‑005**: Nenhuma senha em texto plano, IP bruto ou dado pessoal é exportado/persistido — verificado por scanner automatizado.
*   **SC‑006**: Migrações em dev/test são aplicadas em <30s sem intervenção manual.
*   **SC‑007**: Rollback de migration falha é concluído em <10s sem corromper dados.
*   **SC‑008**: O mirror contém ≥ 100.000 registros sintéticos distribuídos, sem nenhum dado real de produção.
*   **SC‑009 (novo)**: O histórico de feature toggles contém todos os eventos de ativação/desativação, imutáveis e auditáveis.
*   **SC‑010 (novo)**: Snapshots de performance são coletados a cada 15 minutos sem impacto >5% na performance do banco.
*   **SC‑011 (novo)**: Qualquer falha na geração de dados sintéticos é registrada em `synthetic_data_generation_runs` com status `failed` e log do erro.
*   **SC‑012 (novo)**: O tempo de recuperação de um backup do `pgBackRest` em dev é inferior a 5 minutos para um banco de 10GB.

## Database Schema (Expanded)

### New Tables (detalhadas)

#### `migrations_history`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() |
| `revision` | VARCHAR(20) | NOT NULL |
| `action` | VARCHAR(20) | NOT NULL, CHECK (action IN ('upgrade', 'downgrade')) |
| `duration_ms` | INTEGER | NOT NULL |
| `executed_by` | VARCHAR(100) | NOT NULL |
| `log_output` | TEXT | NULLABLE |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Imutável**. Índices: `(revision, action, created_at)` (btree), `(created_at)` (BRIN).

#### `feature_toggle_audit`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `feature_toggle_id` | UUID | NOT NULL, FK -> feature_toggles.id, ON DELETE CASCADE |
| `changed_by` | UUID | NULLABLE, FK -> users.id, ON DELETE SET NULL |
| `previous_state` | BOOLEAN | NOT NULL |
| `new_state` | BOOLEAN | NOT NULL |
| `source_ip_hash` | VARCHAR(64) | NULLABLE (SHA‑256) |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- **Imutável**. Índices: `(feature_toggle_id, created_at)` (btree), `(changed_by, created_at)` (btree).

#### `synthetic_data_generation_runs`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `script_name` | VARCHAR(255) | NOT NULL |
| `status` | VARCHAR(20) | NOT NULL, CHECK (status IN ('running', 'success', 'failed')) |
| `records_generated` | INTEGER | NULLABLE |
| `duration_ms` | INTEGER | NOT NULL |
| `error_log` | TEXT | NULLABLE |
| `started_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| `finished_at` | TIMESTAMPTZ | NULLABLE |
- Índices: `(started_at)` (BRIN), `(status, started_at)` (btree).

#### `database_performance_snapshots`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `snapshot_type` | VARCHAR(50) | NOT NULL |
| `metric_data` | JSONB | NOT NULL |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
- Particionamento por `created_at` (mensal). Índices: `(created_at)` (BRIN), `(snapshot_type, created_at)` (btree).

---

**Nota**: A especificação final deve incluir todas as tabelas originais com seus respectivos índices e constraints, além das novas tabelas acima. Os índices BRIN devem ser aplicados a tabelas grandes como `usage_events`, `audit_log`, `sorteios_historicos`, `migrations_history` e `database_performance_snapshots`. A gestão de backups deve utilizar `pgBackRest` como ferramenta padrão.

**Specs de referência**

- ./specs/001-bet-simulation-promise/spec.md
- ./specs/002-modular-feature-system/spec.md
- ./specs/003-system-management/spec.md
- ./specs/005-backup-automation /spec.md
- ./specs/006-environment-management/spec.md
- ./specs/007-megasena-data-collector/spec.md
- ./specs/008-lotofacil-data-collector/spec.md
- ./specs/008-lotofacil-data-collector/spec.md
- ./specs/010-duplasena-data-collector/spec.md
- ./specs/011-quina-data-collector/spec.md
- ./specs/012-federal-data-collector/spec.md
- ./specs/013-lotomania-data-collector/spec.md
- ./specs/014-timemania-data-collector/spec.md
- ./specs/014-timemania-data-collector/spec.md
- ./specs/015-maismilionaria-data-collector/spec.md
- ./specs/016-supersete-data-collector/spec.md
- ./specs/017-loteca-data-collector/spec.md



