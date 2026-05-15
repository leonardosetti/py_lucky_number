# Feature Specification: Lotofácil Data Collector

**Feature Branch**: `008-lotofacil-data-collector`
**Created**: 2026-05-13
**Status**: Draft
**Input**: Especificação técnica para coleta de sorteios da Caixa Econômica Federal (CEF), específica para o jogo Lotofácil.

---

## 1. Technical Overview

Coleta automatizada do histórico completo de sorteios da Lotofácil a partir da planilha oficial da CEF, com armazenamento em JSON local (`./data/lotofacil.json`) e em tabela dedicada no banco PostgreSQL (`loterias_resultados_lotofacil`). Carga inicial integral na primeira execução; atualizações incrementais via scheduler Celery Beat com intervalo fixo de 6 horas + verificação extra 1 hora após dias de sorteio (segunda a sábado, 22h). Stack assíncrona obrigatória: FastAPI + HTTPX + Polars + asyncpg + orjson + Celery/Redis.

---

## 2. Data Source

| Propriedade | Valor |
|---|---|
| **URL** | `https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Lotof%C3%A1cil` |
| **Formato** | Planilha eletrônica (XLSX), ordenada por concurso crescente |
| **Primeira linha** | Cabeçalho com nomes das colunas |
| **Campos por linha** | Concurso, Data Sorteio, Bola1 a Bola15, Ganhadores 15 acertos, Cidade / UF, Rateio 15 acertos, Ganhadores 14 acertos, Rateio 14 acertos, Ganhadores 13 acertos, Rateio 13 acertos, Ganhadores 12 acertos, Rateio 12 acertos, Ganhadores 11 acertos, Rateio 11 acertos, Acumulado 15 acertos, Arrecadacao Total, Estimativa Prêmio, Acumulado sorteio especial Lotofácil da Independência, Observação |

---

## 3. Behavior

### 3.1 Initial Load (First Execution)

- Download the complete spreadsheet from the CEF URL.
- Parse all rows using Polars (`pl.read_excel()`).
- Convert each row to a JSON object preserving original column names.
- Save as `./data/lotofacil.json` (or `DATA_PATH`/`lotofacil.json`).
- Bulk insert all records into `loterias_resultados_lotofacil` using `asyncpg.copy_from()`.

### 3.2 Periodic Updates (Scheduler)

- **Fixed interval**: 6 hours (configurable via `UPDATE_INTERVAL_HOURS`).
- **Mechanism**:
  1. Download the complete spreadsheet.
  2. Compare the max `Concurso` in the local JSON with the max `Concurso` in the new spreadsheet.
  3. If no new contests → discard download, do not rewrite JSON or database.
  4. If new contests exist (always at the end, due to ascending sort):
     - Read existing JSON, append new objects, rewrite the entire file (no raw append).
     - Insert only new records into `loterias_resultados_lotofacil` (incremental, not full reload).
     - Log metrics: new contest count, processing duration.

### 3.3 Extra Verification on Draw Days

- Lotofácil draws: **Mondays through Saturdays at 21:00 BRT**.
- Extra check scheduled at **22:00 BRT** on draw days, in addition to the 6-hour periodic check.
- The system **must not** depend on exact official publish times (CEF may delay). The extra check is a heuristic.

---

## 4. User Scenarios & Testing *(mandatory)*

### User Story 1 — Initial Load Populates JSON and Database (Priority: P1)

Como o sistema, quero que na primeira execução a planilha completa seja baixada, parseada com Polars e armazenada em `./data/lotofacil.json` e na tabela `loterias_resultados_lotofacil`, para que a base histórica esteja disponível antes de qualquer operação de geração de apostas.

**Acceptance Scenarios**:

