# Lucky Number — TODOs do Projeto

> Arquivo central de acompanhamento de tarefas pendentes, especificações não geradas e
> inconsistências identificadas nas análises de consistência entre artefatos (Constitution,
> Specs, Plan). Atualizado em: 2026-05-26. Última revisão: 2026-05-26 (specs 004, 020, 021 resolvidas).

---

## Legenda

| Marcação | Significado |
|---|---|
| 🔴 CRITICAL | Viola Constitution ou bloqueia funcionalidade baseline |
| 🟠 HIGH | Impacta qualidade, segurança ou integridade |
| 🟡 MEDIUM | Melhoria necessária, não bloqueante |
| 🟢 LOW | Refinamento opcional |

---

## 1. Resolvidos nesta iteração (2026-05-26)

### ✅ Constitution — Segurança, Robustez, Performance, Usabilidade

- [x] **Senhas**: Adicionado CWE-521 (password policy obrigatória: 8+ chars, maiúscula, minúscula, número, especial) + limite máximo de 128 chars
- [x] **Account Lockout**: CWE-307 — 5 tentativas de login falhas bloqueiam por 15 min
- [x] **CSRF**: CWE-352 — toda mutação requer CSRF token
- [x] **Randomness**: CWE-338 — `secrets.SystemRandom` substitui `random`
- [x] **JWT Secret**: `JWT_SECRET_KEY` sem fallback hardcoded (CWE-522)
- [x] **Rate limiting expandido**: 10 req/min geração, 5 req/min login, bloqueio 15 min
- [x] **RBAC real**: `require_permission` agora consulta `role_permissions` table

### ✅ Config — 11 jogos no lugar de 6

- [x] Adicionados: Lotomania, Timemania, +Milionária, Super Sete, Loteca
- [x] `MINIMO_POR_JOGO` por jogo (em vez de `MINIMO_INEGOCIAVEL` global)
- [x] `config.api_endpoint` corrigido para todos os 11 jogos

### ✅ Models — Criados 4 modelos faltantes

- [x] `Combinacao` (`combinacoes_salvas`)
- [x] `Promessa` (`promessas`)
- [x] `SystemNotification` + `NotificationDelivery`
- [x] `UsageEvent`
- [x] `models/__init__.py` atualizado com todos os exports

### ✅ Services — Criados 2 serviços faltantes

- [x] `combinacao_service.py` — CRUD + FIFO 200 + hash único
- [x] `promessa_service.py` — CRUD + FIFO 50 + sharing hash

### ✅ Auth — Endpoints de segurança

- [x] `DELETE /auth/account` — soft delete + anonimização LGPD
- [x] `validate_password_strength()` em register, reset, change-password, admin create
- [x] Login lockout tracker (in-memory; Redis em produção)

### ✅ Gerador — Criptograficamente seguro

- [x] `secrets.SystemRandom` em vez de `random` (CWE-338)
- [x] Validação por jogo específica (min_dezenas do config)

### ✅ Routes — Refatoração de segurança

- [x] Todos os imports movidos para top-level (fim de `__import__` e inline imports)
- [x] Health check inclui Redis ping
- [x] `admin_count` usa `func.count()` em vez de load all
- [x] `clone_user` gera nova senha aleatória (não clona hash)
- [x] Validação de `dezenas` vazia em save_combinacao

### ✅ Spec 004 — Refatoração (FR numbering + cross-references)

- [x] FR numbering corrigido: FR-036/037 → FR-028/029, Audit & Performance reordenado como FR-030–037
- [x] Seção "Relationship with Other Specs" expandida para specs 019–026
- [x] Assumptions atualizadas (FR-036 → FR-028, specs 019-021 → 019-026)
- [x] Checklist atualizado para v2.4

### ✅ Coletores — Enriquecimento de dados + Celery Beat + correções

