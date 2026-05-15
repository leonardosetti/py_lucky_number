# Feature Specification: Backup Automation

**Feature Branch**: `005-backup-automation`
**Created**: 2026-05-11
**Status**: Draft
**Input**: User description: "Defina scripts de automação para back-up de dados. O script deve escolher a linguagem mais performatica e segura para esta atividade (GO, Rust, Pyton C++, Lua, etc). Este script poderá ser coordenado pelo crom e ou daemon."

## Relationship with Spec 004

Esta spec define a ferramenta de backup lógico (pg_dump + AES-256-GCM + S3),
**complementar** ao backup físico pgBackRest definido na spec 004 (FR-035).

| Camada | Ferramenta | Escopo | Spec |
|---|---|---|---|
| Backup físico | pgBackRest (WAL archiving) | Disaster recovery, restore completo | 004 |
| Backup lógico | Go tool (pg_dump + AES-256-GCM) | Exportação seletiva, mirror, dev/QA | 005 (esta) |

Ambas DEVEM coexistir: pgBackRest para RPO de minutos via WAL, Go tool
para exportações sob demanda e população do mirror.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Administrador Executa Backup Programado Automático (Priority: P1)

Como administrador do sistema, quero que backups completos do banco de dados PostgreSQL de produção sejam executados automaticamente em horário programado (diário, 03:00 UTC), sem intervenção manual, com compressão e criptografia, para garantir a recuperabilidade dos dados em caso de desastre com perda máxima de 24 horas (RPO = 24h).

**Why this priority**: Sem backup automatizado, a perda de dados é irreversível. RPO de 24h é o mínimo aceitável para um sistema de produção financeiro (apostas envolvem valores monetários).

**Independent Test**: Pode ser testado configurando o scheduler, aguardando a execução agendada, e validando que o arquivo de backup foi gerado com sucesso no destino configurado.

**Acceptance Scenarios**:

1. **Given** o scheduler configurado para 03:00 UTC, **When** o relógio atinge o horário agendado, **Then** o backup é iniciado automaticamente e um log de início é registrado.
2. **Given** um backup em execução, **When** ele é concluído com sucesso, **Then** o arquivo de backup é comprimido, criptografado e transferido para storage externo (off-site), e um log de sucesso é registrado com tamanho, duração e checksum.
3. **Given** um backup em execução, **When** ele falha (ex: banco indisponível, disco cheio), **Then** o script registra o erro com detalhes, envia notificação para o admin, e faz nova tentativa após 30 minutos.

---

### User Story 2 - Administrador Aciona Backup Manual Sob Demanda (Priority: P1)

Como administrador, quero poder acionar um backup manual a qualquer momento via linha de comando, para realizar backups extraordinários antes de alterações críticas (deploy, migração de schema, alteração de configuração).

**Why this priority**: Backups manuais são essenciais para segurança em operações de risco iminente. Sem eles, qualquer alteração crítica é feita sem rede de proteção.

**Independent Test**: Pode ser testado executando o comando de backup manual e validando que o arquivo gerado é idêntico em formato e integridade ao backup automático.

**Acceptance Scenarios**:

1. **Given** o comando de backup manual disponível no terminal, **When** o admin executa `backup-tool --manual`, **Then** o backup é iniciado imediatamente com os mesmos parâmetros do backup agendado.
2. **Given** um backup manual em execução, **When** o admin pressiona Ctrl+C, **Then** o script interrompe graciosamente, limpa arquivos temporários e registra o cancelamento no log.

---

### User Story 3 - Administrador Valida Integridade e Restaura Backup (Priority: P2)

Como administrador, quero validar a integridade de um arquivo de backup (checksum) e realizar a restauração em um banco de destino (ex: mirror ou development), para verificar periodicamente que os backups são recuperáveis e treinar procedimentos de disaster recovery.

**Why this priority**: Um backup que não pode ser restaurado não é um backup. A validação periódica é a única garantia de que o processo funciona.

**Independent Test**: Pode ser testado executando a validação de checksum de um backup existente e realizando a restauração em um banco mirror, confirmando que os dados estão íntegros e consistentes.

**Acceptance Scenarios**:

1. **Given** um arquivo de backup existente, **When** o admin executa `backup-tool --verify <arquivo>`, **Then** o script calcula o SHA-256 do arquivo e compara com o checksum armazenado no log, retornando "válido" ou "corrompido".
2. **Given** um arquivo de backup válido, **When** o admin executa `backup-tool --restore <arquivo> --target <database_url>`, **Then** o banco de destino é restaurado e o script valida a consistência (contagem de linhas vs. metadados do backup).

---

### User Story 4 - Administrador Define Política de Retenção e Limpeza (Priority: P3)

