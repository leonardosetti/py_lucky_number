# Lucky Number — Kickstart Manual

Veja o produto rodando em **<5 minutos**.

---

## Opção 1: Tudo com Docker (recomendado)

### API + Banco + Redis + Frontend Web

```bash
# 1. Sobe tudo (API em :8000, Frontend em :3000)
docker compose --profile dev up --build -d

# 2. Roda migrações + seed
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed.py

# 3. Abre no navegador
open http://localhost:8000/docs        # API docs (Swagger)
open http://localhost:3000             # Frontend Web
```

### Testar a API

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Listar jogos disponíveis
curl http://localhost:8000/api/v1/jogos-disponiveis | jq

# Registrar novo usuário
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@email.com","senha":"Teste@123"}'

# Login (guarde o token)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@email.com","senha":"Teste@123"}'

# Gerar combinações (use o token do login)
curl -X POST http://localhost:8000/api/v1/gerar-apostas \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{"jogo":"megasena","quantidade":3,"dezenas_por_aposta":6}'
```

---

## Opção 2: Manual (sem Docker para o Python)

### 2.1 Banco + Redis via Docker

```bash
docker compose --profile dev up db redis -d
```

### 2.2 Backend Python

```bash
# Instalar dependências
pip install -r requirements-dev.txt
pip install -e .

# Migrar + seed
alembic upgrade head
python scripts/seed.py

# Iniciar servidor
make dev
# ou: uvicorn lucky_number.main:app --reload --host 0.0.0.0 --port 8000
```

### 2.3 Frontend Web (Next.js)

```bash
cd web
npm install
npm run dev
# Abre em http://localhost:3000
```

### 2.4 Ver tudo funcionando

| Recurso | URL |
|---|---|
| API (FastAPI) | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| Frontend Web | http://localhost:3000 |
| Health Check | http://localhost:8000/api/v1/health |
| Métricas Prometheus | http://localhost:8000/metrics |

---

## Opção 3: Só a API (sem banco — modo degraded)

Sem PostgreSQL/Redis, a API roda mas apenas endpoints **estáticos** funcionam:

```bash
ENVIRONMENT=test uvicorn lucky_number.main:app --reload --host 0.0.0.0 --port 8000

# Testar (funciona sem DB):
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/jogos-disponiveis
```

---

## Credenciais Padrão (seed)

| Papel | Email | Senha |
|---|---|---|
| Admin | admin@luckynumber.app | Admin@123 |
| Apostador | apostador@luckynumber.app | Apostador@123 |

---

## Comandos Úteis

```bash
make test         # Rodar testes
make coverage     # Relatório de cobertura
make lint         # Verificar qualidade do código
make migrate      # Rodar migrações pendentes
make dev          # Iniciar servidor dev
```

---

## Parar Tudo

```bash
docker compose --profile dev down
```