1. **Given** que `./data/lotofacil.json` não existe, **When** o coletor executa, **Then** a planilha é baixada, convertida via Polars e orjson, e o JSON é criado com todos os sorteios.
2. **Given** o JSON gerado, **When** a exportação para o banco é concluída, **Then** `loterias_resultados_lotofacil` contém o mesmo número de registros que o JSON.
3. **Given** a carga inicial concluída, **When** o sistema reinicia, **Then** o coletor detecta o JSON existente e não refaz o download completo.

### User Story 2 — Incremental Update via Celery Beat (Priority: P1)

Como o sistema, quero que o scheduler Celery Beat execute a verificação a cada 6 horas, baixando a planilha, comparando o maior concurso e adicionando apenas sorteios novos, para manter a base atualizada sem tráfego desnecessário.

**Acceptance Scenarios**:

1. **Given** o último concurso local é N, **When** o scheduler executa e a planilha contém N+M, **Then** apenas M novos concursos são adicionados ao JSON e ao banco.
2. **Given** o scheduler executa, **When** não há novos concursos, **Then** o download é descartado, JSON e banco inalterados, log registra "Nenhum novo sorteio".

### User Story 3 — Error Resilience Preserves Existing Data (Priority: P2)

Como o sistema, quero que falhas de download, parse ou escrita nunca corrompam os dados já coletados — a atualização é abortada e os dados anteriores permanecem intactos.

**Acceptance Scenarios**:

1. **Given** dados existentes, **When** o download falha (timeout, HTTP 500), **Then** log de erro é registrado, JSON e banco não são modificados.
2. **Given** dados existentes, **When** o parse da planilha falha (coluna inesperada), **Then** o arquivo baixado é preservado para diagnóstico, dados anteriores mantidos.
3. **Given** dados existentes, **When** a escrita do JSON falha, **Then** o backup do arquivo anterior é restaurado.

---

## 5. Data Model

### JSON File: `./data/lotofacil.json`

```json
{
  "meta": {
    "jogo": "Lotofacil",
    "url_origem": "https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Lotof%C3%A1cil",
    "ultima_atualizacao": "2026-05-13T03:00:00Z",
    "ultima_verificacao": "2026-05-13T09:00:00Z",
    "total_concursos": 3300,
    "versao_formato": "1.0"
  },
  "concursos": [
    {
      "Concurso": 3300,
      "Data Sorteio": "2026-05-09",
      "Bola1": 1, "Bola2": 4, "Bola3": 7, "Bola4": 10, "Bola5": 13,
      "Bola6": 2, "Bola7": 5, "Bola8": 8, "Bola9": 11, "Bola10": 14,
      "Bola11": 3, "Bola12": 6, "Bola13": 9, "Bola14": 12, "Bola15": 15,
      "Ganhadores 15 acertos": 1,
      "Cidade / UF": "São Paulo/SP",
      "Rateio 15 acertos": 1500000.00,
      "Ganhadores 14 acertos": 120,
      "Rateio 14 acertos": 1800.00,
      "Ganhadores 13 acertos": 4500,
      "Rateio 13 acertos": 30.00,
      "Ganhadores 12 acertos": 25000,
      "Rateio 12 acertos": 12.00,
      "Ganhadores 11 acertos": 120000,
      "Rateio 11 acertos": 6.00,
      "Acumulado 15 acertos": false,
      "Arrecadacao Total": 45000000.00,
      "Estimativa Prêmio": 2000000.00,
      "Acumulado sorteio especial Lotofácil da Independência": false,
      "Observação": ""
    }
  ]
}
```

### Database Table: `loterias_resultados_lotofacil`

```sql
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
    "Estimativa Prêmio" DECIMAL(14,2),
    "Acumulado sorteio especial Lotofácil da Independência" BOOLEAN DEFAULT false,
    "Observação" TEXT,

    -- Metadata
    coletado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    hash_combinacao VARCHAR(64) NOT NULL,
    dezenas_ordenadas INTEGER[] NOT NULL,

    CONSTRAINT uq_lotofacil_concurso UNIQUE ("Concurso"),
    CONSTRAINT uq_lotofacil_hash UNIQUE (hash_combinacao)
);

CREATE INDEX idx_lotofacil_data ON loterias_resultados_lotofacil ("Data Sorteio");
CREATE INDEX idx_lotofacil_dezenas ON loterias_resultados_lotofacil USING GIN (dezenas_ordenadas);
```

