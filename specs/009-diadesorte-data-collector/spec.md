# Feature Specification: Dia de Sorte Data Collector

**Feature Branch**: `009-diadesorte-data-collector`
**Created**: 2026-05-13
**Status**: Draft
**Input**: Especificação técnica para coleta de sorteios da Caixa Econômica Federal (CEF), específica para o jogo Dia de Sorte.

---

## 1. Technical Overview

Coleta automatizada do histórico completo de sorteios do Dia de Sorte a partir da planilha oficial da CEF, com armazenamento em JSON local (`./data/diadesorte.json`) e em tabela dedicada no banco PostgreSQL (`loterias_resultados_diadesorte`). Carga inicial integral na primeira execução; atualizações incrementais via scheduler Celery Beat com intervalo fixo de 6 horas + verificação extra 1 hora após dias de sorteio (terças, quintas e sábados, 22h). Stack assíncrona obrigatória: FastAPI + HTTPX + Polars + asyncpg + orjson + Celery/Redis.

---

## 2. Data Source

| Propriedade | Valor |
|---|---|
| **URL** | `https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Dia-De-Sorte` |
| **Formato** | Planilha eletrônica (XLSX), ordenada por concurso crescente |
| **Primeira linha** | Cabeçalho com nomes das colunas |
| **Campos por linha** | Concurso, Data Sorteio, Bola1 a Bola7, Mês da Sorte, Ganhadores 7 acertos, Cidade / UF, Rateio 7 acertos, Ganhadores 6 acertos, Rateio 6 acertos, Ganhadores 5 acertos, Rateio 5 acertos, Ganhadores 4 acertos, Rateio 4 acertos, Ganhadores mês da sorte, Rateio mês da sorte, Acumulado 7 acertos, Arrecadação Total, Estimativa Prêmio, Observação |

---

## 3. Behavior

### 3.1 Initial Load (First Execution)

- Download the complete spreadsheet from the CEF URL.
- Parse all rows using Polars (`pl.read_excel()`).
- Convert each row to a JSON object preserving original column names.
- Save as `./data/diadesorte.json` (or `DATA_PATH`/`diadesorte.json`).
- Bulk insert all records into `loterias_resultados_diadesorte` using `asyncpg.copy_from()`.

### 3.2 Periodic Updates (Scheduler)

- **Fixed interval**: 6 hours (configurable via `UPDATE_INTERVAL_HOURS`).
- **Mechanism**:
  1. Download the complete spreadsheet.
  2. Compare the max `Concurso` in the local JSON with the max `Concurso` in the new spreadsheet.
  3. If no new contests → discard download, do not rewrite JSON or database.
  4. If new contests exist (always at the end, due to ascending sort):
     - Read existing JSON, append new objects, rewrite the entire file (no raw append).
     - Insert only new records into `loterias_resultados_diadesorte` (incremental).
     - Log metrics: new contest count, processing duration.

### 3.3 Extra Verification on Draw Days

- Dia de Sorte draws: **Tuesdays, Thursdays and Saturdays at 21:00 BRT**.
- Extra check scheduled at **22:00 BRT** on draw days, in addition to the 6-hour periodic check.
- System **must not** depend on exact official publish times (CEF may delay).

---

## 4. User Scenarios & Testing *(mandatory)*

### User Story 1 — Initial Load (Priority: P1)

**Acceptance Scenarios**:

1. **Given** que `./data/diadesorte.json` não existe, **When** o coletor executa, **Then** a planilha é baixada, convertida via Polars e orjson, e o JSON é criado com todos os sorteios.
2. **Given** o JSON gerado, **When** a exportação para o banco é concluída, **Then** `loterias_resultados_diadesorte` contém o mesmo número de registros que o JSON.

### User Story 2 — Incremental Update (Priority: P1)

**Acceptance Scenarios**:

1. **Given** o último concurso local é N, **When** o scheduler executa e a planilha contém N+M, **Then** apenas M novos concursos são adicionados ao JSON e ao banco.
2. **Given** o scheduler executa, **When** não há novos concursos, **Then** o download é descartado, JSON e banco inalterados.

### User Story 3 — Error Resilience (Priority: P2)

**Acceptance Scenarios**:

1. **Given** dados existentes, **When** o download falha, **Then** JSON e banco não são modificados.
2. **Given** dados existentes, **When** o parse falha, **Then** o arquivo baixado é preservado para diagnóstico.

---

## 5. Data Model

### JSON: `./data/diadesorte.json`

