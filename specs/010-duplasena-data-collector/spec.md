# Feature Specification: Dupla Sena Data Collector

**Feature Branch**: `010-duplasena-data-collector`
**Created**: 2026-05-13
**Status**: Draft
**Input**: Especificação técnica para coleta de sorteios da Caixa Econômica Federal (CEF), específica para o jogo Dupla Sena.

---

## 1. Technical Overview

Coleta automatizada do histórico completo de sorteios da Dupla Sena a partir da planilha oficial da CEF, com armazenamento em JSON local (`./data/duplasena.json`) e em tabela dedicada no banco PostgreSQL (`loterias_resultados_duplasena`). Carga inicial integral na primeira execução; atualizações incrementais via scheduler Celery Beat com intervalo fixo de 6 horas + verificação extra 1 hora após dias de sorteio (segundas, quartas e sextas, 22h). Stack assíncrona obrigatória: FastAPI + HTTPX + Polars + asyncpg + orjson + Celery/Redis.

**Particularidade da Dupla Sena**: Cada concurso possui **dois sorteios independentes** (Sorteio 1 e Sorteio 2), cada um com 6 bolas, totalizando 12 números por concurso, além de campos de premiação separados para cada sorteio.

---

## 2. Data Source

| Propriedade | Valor |
|---|---|
| **URL** | `https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Dupla-Sena` |
| **Formato** | Planilha eletrônica (XLSX), ordenada por concurso crescente |
| **Primeira linha** | Cabeçalho com nomes das colunas |
| **Campos por linha** | Concurso, Data Sorteio, Bola1 sorteio 1, Bola2 sorteio 1, Bola3 sorteio 1, Bola4 Sorteio 1, Bola5 sorteio 1, Bola6 sorteio 1, Ganhadores 6 acertos Sorteio 1, Cidade / UF, Rateio 6 acertos Sorteio 1, Ganhadores 5 acertos Sorteio 1, Rateio 5 acertos Sorteio 1, Ganhadores 4 acertos Sorteio 1, Rateio 4 acertos Sorteio 1, Ganhadores 3 acertos Sorteio 1, Rateio 3 acertos Sorteio 1, Bola1 sorteio 2 a Bola6 sorteio 2, Ganhadores 6 acertos Sorteio2, Rateio 6 acertos Sorteio 2, Ganhadores 5 acertos Sorteio2, Rateio 5 acertos Sorteio 2, Ganhadores 4 acertos Sorteio2, Rateio 4 acertos Sorteio 2, Ganhadores 3 acertos Sorteio2, Rateio 3 acertos Sorteio 2, Acumulado 6 acertos sorteio 1, Arrecadacao Total, Estimativa Prêmio, Acumulado Sorteio Especial Dupla de Páscoa, Observação |

---

## 3. Behavior

### 3.1 Initial Load (First Execution)

- Download the complete spreadsheet from the CEF URL.
- Parse all rows using Polars (`pl.read_excel()`).
- Convert each row to a JSON object preserving original column names.
- Save as `./data/duplasena.json` (or `DATA_PATH`/`duplasena.json`).
- Bulk insert all records into `loterias_resultados_duplasena` using `asyncpg.copy_from()`.

### 3.2 Periodic Updates (Scheduler)

- **Fixed interval**: 6 hours (configurable via `UPDATE_INTERVAL_HOURS`).
- **Mechanism**:
  1. Download the complete spreadsheet.
  2. Compare max `Concurso` in local JSON with max `Concurso` in new spreadsheet.
  3. If no new contests → discard download.
  4. If new contests exist:
     - Read JSON, append new objects, rewrite entire file.
     - Insert only new records into database (incremental).

### 3.3 Extra Verification on Draw Days

- Dupla Sena draws: **Mondays, Wednesdays and Fridays at 21:00 BRT**.
- Extra check at **22:00 BRT** on draw days.

---

## 4. User Scenarios & Testing *(mandatory)*

### User Story 1 — Initial Load (Priority: P1)

**Acceptance Scenarios**:

1. **Given** que `./data/duplasena.json` não existe, **When** o coletor executa, **Then** a planilha é baixada, convertida via Polars e orjson, e o JSON é criado.
2. **Given** o JSON gerado, **When** a exportação para o banco é concluída, **Then** `loterias_resultados_duplasena` contém o mesmo número de registros.

