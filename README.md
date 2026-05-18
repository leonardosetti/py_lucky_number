# Lucky Number

**Gere combinações únicas para loterias da Caixa — números que nunca foram sorteados antes.**

[![CI](https://github.com/leonardosetti/py_lucky_number/actions/workflows/ci.yml/badge.svg)](https://github.com/leonardosetti/py_lucky_number/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)

---

## Stack

| Camada | Tecnologia |
|---|---|
| API | Python 3.12+ / FastAPI / Pydantic v2 |
| Banco | PostgreSQL 16+ / SQLAlchemy 2.0 / Alembic |
| Cache | Redis 7+ |
| Task Queue | Celery + Redis |
| Coleta | Polars / orjson / HTTPX |
| Frontend Web | Next.js 16 / TypeScript / Tailwind |
| Mobile | Kotlin/Compose (Android API 26+) + Swift/SwiftUI (iOS 15+) |
| Backup | pgBackRest + Go tool |
| Infra | Docker / Docker Compose / GitHub Actions |

## Quick Start

```bash
# 1. Instalar dependências
pip install -r requirements-dev.txt && pip install -e .

# 2. Iniciar banco + Redis
docker compose --profile dev up db redis -d

# 3. Migrar e popular
alembic upgrade head
python scripts/seed.py

# 4. Rodar
uvicorn lucky_number.main:app --reload --port 8000
```

Acessar: http://localhost:8000/docs

## Estrutura

```
src/
├── lucky_number/        # Backend Python/FastAPI
│   ├── api/             # Rotas, auth, dependências
│   ├── database/        # Engine, modelos SQLAlchemy
│   ├── features/        # Feature toggles
│   └── services/        # Lógica de negócio
├── collectors/          # 10 coletores CEF (BaseLotteryCollector)
├── tasks/               # Celery
web/                     # Next.js 16 frontend
mobile/                  # Kotlin Android + Swift iOS
specs/                   # 21 especificações SDD
```

## Licença

MIT — see [LICENSE](LICENSE).
