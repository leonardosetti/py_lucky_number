# Feature Specification: Lotomania Data Collector

**Feature Branch**: `013-lotomania-data-collector`
**Created**: 2026-05-13
**Status**: Draft
**Input**: Especificação técnica para coleta de sorteios da Caixa Econômica Federal (CEF), específica para o jogo Lotomania.

---

## 1. Technical Overview

Coleta automatizada do histórico completo de sorteios da Lotomania a partir da planilha oficial da CEF, com armazenamento em JSON local (`./data/lotomania.json`) e em tabela dedicada no banco PostgreSQL (`loterias_resultados_lotomania`). Carga inicial integral na primeira execução; atualizações incrementais via scheduler Celery Beat com intervalo fixo de 6 horas + verificação extra 1 hora após dias de sorteio (segundas, quartas e sextas, 22h). Stack assíncrona obrigatória: FastAPI + HTTPX + Polars + asyncpg + orjson + Celery/Redis.

**Particularidade da Lotomania**: 20 bolas sorteadas por concurso (range 0–99). Possui faixa de premiação especial "Nenhum Número" (acertar zero números). Range inclui 0 (zero), diferentemente dos demais jogos.

---

## 2. Data Source

| Propriedade | Valor |
|---|---|
| **URL** | `https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Lotomania` |
| **Formato** | Planilha eletrônica (XLSX), ordenada por concurso crescente |
| **Primeira linha** | Cabeçalho com nomes das colunas |
| **Campos por linha** | Concurso, Data Sorteio, Bola1 a Bola20, Ganhadores 20 acertos, Cidade / UF, Rateio 20 acertos, Ganhadores 19 acertos, Rateio 19 acertos, Ganhadores 18 acertos, Rateio 18 acertos, Ganhadores 17 acertos, Rateio 17 acertos, Ganhadores 16 acertos, Rateio 16 acertos, Ganhadores 15 acertos, Rateio 15 acertos, Ganhadores Nenhum Número, Rateio Nenhum Número, Acumulado 20 acertos, Arrecadação Total, Estimativa Prêmio, Observação |

---

## 3. Behavior

### 3.1 Initial Load (First Execution)

- Download the complete spreadsheet from the CEF URL.
- Parse all rows using Polars (`pl.read_excel()`).
- Convert each row to a JSON object preserving original column names.
- Save as `./data/lotomania.json` (or `DATA_PATH`/`lotomania.json`).
- Bulk insert all records into `loterias_resultados_lotomania` using `asyncpg.copy_from()`.

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

- Lotomania draws: **Mondays, Wednesdays and Fridays at 21:00 BRT**.
- Extra check at **22:00 BRT** on draw days.

---

## 4. User Scenarios & Testing *(mandatory)*

### User Story 1 — Initial Load (Priority: P1)

**Acceptance Scenarios**:

1. **Given** que `./data/lotomania.json` não existe, **When** o coletor executa, **Then** a planilha é baixada e convertida via Polars e orjson.
2. **Given** o JSON gerado, **When** a exportação para o banco é concluída, **Then** `loterias_resultados_lotomania` contém o mesmo número de registros que o JSON.

### User Story 2 — Incremental Update (Priority: P1)

**Acceptance Scenarios**:

1. **Given** o último concurso local é N, **When** o scheduler executa e a planilha contém N+M, **Then** apenas M novos são adicionados.
2. **Given** scheduler executa sem novos concursos, **Then** JSON e banco inalterados.

### User Story 3 — Error Resilience (Priority: P2)

**Acceptance Scenarios**:

1. **Given** dados existentes, **When** download ou parse falha, **Then** dados anteriores intactos, erro logado.

---

## 5. Data Model

### JSON: `./data/lotomania.json`

```json
{
  "meta": {
    "jogo": "Lotomania",
    "url_origem": "https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Lotomania",
    "ultima_atualizacao": "2026-05-13T03:00:00Z",
    "ultima_verificacao": "2026-05-13T09:00:00Z",
    "total_concursos": 2800,
    "versao_formato": "1.0"
  },
  "concursos": [
    {
      "Concurso": 2800,
      "Data Sorteio": "2026-05-09",
      "Bola1": 3, "Bola2": 12, "Bola3": 23, "Bola4": 34, "Bola5": 45,
      "Bola6": 56, "Bola7": 67, "Bola8": 78, "Bola9": 89, "Bola10": 0,
      "Bola11": 11, "Bola12": 22, "Bola13": 33, "Bola14": 44, "Bola15": 55,
      "Bola16": 66, "Bola17": 77, "Bola18": 88, "Bola19": 99, "Bola20": 7,
      "Ganhadores 20 acertos": 0,
      "Cidade / UF": "",
      "Rateio 20 acertos": 0,
      "Ganhadores 19 acertos": 2,
      "Rateio 19 acertos": 85000.00,
      "Ganhadores 18 acertos": 25,
      "Rateio 18 acertos": 3500.00,
      "Ganhadores 17 acertos": 400,
      "Rateio 17 acertos": 250.00,
      "Ganhadores 16 acertos": 3500,
      "Rateio 16 acertos": 40.00,
      "Ganhadores 15 acertos": 18000,
      "Rateio 15 acertos": 10.00,
      "Ganhadores Nenhum Número": 0,
      "Rateio Nenhum Número": 0,
      "Acumulado 20 acertos": true,
      "Arrecadação Total": 8500000.00,
      "Estimativa Prêmio": 3000000.00,
      "Observação": ""
    }
  ]
}
```

