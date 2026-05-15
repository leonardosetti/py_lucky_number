# Feature Specification: Super Sete Data Collector

**Feature Branch**: `016-supersete-data-collector`
**Created**: 2026-05-13
**Status**: Draft
**Input**: Especificação técnica para coleta de sorteios da Caixa Econômica Federal (CEF), específica para o jogo Super Sete.

---

## 1. Technical Overview

Coleta automatizada do histórico completo de sorteios do Super Sete a partir da planilha oficial da CEF, com armazenamento em JSON local (`./data/supersete.json`) e em tabela dedicada no banco PostgreSQL (`loterias_resultados_supersete`). Carga inicial integral na primeira execução; atualizações incrementais via scheduler Celery Beat com intervalo fixo de 6 horas + verificação extra 1 hora após dias de sorteio (segundas, quartas e sextas, 22h). Stack assíncrona obrigatória: FastAPI + HTTPX + Polars + asyncpg + orjson + Celery/Redis.

**Particularidade do Super Sete**: 7 colunas independentes, cada uma com um dígito de 0 a 9. O resultado forma um número de 7 dígitos. Diferentemente dos demais jogos, não há "bolas" — cada coluna é um sorteio individual de um dígito.

---

## 2. Data Source

| Propriedade | Valor |
|---|---|
| **URL** | `https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Super-Sete` |
| **Formato** | Planilha eletrônica (XLSX), ordenada por concurso crescente |
| **Primeira linha** | Cabeçalho com nomes das colunas |
| **Campos por linha** | Concurso, Data Sorteio, Coluna 1, Coluna 2, Coluna 3, Coluna 4, Coluna 5, Coluna 6, Coluna 7, Ganhadores 7 acertos, Cidade / UF, Rateio 7 acertos, Ganhadores 6 acertos, Rateio 6 acertos, Ganhadores 5 acertos, Rateio 5 acertos, Ganhadores 4 acertos, Rateio 4 acertos, Ganhadores 3 acertos, Rateio 3 acertos, Acumulado 7 acertos, Arrecadação Total, Estimativa Prêmio, Observação |

---

## 3. Behavior

### 3.1 Initial Load (First Execution)

- Download the complete spreadsheet from the CEF URL.
- Parse all rows using Polars (`pl.read_excel()`).
- Convert each row to a JSON object preserving original column names.
- Save as `./data/supersete.json` (or `DATA_PATH`/`supersete.json`).
- Bulk insert all records into `loterias_resultados_supersete` using `asyncpg.copy_from()`.

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

- Super Sete draws: **Mondays, Wednesdays and Fridays at 21:00 BRT**.
- Extra check at **22:00 BRT** on draw days.

---

## 4. User Scenarios & Testing *(mandatory)*

### User Story 1 — Initial Load (Priority: P1)

**Acceptance Scenarios**:

1. **Given** que `./data/supersete.json` não existe, **When** o coletor executa, **Then** a planilha é baixada e convertida via Polars e orjson.
2. **Given** o JSON gerado, **When** a exportação para o banco é concluída, **Then** `loterias_resultados_supersete` contém o mesmo número de registros que o JSON.

### User Story 2 — Incremental Update (Priority: P1)

**Acceptance Scenarios**:

1. **Given** o último concurso local é N, **When** o scheduler executa e a planilha contém N+M, **Then** apenas M novos são adicionados.
2. **Given** scheduler executa sem novos concursos, **Then** JSON e banco inalterados.

### User Story 3 — Error Resilience (Priority: P2)

**Acceptance Scenarios**:

1. **Given** dados existentes, **When** download ou parse falha, **Then** dados anteriores intactos, erro logado.

---

## 5. Data Model

### JSON: `./data/supersete.json`

