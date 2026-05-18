# Lucky Number — Guia de Execução

## Pré-requisitos

| Componente | Versão | Obter |
|---|---|---|
| Python | 3.12+ | `python3 --version` |
| PostgreSQL | 16+ | `docker compose --profile dev up db` |
| Redis | 7+ | `docker compose --profile dev up redis` |
| Go (opcional) | 1.22+ | Apenas para o backup tool |

---

## 1. Ambiente de Desenvolvimento (dev)

### 1.1 Instalar dependências

```bash
pip install -r requirements-dev.txt
pip install -e .
```

### 1.2 Iniciar banco + Redis via Docker

```bash
docker compose --profile dev up db redis -d
```

### 1.3 Executar migrações

```bash
alembic upgrade head
```

### 1.4 Popular dados iniciais

```bash
python scripts/seed.py
```

### 1.5 Iniciar servidor

```bash
make dev
# ou
uvicorn lucky_number.main:app --reload --host 0.0.0.0 --port 8000
```

### 1.6 Acessar

| Recurso | URL |
|---|---|
| API | http://localhost:8000/api/v1 |
| Docs | http://localhost:8000/docs |
| Health | http://localhost:8000/api/v1/health |
| Metrics | http://localhost:8000/metrics |

---

## 2. Ambiente de Testes (test)

### Executar suite completa

```bash
ENVIRONMENT=test pytest tests/ -v --cov=src/lucky_number --cov-report=term
```

### Testes sem banco

O modo `ENVIRONMENT=test` desabilita rate limiting, CORS e TrustedHost,
permitindo que os testes rodem sem depender de infraestrutura externa.

---

## 3. Ambiente de Demonstração (demo)

```bash
docker compose --profile demo up -d
```

Acessar em http://localhost:8000

---

## 4. Ambiente de Produção (prod)

```bash
docker compose --profile prod up -d
```

Requer aprovação manual via GitHub Actions (`.github/workflows/cd.yml`).

---

## 5. API — Endpoints Disponíveis (42 rotas)

### Públicos
| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Index / landing |
| GET | `/api/v1/health` | Health check com status do DB |
| GET | `/api/v1/jogos-disponiveis` | Lista jogos de loteria |
| GET | `/metrics` | Métricas Prometheus |

### Autenticação
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/v1/auth/register` | Registrar novo usuário |
| POST | `/api/v1/auth/login` | Login (retorna JWT) |
| POST | `/api/v1/auth/refresh` | Renovar JWT |
| POST | `/api/v1/auth/logout` | Logout |

### Geração de Apostas
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/v1/gerar-apostas` | Gerar combinações |

### Combinações Salvas
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/combinacoes` | Listar (paginação 20) |
| POST | `/api/v1/combinacoes` | Salvar |
| DELETE | `/api/v1/combinacoes/{id}` | Excluir |
| PUT | `/api/v1/combinacoes/{id}/favorita` | Favoritar |

### Promessas
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/promessas` | Listar |
| POST | `/api/v1/promessas` | Criar |
| DELETE | `/api/v1/promessas/{id}` | Excluir |
| POST | `/api/v1/promessas/{id}/clone` | Clonar |
| POST | `/api/v1/promessas/{id}/compartilhar` | Compartilhar (HMAC) |

### Notificações
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/notifications` | Listar |
| PUT | `/api/v1/notifications/{id}/read` | Marcar como lida |

### Admin
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/admin/features` | Listar features |
| PUT | `/api/v1/admin/features/{slug}` | Alternar feature |
| GET | `/api/v1/admin/features/{slug}/audit` | Audit log |
| GET | `/api/v1/admin/users` | Listar usuários |
| POST | `/api/v1/admin/users` | Criar usuário |
| GET | `/api/v1/admin/users/{id}` | Detalhe |
| PUT | `/api/v1/admin/users/{id}` | Editar |
| DELETE | `/api/v1/admin/users/{id}` | Excluir (soft delete) |
| POST | `/api/v1/admin/users/{id}/clone` | Clonar |
| GET | `/api/v1/admin/roles` | Listar roles |
| POST | `/api/v1/admin/roles` | Criar role |
| PUT | `/api/v1/admin/roles/{id}` | Editar |
| DELETE | `/api/v1/admin/roles/{id}` | Excluir |
| POST | `/api/v1/admin/roles/{id}/clone` | Clonar |
| POST | `/api/v1/admin/notifications` | Criar notificação |
| GET | `/api/v1/admin/dashboard/summary` | Dashboard |
| GET | `/api/v1/admin/dashboard/events` | Eventos filtrados |

---

## 6. Testando agora (sem dependências externas)

A API pode ser iniciada em **modo teste** sem PostgreSQL ou Redis:

```bash
# Terminal 1: Iniciar servidor
ENVIRONMENT=test uvicorn lucky_number.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Testar health (funciona sem DB)
curl http://localhost:8000/api/v1/health
# Resposta: {"status":"degraded","database":"disconnected","timestamp":"..."}

# Testar jogos disponíveis (dados estáticos do config.py)
curl http://localhost:8000/api/v1/jogos-disponiveis

# Testar docs interativas
open http://localhost:8000/docs
```

> ⚠️ Endpoints que exigem banco de dados (`/auth/*`, `/combinacoes/*`,
> `/promessas/*`, `/admin/*`) retornarão erro 500 sem PostgreSQL rodando.
> Para funcionalidade completa, execute `docker compose --profile dev up db redis`.