---

## 6. Functional Requirements

### Initial Load
- **FR-001**: System MUST download the complete XLSX from the configured URL on first run (JSON absent).
- **FR-002**: System MUST parse the spreadsheet using Polars (`pl.read_excel()`), never Pandas.
- **FR-003**: System MUST serialize the output using orjson, never stdlib `json`.
- **FR-004**: System MUST save JSON to `./data/lotofacil.json` (or `DATA_PATH`/`lotofacil.json`).
- **FR-005**: System MUST bulk insert all records into `loterias_resultados_lotofacil` using asyncpg `copy_from()`.

### Incremental Updates
- **FR-006**: System MUST run periodic checks every 6 hours via Celery Beat (configurable `UPDATE_INTERVAL_HOURS`).
- **FR-007**: System MUST schedule an extra check at 22:00 BRT on draw days (Monday–Saturday).
- **FR-008**: System MUST compare max `Concurso` to detect new records.
- **FR-009**: System MUST read existing JSON, append new objects, rewrite entire file (not raw append).
- **FR-010**: System MUST insert only new records into database (incremental).
- **FR-011**: System MUST NOT rewrite JSON or database if no new contests exist.

### Error Handling
- **FR-012**: Download failure → log ERROR, abort, preserve existing data, send alert to GlitchTip.
- **FR-013**: Parse failure (Polars error) → log details, abort, preserve downloaded file in `./data/erros/`.
- **FR-014**: JSON write failure → restore previous file backup, log CRITICAL.
- **FR-015**: Database insert failure → rollback transaction, log ERROR, do not commit.
- **FR-016**: Download timeout → retry with exponential backoff up to 3 attempts (Celery retry).

### Monitoring (Prometheus)
- **FR-017**: System MUST expose metrics at `/metrics`:
  - `lottery_download_duration_seconds{game="lotofacil"}`
  - `lottery_new_contests_total{game="lotofacil"}`
  - `lottery_last_success_timestamp{game="lotofacil"}`
  - `lottery_errors_total{game="lotofacil",type="download|parse|db|json"}`
- **FR-018**: System MUST emit structured JSON logs with fields: `timestamp`, `level`, `game`, `contest`, `message`, `trace_id`.

### Security (OWASP / CWE)
- **FR-019**: All database queries MUST use parameterized statements (CWE-89).
- **FR-020**: All spreadsheet fields MUST be validated via Pydantic models before insert (CWE-20).
- **FR-021**: Logs MUST NOT contain raw contest data — only metadata (concurso, date) (CWE-200).
- **FR-022**: Containers MUST run as non-root user (`USER appuser`) (OWASP A05:2021).
- **FR-023**: Admin endpoints MUST require JWT authentication (OWASP A07:2021).
- **FR-024**: HTTP download MUST have timeout: `httpx.Timeout(connect=5.0, read=30.0, write=5.0, pool=5.0)` (CWE-400).
- **FR-025**: JSON filename MUST be fixed (`lotofacil.json`), never derived from spreadsheet data (CWE-73).

### Coexistence & Reusability
- **FR-026**: Each game MUST have its own database table (`loterias_resultados_{jogo}`).
- **FR-027**: Each game MUST have its own JSON file (`./data/{jogo}.json`).
- **FR-028**: Each game MUST have its own Celery Beat task (no shared state beyond Redis broker).
- **FR-029**: Collector logic MUST be implemented via `BaseLotteryCollector` abstract class with overridable: URL, column names, table name, JSON path.
- **FR-030**: Individual collectors (`LotofacilCollector`) MUST inherit from `BaseLotteryCollector` with zero duplicated logic.

---

## 7. Mandatory Open Source Stack