```json
{
  "meta": {
    "jogo": "Supersete",
    "url_origem": "https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Super-Sete",
    "ultima_atualizacao": "2026-05-13T03:00:00Z",
    "ultima_verificacao": "2026-05-13T09:00:00Z",
    "total_concursos": 800,
    "versao_formato": "1.0"
  },
  "concursos": [
    {
      "Concurso": 800,
      "Data Sorteio": "2026-05-09",
      "Coluna 1": 3, "Coluna 2": 7, "Coluna 3": 0,
      "Coluna 4": 5, "Coluna 5": 2, "Coluna 6": 9,
      "Coluna 7": 1,
      "Ganhadores 7 acertos": 0,
      "Cidade / UF": "",
      "Rateio 7 acertos": 0,
      "Ganhadores 6 acertos": 2,
      "Rateio 6 acertos": 35000.00,
      "Ganhadores 5 acertos": 85,
      "Rateio 5 acertos": 1200.00,
      "Ganhadores 4 acertos": 3200,
      "Rateio 4 acertos": 60.00,
      "Ganhadores 3 acertos": 45000,
      "Rateio 3 acertos": 5.00,
      "Acumulado 7 acertos": true,
      "Arrecadação Total": 7200000.00,
      "Estimativa Prêmio": 2500000.00,
      "Observação": ""
    }
  ]
}
```

### Database: `loterias_resultados_supersete`

```sql
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
    "Arrecadação Total" DECIMAL(14,2),
    "Estimativa Prêmio" DECIMAL(14,2),
    "Observação" TEXT,

    coletado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    hash_combinacao VARCHAR(64) NOT NULL,

    CONSTRAINT uq_supersete_concurso UNIQUE ("Concurso"),
    CONSTRAINT uq_supersete_hash UNIQUE (hash_combinacao)
);

CREATE INDEX idx_supersete_data ON loterias_resultados_supersete ("Data Sorteio");
```

---

## 6. Functional Requirements

### Initial Load
- **FR-001**: System MUST download the complete XLSX on first run.
- **FR-002**: Parse with Polars (`pl.read_excel()`), never Pandas.
- **FR-003**: Serialize with orjson, never stdlib `json`.
- **FR-004**: Save JSON to `./data/supersete.json`.
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
- **FR-017**: Expose `lottery_download_duration_seconds{game="supersete"}`, `lottery_new_contests_total{game="supersete"}`, `lottery_last_success_timestamp{game="supersete"}`, `lottery_errors_total{game="supersete",type="download|parse|db|json"}`.
- **FR-018**: Structured JSON logs with `timestamp`, `level`, `game`, `contest`, `message`, `trace_id`.

### Security (OWASP/CWE)
- **FR-019**: Parameterized queries only (CWE-89).
- **FR-020**: Pydantic validation before insert (CWE-20).
- **FR-021**: Logs must not contain raw data (CWE-200).
- **FR-022**: Containers as non-root (OWASP A05).
- **FR-023**: Admin endpoints require JWT (OWASP A07).
- **FR-024**: HTTP timeout: `httpx.Timeout(connect=5.0, read=30.0, write=5.0, pool=5.0)` (CWE-400).
- **FR-025**: JSON filename fixed as `supersete.json` (CWE-73).

### Coexistence
- **FR-026**: Each game has its own table `loterias_resultados_{jogo}`.
- **FR-027**: Each game has its own JSON file `./data/{jogo}.json`.
- **FR-028**: Each game has its own Celery Beat task.
- **FR-029**: `BaseLotteryCollector` abstract class.
- **FR-030**: `SuperseteCollector` inherits `BaseLotteryCollector`.

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

- **SC-001**: Initial load of ~800 contests completes in under 30 seconds.
- **SC-002**: Verification with zero new contests in under 15 seconds.
- **SC-003**: Incremental update with 1 new contest in under 20 seconds.
- **SC-004**: Zero data loss on any failure scenario.
- **SC-005**: All Prometheus metrics increment correctly.
- **SC-006**: Adding a new game requires only a subclass + Celery Beat entry.

---

## 10. Assumptions

- **Formato XLSX estável**: CEF mantém cabeçalhos. Mudanças disparam erro de parse.
- **Colunas vs Bolas**: Cada "Coluna N" é um dígito independente (0–9). Não há relação entre colunas.
- **Hash**: Calculado sobre a string `supersete|{Concurso}|{C1}{C2}{C3}{C4}{C5}{C6}{C7}`.
- **Range**: Cada coluna aceita apenas valores 0–9 (validação Pydantic).
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
│   │   ├── supersete.py
│   │   └── (future)
│   ├── models/
│   ├── tasks/
│   ├── utils/
│   └── main.py
├── data/
│   └── supersete.json
├── tests/
└── requirements.txt
```