### User Story 2 — Incremental Update (Priority: P1)

**Acceptance Scenarios**:

1. **Given** o último concurso local é N, **When** o scheduler executa e a planilha contém N+M, **Then** apenas M novos são adicionados.
2. **Given** scheduler executa sem novos concursos, **Then** JSON e banco inalterados.

### User Story 3 — Error Resilience (Priority: P2)

**Acceptance Scenarios**:

1. **Given** dados existentes, **When** download ou parse falha, **Then** dados anteriores intactos, erro logado.

---

## 5. Data Model

### JSON: `./data/duplasena.json`

```json
{
  "meta": {
    "jogo": "Duplasena",
    "url_origem": "https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Dupla-Sena",
    "ultima_atualizacao": "2026-05-13T03:00:00Z",
    "ultima_verificacao": "2026-05-13T09:00:00Z",
    "total_concursos": 2800,
    "versao_formato": "1.0"
  },
  "concursos": [
    {
      "Concurso": 2800,
      "Data Sorteio": "2026-05-09",
      "Bola1 sorteio 1": 3, "Bola2 sorteio 1": 12, "Bola3 sorteio 1": 23,
      "Bola4 Sorteio 1": 34, "Bola5 sorteio 1": 40, "Bola6 sorteio 1": 48,
      "Ganhadores 6 acertos  Sorteio 1": 1,
      "Cidade / UF": "São Paulo/SP",
      "Rateio 6 acertos  Sorteio 1": 1200000.00,
      "Ganhadores 5 acertos Sorteio 1": 30,
      "Rateio 5 acertos Sorteio 1": 4500.00,
      "Ganhadores 4 acertos Sorteio 1": 1500,
      "Rateio 4 acertos Sorteio 1": 180.00,
      "Ganhadores 3 acertos Sorteio 1": 25000,
      "Rateio 3 acertos Sorteio 1": 12.00,
      "Bola1 sorteio 2": 5, "Bola2 sorteio 2": 14, "Bola3 sorteio 2": 22,
      "Bola4 Sorteio 2": 33, "Bola5 sorteio 2": 41, "Bola6 sorteio 2": 50,
      "Ganhadores 6 acertos Sorteio2": 0,
      "Rateio 6 acertos  Sorteio 2": 0,
      "Ganhadores 5 acertos Sorteio2": 15,
      "Rateio 5 acertos Sorteio 2": 5200.00,
      "Ganhadores 4 acertos Sorteio2": 800,
      "Rateio 4 acertos Sorteio 2": 200.00,
      "Ganhadores 3 acertos Sorteio2": 18000,
      "Rateio 3 acertos Sorteio 2": 15.00,
      "Acumulado 6 acertos sorteio 1": true,
      "Arrecadacao Total": 12500000.00,
      "Estimativa Prêmio": 3000000.00,
      "Acumulado Sorteio Especial Dupla de Páscoa": false,
      "Observação": ""
    }
  ]
}
```

### Database: `loterias_resultados_duplasena`

```sql
CREATE TABLE loterias_resultados_duplasena (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    "Concurso" INTEGER NOT NULL,
    "Data Sorteio" DATE NOT NULL,

    -- Sorteio 1 (6 balls + prizes)
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

    -- Sorteio 2 (6 balls + prizes)
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

    -- Aggregate fields
    "Acumulado 6 acertos sorteio 1" BOOLEAN DEFAULT false,
    "Arrecadacao Total" DECIMAL(14,2),
    "Estimativa Prêmio" DECIMAL(14,2),
    "Acumulado Sorteio Especial Dupla de Páscoa" BOOLEAN DEFAULT false,
    "Observação" TEXT,

    coletado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    hash_combinacao VARCHAR(64) NOT NULL,
    dezenas_ordenadas INTEGER[] NOT NULL,

    CONSTRAINT uq_duplasena_concurso UNIQUE ("Concurso"),
    CONSTRAINT uq_duplasena_hash UNIQUE (hash_combinacao)
);

CREATE INDEX idx_duplasena_data ON loterias_resultados_duplasena ("Data Sorteio");
CREATE INDEX idx_duplasena_dezenas ON loterias_resultados_duplasena USING GIN (dezenas_ordenadas);
```