- [x] `base.py`: `enrich_record()` computa `hash_combinacao` (SHA-256), `dezenas_ordenadas`, `coletado_em`
- [x] `bulk_insert_to_db()`: transação + tratamento de erro + fallback sem DB crash
- [x] `collect()`: enrich antes de salvar JSON/DB; erro DB não corrompe JSON
- [x] Federal: override para `hash_extracao` (sem dezenas)
- [x] Super Sete / Loteca: `ball_prefix = "Coluna"`, `has_dezenas = False`
- [x] +Milionária: `trevos_ordenados` + hash combinado bolas+trevos
- [x] Migration 003: `"Mês da Sorte"` acento corrigido (Dia de Sorte)
- [x] `periodic.py`: 11 tasks Celery Beat com `COLETA_INTERVALO_MINUTOS`
- [x] `__init__.py`: exports todos os 11 coletores

### ✅ Banco — 10 tabelas `loterias_resultados_*` + `audit_log` + HistoryProvider

- [x] Migration 003 criada com todas as 10 tabelas `loterias_resultados_{jogo}` via raw SQL
- [x] Tabela `audit_log` criada (modelo SQLAlchemy + migration)
- [x] `lottery_result.py` — registro de nomes de tabelas + `DatabaseHistoryProvider`
- [x] `HistoryProvider` real consulta `dezenas_ordenadas` de cada jogo
- [x] `get_gerador()` wired com `DatabaseHistoryProvider` via `get_db_session()`
- [x] Tasks T098/T099 do plano marcadas como concluídas

### ✅ Specs 020 e 021 — Revisão e alinhamento

- [x] Gaps table atualizada com status real das dependências de backend
- [x] Referências adicionadas para specs 022–026 (registration, password recovery)
- [x] Framework mobile confirmado como nativo (Kotlin/Compose + Swift/SwiftUI)
- [x] Checklists atualizados

### ✅ .env.example

- [x] `JWT_SECRET_KEY` sem fallback default
- [x] `ACTIVATION_CODE_TTL_HOURS`, `MAX_ACTIVATION_ATTEMPTS`, `REGISTRATION_COOLDOWN_SECONDS`
- [x] `LOGIN_LOCKOUT_MINUTES`, `MAX_LOGIN_ATTEMPTS`

---

## 2. Specs Não Geradas (Missing Specs)

### 🟡 [020] Web Frontend — Interface Web Responsiva

**Motivação**: Constitution Princípio VII exige aplicação web responsiva (mobile-first).
Spec 020 existe e foi revisada (v2026-05-26). Scaffold Next.js 16 + páginas + Playwright
criados. Pendências de implementação:
- [ ] Página de perfil (`/profile`) com alteração de senha
- [ ] Página de ativação de conta (`/activate`)
- [ ] Fluxo de redefinição de senha no frontend
- [ ] Integração com CAPTCHA no cadastro
- [ ] Suporte a tema claro/escuro consistente
- [ ] Testes E2E com Playwright (existe scaffold)

### 🟡 [021] Mobile App — Android e iOS

**Motivação**: Constitution Princípio VII determina mobile nativo.
Spec 021 existe e foi revisada (v2026-05-26). Scaffold Android (Kotlin) + iOS (Swift)
criados. Framework nativo confirmado. Pendências de implementação:
- [ ] Android: fluxo de cadastro completo (spec 023)
- [ ] iOS: fluxo de cadastro completo (spec 023)
- [ ] Perfil e configurações mobile
- [ ] Suporte offline parcial

---

## 3. Inconsistências e Correções em Specs Existentes

### ✅ Spec 004 — FRs 001–037 Restaurados e Renumerados

**Problema original**: A spec 004 foi substituída pela v2.0 (018→004), e os
FRs originais 001–027 foram perdidos. FR-036/037 estavam fora de ordem.

**Resolução**:
- [x] FR-001 a 004 (database environments) — restaurados
- [x] FR-005 a 008 (schema & migrations) — restaurados
- [x] FR-009 a 014 (data integrity & constraints) — restaurados
- [x] FR-015 a 023 (security & compliance) — restaurados
- [x] FR-024 a 027 (containerization & CI/CD) — restaurados
- [x] FR-028 a 029 (Session & Cache — antigos FR-036/037)
- [x] FR-030 a 037 (Audit & Performance — antigos FR-028/035)
- [x] Numeração final: FR-001 a FR-037 sequencial ✓