```json
{
  "meta": {
    "jogo": "Diadesorte",
    "url_origem": "https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Dia-De-Sorte",
    "ultima_atualizacao": "2026-05-13T03:00:00Z",
    "ultima_verificacao": "2026-05-13T09:00:00Z",
    "total_concursos": 1000,
    "versao_formato": "1.0"
  },
  "concursos": [
    {
      "Concurso": 1000,
      "Data Sorteio": "2026-05-09",
      "Bola1": 3, "Bola2": 8, "Bola3": 12, "Bola4": 17,
      "Bola5": 21, "Bola6": 25, "Bola7": 30,
      "Mês da Sorte": 12,
      "Ganhadores 7 acertos": 1,
      "Cidade / UF": "São Paulo/SP",
      "Rateio 7 acertos": 500000.00,
      "Ganhadores 6 acertos": 25,
      "Rateio 6 acertos": 3500.00,
      "Ganhadores 5 acertos": 1200,
      "Rateio 5 acertos": 120.00,
      "Ganhadores 4 acertos": 18000,
      "Rateio 4 acertos": 8.00,
      "Ganhadores mês da sorte": 500,
      "Rateio mês da sorte": 50.00,
      "Acumulado 7 acertos": false,
      "Arrecadação Total": 8500000.00,
      "Estimativa Prêmio": 1200000.00,
      "Observação": ""
    }
  ]
}
```

### Database: `loterias_resultados_diadesorte`

```sql
CREATE TABLE loterias_resultados_diadesorte (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    "Concurso" INTEGER NOT NULL,
    "Data Sorteio" DATE NOT NULL,
    "Bola1" INTEGER NOT NULL, "Bola2" INTEGER NOT NULL,
    "Bola3" INTEGER NOT NULL, "Bola4" INTEGER NOT NULL,
    "Bola5" INTEGER NOT NULL, "Bola6" INTEGER NOT NULL,
    "Bola7" INTEGER NOT NULL,
    "Mês da Sorte" INTEGER NOT NULL,
    "Ganhadores 7 acertos" INTEGER DEFAULT 0,
    "Cidade / UF" VARCHAR(150),
    "Rateio 7 acertos" DECIMAL(14,2),
    "Ganhadores 6 acertos" INTEGER DEFAULT 0,
    "Rateio 6 acertos" DECIMAL(14,2),
    "Ganhadores 5 acertos" INTEGER DEFAULT 0,
    "Rateio 5 acertos" DECIMAL(14,2),
    "Ganhadores 4 acertos" INTEGER DEFAULT 0,
    "Rateio 4 acertos" DECIMAL(14,2),
    "Ganhadores mês da sorte" INTEGER DEFAULT 0,
    "Rateio mês da sorte" DECIMAL(14,2),
    "Acumulado 7 acertos" BOOLEAN DEFAULT false,
    "Arrecadação Total" DECIMAL(14,2),
    "Estimativa Prêmio" DECIMAL(14,2),
    "Observação" TEXT,

    coletado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    hash_combinacao VARCHAR(64) NOT NULL,
    dezenas_ordenadas INTEGER[] NOT NULL,
    CONSTRAINT uq_diadesorte_concurso UNIQUE ("Concurso"),
    CONSTRAINT uq_diadesorte_hash UNIQUE (hash_combinacao)
);

CREATE INDEX idx_diadesorte_data ON loterias_resultados_diadesorte ("Data Sorteio");
CREATE INDEX idx_diadesorte_dezenas ON loterias_resultados_diadesorte USING GIN (dezenas_ordenadas);
```

---

## 6. Functional Requirements

### Initial Load
- **FR-001**: System MUST download the complete XLSX from the configured URL on first run.
- **FR-002**: System MUST parse the spreadsheet using Polars (`pl.read_excel()`), never Pandas.
- **FR-003**: System MUST serialize the output using orjson, never stdlib `json`.
- **FR-004**: System MUST save JSON to `./data/diadesorte.json`.
- **FR-005**: System MUST bulk insert all records using asyncpg `copy_from()`.

### Incremental Updates
- **FR-006**: System MUST run periodic checks every 6 hours via Celery Beat.
- **FR-007**: System MUST schedule extra check at 22:00 BRT on draw days (Tuesday, Thursday, Saturday).
- **FR-008**: System MUST compare max `Concurso` to detect new records.
- **FR-009**: System MUST read existing JSON, append new objects, rewrite entire file.
- **FR-010**: System MUST insert only new records into database (incremental).
- **FR-011**: System MUST NOT rewrite JSON or database if no new contests exist.

### Error Handling
- **FR-012**: Download failure → log ERROR, abort, preserve data, GlitchTip alert.
- **FR-013**: Parse failure → log details, abort, preserve file in `./data/erros/`.
- **FR-014**: JSON write failure → restore previous backup, log CRITICAL.
- **FR-015**: DB insert failure → rollback, log ERROR, do not commit.
- **FR-016**: Timeout → retry 3x with exponential backoff (Celery).