---

## 6. Functional Requirements

### Initial Load
- **FR-001**: System MUST download the complete XLSX on first run.
- **FR-002**: Parse with Polars (`pl.read_excel()`), never Pandas.
- **FR-003**: Serialize with orjson, never stdlib `json`.
- **FR-004**: Save JSON to `./data/duplasena.json`.
- **FR-005**: Bulk insert via asyncpg `copy_from()`.

### Incremental Updates
- **FR-006**: Periodic checks every 6 hours via Celery Beat.
- **FR-007**: Extra check at 22:00 BRT on draw days (Mon, Wed, Fri).
- **FR-008**: Compare max `Concurso` to detect new records.
- **FR-009**: Read JSON, append new, rewrite entire file.
- **FR-010**: Insert only new records (incremental).
- **FR-011**: No rewrite if no new contests.

### Error Handling
- **FR-012**: Download failure → log ERROR, abort, preserve data, GlitchTip alert.
- **FR-013**: Parse failure → log details, abort, preserve file.
- **FR-014**: JSON write failure → restore backup, log CRITICAL.
- **FR-015**: DB insert failure → rollback, log ERROR.
- **FR-016**: Timeout → retry 3x exponential backoff.

### Monitoring
- **FR-017**: Expose `lottery_download_duration_seconds{game="duplasena"}`, `lottery_new_contests_total{game="duplasena"}`, `lottery_last_success_timestamp{game="duplasena"}`, `lottery_errors_total{game="duplasena",type="download|parse|db|json"}`.
- **FR-018**: Structured JSON logs with `timestamp`, `level`, `game`, `contest`, `message`, `trace_id`.

### Security (OWASP/CWE)
- **FR-019**: Parameterized queries only (CWE-89).
- **FR-020**: Pydantic validation before insert (CWE-20).
- **FR-021**: Logs must not contain raw data (CWE-200).
- **FR-022**: Containers as non-root (OWASP A05).
- **FR-023**: Admin endpoints require JWT (OWASP A07).
- **FR-024**: HTTP timeout: `httpx.Timeout(connect=5.0, read=30.0, write=5.0, pool=5.0)` (CWE-400).
- **FR-025**: JSON filename fixed as `duplasena.json` (CWE-73).

### Coexistence
- **FR-026**: Each game has its own table `loterias_resultados_{jogo}`.
- **FR-027**: Each game has its own JSON file `./data/{jogo}.json`.
- **FR-028**: Each game has its own Celery Beat task.
- **FR-029**: `BaseLotteryCollector` abstract class.
- **FR-030**: `DuplasenaCollector` inherits `BaseLotteryCollector`.

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
| Error Tracking | GlitchTip / Sentry |
| Rate Limiting | slowapi + Redis |
| Auth | python-jose (JWT) |
| File Security | ClamAV (optional) |

**Forbidden**: Pandas, `requests` sync, sqlite3, `json` stdlib, pure sync.

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

- **SC-001**: Initial load of ~2800 contests (dual draw) completes in under 90 seconds.
- **SC-002**: Verification with zero new contests completes in under 15 seconds.
- **SC-003**: Incremental update with 1 new contest completes in under 20 seconds.
- **SC-004**: Zero data loss on any failure scenario.
- **SC-005**: All Prometheus metrics increment correctly.
- **SC-006**: Adding a new game requires only a subclass + Celery Beat entry.

---

## 10. Assumptions

- **Formato XLSX estável**: CEF mantém cabeçalhos. Mudanças disparam erro de parse.
- **Dois sorteios por concurso**: Cada linha contém 12 bolas (6 + 6). O hash é calculado sobre as 12 bolas ordenadas.
- **CEF sem API de metadados**: Download completo necessário a cada verificação.
- **JSON é fonte primária offline**: Banco é projeção para consulta via API.
- **Redis disponível**: Essencial para broker Celery.

---

## 11. Project Structure

```
.
├── docker-compose.yml
├── .env.example
├── app/
│   ├── api/
│   ├── collectors/
│   │   ├── base.py
│   │   ├── duplasena.py
│   │   └── (future)
│   ├── models/
│   ├── tasks/
│   ├── utils/
│   └── main.py
├── data/
│   └── duplasena.json
├── tests/
└── requirements.txt
```