| Layer | Component | Notes |
|---|---|---|
| REST API | FastAPI | Async, Pydantic v2 |
| HTTP Client | HTTPX | Async, streaming |
| Data Processing | Polars | Excel reading (`pl.read_excel()`), lazy if possible |
| Database | PostgreSQL 15+ | One table per game |
| DB Driver | asyncpg | `copy_from` for bulk insert |
| JSON | orjson | Read/write, never stdlib `json` |
| Task Scheduler | Celery + Redis | Celery Beat for periodicity |
| Container | Docker (Moby) | docker-compose for dev |
| Monitoring | Prometheus + Grafana | Metrics endpoint |
| Logs | Loki + Promtail | JSON structured logs |
| Error Tracking | GlitchTip / Sentry On-Premise | Exception capture |
| Rate Limiting | slowapi + Redis | For manual endpoints |
| Auth | python-jose (JWT) + OAuth2 | FastAPI Depends |
| File Security | ClamAV | Optional scan |

**Forbidden**: Pandas, synchronous requests, sqlite3, pure synchronous architecture, proprietary/non-OSI licenses.

---

## 8. Error Handling (Mandatory)

| Failure | Action |
|---|---|
| Download failure | Log ERROR, abort, preserve data, GlitchTip alert |
| Parse failure (Polars) | Log details, abort, save `.xlsx` to `./data/erros/` |
| JSON write failure | Restore backup, log CRITICAL |
| DB insert failure | Rollback transaction, log ERROR |
| Download timeout | Retry 3x with exponential backoff (Celery) |

---

## 9. Success Criteria *(mandatory)*

- **SC-001**: Initial load of ~3300 contests completes in under 90 seconds (10 Mbps connection).
- **SC-002**: Verification with zero new contests completes in under 15 seconds.
- **SC-003**: Incremental update with 1 new contest completes in under 20 seconds.
- **SC-004**: Zero data loss on any failure scenario — 100% of existing data preserved.
- **SC-005**: All Prometheus metrics are exposed and increment correctly on each collection cycle.
- **SC-006**: A second game collector (e.g., Mega-Sena) can be added by creating only a subclass + Celery Beat entry, without modifying existing code.

---

## 10. Assumptions

- **Formato XLSX estável**: CEF mantém cabeçalhos consistentes. Mudanças disparam erro de parse.
- **Ordenação crescente**: Planilha sempre ordenada por concurso. Novos sorteios no final.
- **CEF sem API de metadados**: Download completo necessário a cada verificação.
- **Atraso na publicação**: CEF pode publicar horas após o sorteio. Scheduler não depende de horários exatos.
- **JSON é fonte primária offline**: Arquivo JSON é a fonte de verdade; banco é projeção para consulta via API.
- **Redis disponível**: Redis rodando como broker Celery — essencial para scheduler.
- **Volume de dados**: ~3300 concursos × ~32 campos = < 10 MB. Gerenciável sem soluções complexas.

---

## 11. Project Structure

```
.
├── docker-compose.yml
├── .env.example
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py          # GET /health, POST /collect/manual
│   │   └── dependencies.py    # auth, rate limiting
│   ├── collectors/
│   │   ├── base.py            # BaseLotteryCollector (abstract)
│   │   ├── lotofacil.py       # LotofacilCollector
│   │   └── (future: megasena.py, quina.py)
│   ├── models/
│   │   ├── schemas.py         # Pydantic validation models
│   │   └── database.py        # asyncpg connection, queries
│   ├── tasks/
│   │   ├── celery_app.py
│   │   └── periodic.py        # Celery Beat schedule
│   ├── utils/
│   │   ├── logging_config.py  # JSON structured logging
│   │   ├── metrics.py         # Prometheus exposition
│   │   └── security.py        # sanitization, validation
│   └── main.py                # FastAPI app
├── data/                      # mounted volume
│   └── lotofacil.json
├── tests/
│   ├── test_collector.py
│   └── test_api.py
└── requirements.txt
```