### Database: `loterias_resultados_lotomania`

```sql
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
    "Ganhadores Nenhum Número" INTEGER DEFAULT 0,
    "Rateio Nenhum Número" DECIMAL(14,2),
    "Acumulado 20 acertos" BOOLEAN DEFAULT false,
    "Arrecadação Total" DECIMAL(14,2),
    "Estimativa Prêmio" DECIMAL(14,2),
    "Observação" TEXT,

    coletado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    hash_combinacao VARCHAR(64) NOT NULL,
    dezenas_ordenadas INTEGER[] NOT NULL,

    CONSTRAINT uq_lotomania_concurso UNIQUE ("Concurso"),
    CONSTRAINT uq_lotomania_hash UNIQUE (hash_combinacao)
);

CREATE INDEX idx_lotomania_data ON loterias_resultados_lotomania ("Data Sorteio");
CREATE INDEX idx_lotomania_dezenas ON loterias_resultados_lotomania USING GIN (dezenas_ordenadas);
```

---

## 6. Functional Requirements

### Initial Load
- **FR-001**: System MUST download the complete XLSX on first run.
- **FR-002**: Parse with Polars (`pl.read_excel()`), never Pandas.
- **FR-003**: Serialize with orjson, never stdlib `json`.
- **FR-004**: Save JSON to `./data/lotomania.json`.
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
- **FR-017**: Expose `lottery_download_duration_seconds{game="lotomania"}`, `lottery_new_contests_total{game="lotomania"}`, `lottery_last_success_timestamp{game="lotomania"}`, `lottery_errors_total{game="lotomania",type="download|parse|db|json"}`.
- **FR-018**: Structured JSON logs with `timestamp`, `level`, `game`, `contest`, `message`, `trace_id`.

### Security (OWASP/CWE)
- **FR-019**: Parameterized queries only (CWE-89).
- **FR-020**: Pydantic validation before insert (CWE-20).
- **FR-021**: Logs must not contain raw data (CWE-200).
- **FR-022**: Containers as non-root (OWASP A05).
- **FR-023**: Admin endpoints require JWT (OWASP A07).
- **FR-024**: HTTP timeout: `httpx.Timeout(connect=5.0, read=30.0, write=5.0, pool=5.0)` (CWE-400).
- **FR-025**: JSON filename fixed as `lotomania.json` (CWE-73).

### Coexistence
- **FR-026**: Each game has its own table `loterias_resultados_{jogo}`.
- **FR-027**: Each game has its own JSON file `./data/{jogo}.json`.
- **FR-028**: Each game has its own Celery Beat task.
- **FR-029**: `BaseLotteryCollector` abstract class.
- **FR-030**: `LotomaniaCollector` inherits `BaseLotteryCollector`.

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

- **SC-001**: Initial load of ~2800 contests (20 balls each) completes in under 120 seconds.
- **SC-002**: Verification with zero new contests in under 15 seconds.
- **SC-003**: Incremental update with 1 new contest in under 20 seconds.
- **SC-004**: Zero data loss on any failure scenario.
- **SC-005**: All Prometheus metrics increment correctly.
- **SC-006**: Adding a new game requires only a subclass + Celery Beat entry.

---

## 10. Assumptions

- **Formato XLSX estável**: CEF mantém cabeçalhos. Mudanças disparam erro de parse.
- **Range 0–99**: Bolas podem incluir 0 (zero), diferentemente dos demais jogos.
- **Faixa especial**: "Nenhum Número" é uma faixa de premiação válida e deve ser preservada.
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
│   │   ├── lotomania.py
│   │   └── (future)
│   ├── models/
│   ├── tasks/
│   ├── utils/
│   └── main.py
├── data/
│   └── lotomania.json
├── tests/
└── requirements.txt
```