Como administrador, quero configurar a política de retenção de backups (ex: manter backups diários dos últimos 30 dias, semanais dos últimos 6 meses, mensais dos últimos 5 anos), para que backups antigos sejam removidos automaticamente sem acumular custos de armazenamento.

**Why this priority**: Sem retenção configurada, o storage cresce indefinidamente. A política libera espaço automaticamente, mas o sistema funciona sem ela — daí P3.

**Independent Test**: Pode ser testado configurando uma retenção curta (ex: 2 dias), aguardando a limpeza automática, e validando que backups com mais de 2 dias foram removidos.

**Acceptance Scenarios**:

1. **Given** a política de retenção configurada (ex: 30 dias diários + 6 meses semanais), **When** o script de limpeza é executado após o backup, **Then** backups fora da política são removidos e um log de remoção é registrado.
2. **Given** a política configurada, **When** não há backups para remover (todos dentro da política), **Then** o script registra "Nenhum backup a remover" e continua normalmente.

---

### Edge Cases

- **Concorrência**: Se um backup já estiver em execução quando o próximo for agendado, o novo não deve iniciar — deve registrar "Backup já em execução" e aguardar o próximo ciclo.
- **Disco cheio durante backup**: O script deve detectar espaço insuficiente antes de iniciar o dump, abortar com erro claro e notificar o admin. Durante a execução, deve monitorar espaço e abortar se atingir 95% de uso.
- **Falha de rede no upload**: Se o upload para storage externo falhar, o backup local deve ser mantido e reenviado na próxima tentativa (30 min). Após 3 falhas consecutivas, notificação crítica deve ser enviada.
- **Backup corrompido**: Se o checksum pós-dump não corresponder ao esperado, o backup deve ser descartado e refeito automaticamente (máx 2 tentativas).
- **Timezone**: Todos os timestamps de backup devem ser em UTC para evitar ambiguidade em ambientes distribuídos.
- **Restauração em produção**: O comando `--restore` deve exigir confirmação explícita adicional (`--force`) se o destino for produção, para evitar restauração acidental.

## Language Decision

Com base nos requisitos de **performance**, **segurança** e **portabilidade**, a linguagem recomendada é **Go** pelas seguintes razões:

| Critério | Go | Python | Rust | C++ |
|---|---|---|---|---|
| Binário único estático | ✅ Sim | ❌ Requer runtime | ✅ Sim | ✅ Sim |
| Performance I/O (pg_dump pipes) | ✅ Excelente | ⚠️ Moderada | ✅ Excelente | ✅ Excelente |
| Criptografia nativa stdlib | ✅ crypto/aes, crypto/sha256 | ⚠️ Via PyCryptodome | ✅ Excelente | ⚠️ Via OpenSSL |
| Daemon/service nativo | ✅ Simples | ⚠️ Complexo | ✅ Simples | ⚠️ Complexo |
| Facilidade de manutenção | ✅ Alta | ✅ Alta | ⚠️ Média | ❌ Baixa |
| Ecossistema para cloud storage | ✅ excelente (S3, GCS) | ✅ excelente | ⚠️ Maturação média | ❌ Limitado |
| Compilação cruzada | ✅ nativa | ❌ N/A | ✅ nativa | ⚠️ Requer toolchain |
| Segurança de memória | ✅ GC seguro | ✅ GC seguro | ✅ Ownership | ❌ Manual |

**Decisão**: Go atende todos os requisitos com o melhor equilíbrio entre performance, segurança e manutenibilidade. Rust seria equivalente em performance e segurança, mas com maior custo de desenvolvimento e manutenção.

## Requirements *(mandatory)*

### Functional Requirements

**Backup Engine**
- **FR-001**: A ferramenta DEVE executar dump do banco PostgreSQL via `pg_dump` custom format (formato `custom`, que permite compressão e paralelismo).
- **FR-002**: O dump DEVE ser comprimido com gzip (nível 6) e criptografado com AES-256-GCM antes da transferência.
- **FR-003**: A chave de criptografia DEVE ser fornecida via variável de ambiente (`BACKUP_ENCRYPTION_KEY`), nunca hardcoded ou em linha de comando.
- **FR-004**: O checksum SHA-256 do arquivo final DEVE ser calculado e armazenado junto ao backup (arquivo `.sha256`).
- **FR-005**: O script DEVE suportar backup de bancos específicos e de todas as databases do cluster (modo full).
- **FR-006**: O backup DEVE incluir metadados: database, timestamp, tamanho, checksum, versão do schema, duração.
- **FR-007**: O script DEVE gravar logs estruturados (JSON) em arquivo rotativo com níveis: INFO, WARN, ERROR.