### 🟡 Spec 002/003 — `feature_toggles` Duplicado

**Problema**: Entidade `feature_toggles` definida em spec 002 (FR-001) e spec 003
(entidades), sem referência cruzada.

**Ação**:
- [ ] Spec 002: definição canônica da tabela `feature_toggles`
- [ ] Spec 003: referenciar spec 002 em vez de redefinir

### 🟡 Spec 004 — Colunas com Espaços/Acentos

**Problema**: Tabelas `loterias_resultados_*` usam nomes de colunas com espaços e
acentos, exigindo quoting constante em SQL.

**Decisão pendente**: Manter fiel à planilha (com quoting) ou normalizar para
`snake_case`?

- [ ] Documentar decisão na spec 004
- [ ] Se normalizar, criar mapeamento planilha → coluna em cada collector

---

## 4. Funcionalidades Subespecificadas

### 🟡 Spec 003 — Georreferenciamento (FR-022)

**Problema**: FR-022 exige filtro por "região geográfica" no dashboard, mas
nenhum mecanismo de geolocalização é definido.

**Ação**:
- [ ] Criar tarefa de implementação para GeoIP (MaxMind ou similar)
- [ ] Definir tabela de fallback (região não identificada)
- [ ] Especificar middleware de captura de `ip_hash` + `regiao`

### 🟡 Redis para Sessões Anônimas

**Problema**: Constitution II determina Redis para sessões anônimas.
Nenhuma spec cobre a integração Redis + sessão.

**Ação**:
- [ ] Especificar integração Redis no plano de implementação
- [ ] Definir TTL de sessão anônima (default 30 dias conforme spec 001)
- [ ] Mapear entidades que usam `session_id` (promessas, usage_events)

---

## 5. Pendências Técnicas

### 🟡 Cobertura de Testes

- [ ] `combinacao_service.py` — 17% coverage
- [ ] `promessa_service.py` — 19% coverage
- [ ] `notification_service.py` — 32% coverage (core: email + WhatsApp)
- [ ] `share_service.py` — 0% coverage
- [ ] `routes.py` — aumentar cobertura de cenários de erro

### 🟡 Login Lockout em Produção

- [ ] Migrar de in-memory para Redis (CWE-307)
- [ ] Persistir tentativas entre restart do servidor

### 🟢 Ajustes no Plan

- [ ] Plan atual referencia specs 001–006 e 007–017 mas não menciona spec 004 v2
- [ ] Adicionar fase específica para specs 019 (Export), 020 (Web), 021 (Mobile)
- [ ] Detalhar stack frontend e mobile no Technical Context

---

## 6. Resumo

| Tipo | Quantidade |
|---|---|---|
| 🔴 Specs faltantes (CRITICAL) | 0 |
| 🔴 Inconsistências em specs existentes | 0 |
| 🟡 Melhorias em specs / APIs faltantes | 4 |
| 🟢 Ajustes no Plan | 1 |
| 🟡 Pendências técnicas (testes, Redis, cobertura) | 4 |
| ✅ Resolvidos nesta iteração | 25+ |

**Total de TODOs pendentes**: ~11 itens (pendências de implementação, testes, Redis)

---

### 🟡 Cobertura de testes — módulos que dependem de banco

Módulos como `auth.py`, `routes.py`, `combinacao_service.py`, `promessa_service.py`, `notification_service.py` e `share_service.py` dependem de conexão com PostgreSQL via SQLAlchemy async, que não está disponível no CI sem um banco de testes populado. Cobertura geral ficou em ~47%.

**Próximo passo:** Criar fixtures de banco em memória (SQLite via `aiosqlite`) ou usar `pytest-asyncio` com banco de testes dedicado no CI para aumentar cobertura desses módulos para ≥70%.