### Monitoring
- **FR-017**: Expose `lottery_download_duration_seconds{game="diadesorte"}`, `lottery_new_contests_total{game="diadesorte"}`, `lottery_last_success_timestamp{game="diadesorte"}`, `lottery_errors_total{game="diadesorte",type="download|parse|db|json"}`.
- **FR-018**: Structured JSON logs with `timestamp`, `level`, `game`, `contest`, `message`, `trace_id`.

### Security (OWASP/CWE)
- **FR-019**: Parameterized queries only (CWE-89).
- **FR-020**: Pydantic validation before insert (CWE-20).
- **FR-021**: Logs must not contain raw contest data (CWE-200).
- **FR-022**: Containers as non-root user (OWASP A05).
- **FR-023**: Admin endpoints require JWT (OWASP A07).
- **FR-024**: HTTP timeout: `httpx.Timeout(connect=5.0, read=30.0, write=5.0, pool=5.0)` (CWE-400).
- **FR-025**: JSON filename fixed as `diadesorte.json` (CWE-73).

### Coexistence
- **FR-026**: Each game has its own table `loterias_resultados_{jogo}`.
- **FR-027**: Each game has its own JSON file `./data/{jogo}.json`.
- **FR-028**: Each game has its own Celery Beat task.
- **FR-029**: `BaseLotteryCollector` abstract class with overridable URL, columns, table, JSON path.
- **FR-030**: `DiadesorteCollector` inherits `BaseLotteryCollector` with zero duplicated logic.

---

## 7. Mandatory Stack

| Layer | Component |
|---|---|
| REST API | FastAPI + Pydantic v2 |
| HTTP Client | HTTPX (async) |
| Data Processing | Polars (`pl.read_excel`) |
| Database | PostgreSQL 15+ |
| DB Driver | asyncpg (`copy_from`) |
| JSON | orjson |
| Scheduler | Celery + Redis (Celery Beat) |
| Container | Docker + docker-compose |
| Monitoring | Prometheus + Grafana |
| Logs | Loki + Promtail (JSON) |
| Error Tracking | GlitchTip / Sentry On-Premise |
| Rate Limiting | slowapi + Redis |
| Auth | python-jose (JWT) |
| File Security | ClamAV (optional) |

**Forbidden**: Pandas, `requests` sync, sqlite3, `json` stdlib, pure sync architecture.

---

## 8. Error Handling

| Failure | Action |
|---|---|
| Download failure | Log ERROR, abort, preserve data, GlitchTip alert |
| Parse failure (Polars) | Log details, abort, save `.xlsx` to `./data/erros/` |
| JSON write failure | Restore backup, log CRITICAL |
| DB insert failure | Rollback transaction, log ERROR |
| Download timeout | Retry 3x exponential backoff (Celery) |

---

## 9. Success Criteria *(mandatory)*

- **SC-001**: Initial load of ~1000 contests completes in under 60 seconds.
- **SC-002**: Verification with zero new contests completes in under 15 seconds.
- **SC-003**: Incremental update with 1 new contest completes in under 20 seconds.
- **SC-004**: Zero data loss on any failure scenario.
- **SC-005**: All Prometheus metrics increment correctly on each collection cycle.
- **SC-006**: Adding a new game collector requires only a subclass + Celery Beat entry, zero existing code changes.

---

## 10. Assumptions

- **Formato XLSX estável**: CEF mantém cabeçalhos. Mudanças disparam erro de parse.
- **Ordenação crescente**: Planilha ordenada por concurso. Novos sorteios no final.
- **CEF sem API de metadados**: Download completo necessário a cada verificação.
- **Atraso na publicação**: CEF pode publicar horas após o sorteio.
- **JSON é fonte primária offline**: Banco é projeção dos dados para consulta via API.
- **Redis disponível**: Essencial para broker Celery.
- **Volume de dados**: ~1000 concursos × ~25 campos = < 5 MB.

---

## 11. Project Structure

```
.
├── docker-compose.yml
├── .env.example
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── dependencies.py
│   ├── collectors/
│   │   ├── base.py            # BaseLotteryCollector
│   │   ├── diadesorte.py      # DiadesorteCollector
│   │   └── (future)
│   ├── models/
│   │   ├── schemas.py
│   │   └── database.py
│   ├── tasks/
│   │   ├── celery_app.py
│   │   └── periodic.py
│   ├── utils/
│   │   ├── logging_config.py
│   │   ├── metrics.py
│   │   └── security.py
│   └── main.py
├── data/
│   └── diadesorte.json
├── tests/
│   ├── test_collector.py
│   └── test_api.py
└── requirements.txt
```