**Scheduling & Execution**
- **FR-008**: A ferramenta DEVE suportar dois modos de execução: **cron** (execução única por chamada, agendada externamente) e **daemon** (processo contínuo com scheduler interno).
- **FR-009**: No modo daemon, o intervalo entre backups DEVE ser configurável via variável de ambiente (`BACKUP_INTERVAL`, default 24h).
- **FR-010**: No modo daemon, o script DEVE garantir que apenas uma instância de backup rode por vez (mutex via lockfile).
- **FR-011**: A ferramenta DEVE aceitar parâmetros via linha de comando e variáveis de ambiente, com variáveis de ambiente tendo precedência.

**Storage & Transfer**
- **FR-012**: O backup DEVE ser transferido para storage externo (S3-compatible ou SFTP) após a conclusão local.
- **FR-013**: O storage de destino DEVE ser configurável via variáveis de ambiente (`BACKUP_STORAGE_TYPE`, `BACKUP_STORAGE_URL`, `BACKUP_STORAGE_KEY`, `BACKUP_STORAGE_SECRET`).
- **FR-014**: O script DEVE manter o backup local temporário até que o upload externo seja confirmado, removendo-o apenas após sucesso.

**Retention & Cleanup**
- **FR-015**: A política de retenção DEVE ser configurada com 3 níveis: diário (dias), semanal (semanas), mensal (meses).
- **FR-016**: A limpeza DEVE ser executada automaticamente após cada backup bem-sucedido, removendo backups que excedam a política.
- **FR-017**: Backups marcados como "manual" NUNCA DEVEM ser removidos pela política de retenção automática.

**Restore & Verification**
- **FR-018**: O script DEVE suportar restore via `pg_restore` com validação pós-restore (contagem de linhas vs. metadados).
- **FR-019**: O restore em ambiente de produção DEVE exigir flag `--force` explícita para prevenir execução acidental.
- **FR-020**: O script DEVE verificar a integridade do arquivo de backup (checksum SHA-256) antes de qualquer tentativa de restore.

**Security**
- **FR-021**: A chave de criptografia NUNCA DEVE aparecer em logs, linha de comando (evitada via env vars) ou metadados do backup.
- **FR-022**: O binário DEVE ser compilado como static binary (sem dependências externas) para distribuição segura.
- **FR-023**: A comunicação com storage externo DEVE usar TLS 1.2+.
- **FR-024**: O arquivo de lockfile DEVE ser armazenado em `/var/lock/backup.lock` com permissões 0600. Em ambiente containerizado, o diretório `/var/lock/` DEVE ser montado como volume para garantir persistência entre restart do container.
- **FR-025**: Logs NUNCA DEVEM conter strings de conexão, chaves de criptografia ou senhas do banco.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Backup completo de um banco com 1GB de dados é concluído em menos de 5 minutos (dump + compressão + criptografia + upload).
- **SC-002**: A ferramenta opera com uso de memória inferior a 100MB durante toda a execução.
- **SC-003**: O restore de um backup de 1GB em banco vazio é concluído em menos de 10 minutos com 100% de integridade dos dados.
- **SC-004**: Zero falhas de segurança: a chave de criptografia não é exposta em logs, linha de comando ou metadados em 100% das execuções.
- **SC-005**: O daemon mantém execução contínua por 30 dias sem falhas ou vazamento de memória.
- **SC-006**: A política de retenção remove backups expirados corretamente em 100% dos casos, sem remover backups manuais ou dentro da política.
- **SC-007**: 100% dos backups são recuperáveis e validados por restore trimestral em ambiente mirror.
- **SC-008**: Notificações de falha são entregues em menos de 5 minutos após a detecção do erro.

## Assumptions

- **pg_dump/pg_restore disponíveis**: Assume-se que as ferramentas `pg_dump` e `pg_restore` (versão compatível com o banco) estão instaladas no ambiente onde o script será executado.
- **PostgreSQL 16+**: O banco de dados alvo é PostgreSQL 16 ou superior (compatível com `pg_dump` custom format).
- **Storage S3-compatible**: O storage externo é S3-compatible (AWS S3, MinIO, DigitalOcean Spaces, etc.) ou SFTP.
- **Cron como alternativa**: Ambientes sem systemd podem usar cron com a flag `--cron`. O modo daemon é preferível para ambientes serverless ou containerizados.
- **Notificação via email/webhook**: Falhas de backup enviam notificação para o admin via webhook configurável (Slack, email, etc.).
- **Binário único**: O binário Go será compilado como static binary para Linux amd64 e arm64, sem dependências de runtime.
- **Chave de 256 bits**: A chave de criptografia AES-256-GCM deve ter exatamente 32 bytes (256 bits), codificada em base64 na variável de ambiente.
