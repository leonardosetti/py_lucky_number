# Test Plan — Lucky Number v0.1-beta

**Versão**: 1.0 | **Data**: 2026-05-14 | **Specs**: 001–021
**Cobertura alvo**: ≥90% (código) + 100% (cenários Gherkin para acceptance criteria)

---

## 1. Estratégia de Testes

### Pirâmide de Testes

```
            ╱╲
           ╱  ╲  E2E (Playwright) — 5% — fluxos críticos
          ╱    ╲
         ╱──────╲
        ╱        ╲  Integration (pytest + httpx) — 25% — API + DB + coletores
       ╱          ╲
      ╱────────────╲
     ╱              ╲  Unit (pytest) — 70% — services, models, utils
    ╱                ╲
   ╱──────────────────╲
```

### Níveis

| Nível | Ferramenta | Onde | Cobertura |
|---|---|---|---|
| **Unit** | pytest + pytest-asyncio | `tests/` | 70% — serviços, modelos, validação |
| **Integration** | pytest + httpx + asyncpg | `tests/` (DB fixtures) | 25% — API, coletores, banco |
| **E2E** | Playwright (web) / Detox (mobile) | `web/e2e/` / `mobile/` | 5% — fluxos críticos |
| **Manual** | Gherkin (`.feature`) | `tests/features/` | 100% acceptance criteria |

### Tipos de Teste

| Tipo | Descrição | Ferramenta |
|---|---|---|
| Unitários | Funções individuais, sem I/O | pytest |
| API (contrato) | Endpoints REST, status code + schema | pytest + httpx |
| Integração DB | Operações com PostgreSQL real | pytest + asyncpg |
| Coletores | Download + parse + insert (mock HTTP) | pytest + respx |
| Segurança | SQLi, XSS, CSRF, rate limit | pytest + OWASP ZAP |
| Performance | Hash lookup, dashboard, geração | pytest-benchmark + locust |
| Acessibilidade | WCAG 2.2 AA | axe-core + Lighthouse |
| E2E Web | Fluxos completos (login → gerar → salvar) | Playwright |
| E2E Mobile | Fluxos (login → gerar → offline) | Detox (RN) ou XCUITest/Espresso |
| Cobertura | Linhas + branches | pytest-cov (≥90%) |

### Gatilhos (CI/CD)

| Evento | Ações |
|---|---|
| **Pull Request** | `pytest tests/` + `pytest --cov --cov-fail-under=90` + `bandit -r src/` |
| **Merge → develop** | CI + deploy automático demo + Playwright E2E |
| **Merge → main** | CI + deploy produção (com gate) + OWASP ZAP scan |
| **Semanal** | `locust` (carga) + `pg_stat_statements` análise |

---

## 2. Mapa de Testes por Spec

| Spec | FRs | Testes Unit | Testes API | Testes E2E | Gherkin |
|---|---|---|---|---|---|
| 001 — Promises | 6 | `test_promises.py` | `test_api_promises.py` | E2E: Create/Share Promise | `001-promises.feature` |
| 002 — Feature Toggles | 10 | `test_features.py` | `test_api_features.py` | E2E: Admin Toggle | `002-features.feature` |
| 003 — System Management | 27 | `test_auth.py`, `test_roles.py` | `test_api_auth.py`, `test_api_admin.py` | E2E: CRUD User | `003-system.feature` |
| 004 — Database | 37 | `test_db_*.py` | `test_api_health.py` | — | `004-database.feature` |
| 005 — Backup | 25 | — | — | — | `005-backup.feature` |
| 006 — Environments | 24 | — | — | — | `006-env.feature` |
| 007–017 — Collectors | 30×10 | `test_collectors/test_*.py` | — | — | `007-megasena.feature` … `017-loteca.feature` |
| 019 — Export | 9 | `test_export.py` | `test_api_export.py` | E2E: Download CSV | `019-export.feature` |
| 020 — Web Frontend | 30 | — | — | Playwright: 6 user stories | `020-web.feature` |
| 021 — Mobile App | 27 | — | — | Detox: 5 user stories | `021-mobile.feature` |

---

## 3. Cenários de Teste por Spec (Gherkin)

### `001-promises.feature`
```gherkin
Feature: Promessas de Aposta
  Como um usuário do sistema
  Quero criar, gerenciar e compartilhar promessas de aposta
  Para planejar meus gastos com loterias

  Background:
    Given que o usuário "maria@email.com" está autenticado
    And que o usuário possui 3 combinações salvas

  Scenario: Criar promessa com título e prioridade
    Given que o usuário seleciona 2 combinações
    When ele clica em "Criar Promessa"
    And preenche o título "Aposta Final de Semana"
    And seleciona prioridade "Alta"
    Then o sistema persiste a promessa com snapshot das combinações
    And o valor total da promessa é calculado corretamente

  Scenario: FIFO ao atingir 50 promessas
    Given que o usuário possui 50 promessas salvas
    And a mais antiga não é favorita
    When ele cria uma nova promessa
    Then a promessa mais antiga não favorita é removida
    And o sistema exibe notificação "Limite de 50 promessas atingido"

  Scenario: Compartilhar promessa via WhatsApp
    Given que o usuário possui uma promessa salva
    When ele clica em "Compartilhar via WhatsApp"
    Then um link wa.me é gerado com as combinações em texto puro
    And o link expira em 7 dias

  Scenario: Excluir promessa com confirmação
    Given que o usuário possui uma promessa
    When ele clica em "Excluir"
    Then um diálogo de confirmação é exibido
    When ele confirma a exclusão
    Then a promessa é removida

  Scenario: Erro ao criar promessa sem combinações
    Given que o usuário não selecionou nenhuma combinação
    When ele tenta criar uma promessa
    Then o sistema exibe erro "Selecione ao menos uma combinação"

  Scenario: Rejeitar duplicata de promessa
    Given que o usuário já possui uma promessa com as mesmas combinações
    When ele tenta criar outra idêntica
    Then o sistema impede a criação com erro "Promessa duplicada"
```

### `002-features.feature`
```gherkin
Feature: Feature Toggles
  Como um administrador
  Quero ativar e desativar funcionalidades do sistema
  Para controlar a disponibilidade de features em produção

  Background:
    Given que o admin "admin@sistema.com" está autenticado com role Admin

  Scenario: Listar todas as features
    Given que existem features cadastradas
    When o admin acessa o painel de features
    Then a lista exibe slug, nome, descrição, status e data de criação
    And a lista contém pelo menos 4 features: "geracao-apostas", "promessas", "export", "admin"

  Scenario: Alternar status de feature
    Given que a feature "geracao-apostas" está ativa
    When o admin alterna o toggle para "inativa"
    Then o status da feature é alterado para "inativa"
    And o cache é invalidado
    And um registro é criado em feature_toggle_audit

  Scenario: Usuário não-admin não acessa painel
    Given que o usuário "maria@email.com" está autenticado com role Apostador
    When ele tenta acessar GET /api/v1/admin/features
    Then o sistema retorna 403 Forbidden

  Scenario: Feature desativada bloqueia acesso
    Given que a feature "geracao-apostas" está inativa
    When um usuário tenta acessar POST /api/v1/gerar-apostas
    Then o sistema retorna 404 com mensagem "Feature indisponível"

  Scenario: Toggle concorrente com optimistic locking
    Given que dois admins acessam a mesma feature simultaneamente
    When ambos tentam alterar o toggle
    Then apenas o primeiro commit é aceito
    And o segundo recebe erro de concorrência (version conflict)
```

### `003-system.feature`
```gherkin
Feature: System Management (Auth, Roles, Users)
  Como um administrador
  Quero gerenciar usuários, roles e permissões
  Para controlar acesso ao sistema

  Background:
    Given que existem 4 roles no sistema: Admin, Auditor, TestDemo, Apostador

  Scenario: Registrar novo usuário
    Given que um novo usuário acessa a página de registro
    When ele preenche email "novo@email.com" e senha "Str0ng!Pass"
    Then a conta é criada com role Apostador
    And a senha é armazenada como bcrypt hash (custo 12)

  Scenario: Login com credenciais válidas
    Given que o usuário "maria@email.com" possui conta
    When ele faz login com email e senha corretos
    Then um JWT é retornado
    And o token contém user_id e role

  Scenario: Login com senha inválida
    Given que o usuário "maria@email.com" possui conta
    When ele faz login com senha incorreta
    Then o sistema retorna 401 Unauthorized
    And o evento é registrado no audit_log

  Scenario: Bloquear exclusão do último admin
    Given que existe apenas 1 usuário com role Admin
    When uma tentativa de excluir este usuário é feita
    Then o sistema bloqueia com erro "Não é possível excluir o último administrador"

  Scenario: Bloquear auto-exclusão
    Given que o admin está autenticado
    When ele tenta excluir a própria conta
    Then o sistema bloqueia com erro "Você não pode excluir sua própria conta"

  Scenario: Auditor tem acesso somente leitura
    Given que o usuário "auditor@email.com" está autenticado com role Auditor
    When ele tenta criar um novo usuário via POST /api/v1/admin/users
    Then o sistema retorna 403 Forbidden

  Scenario: TestDemo com transaction rollback
    Given que o usuário "teste@email.com" está autenticado com role TestDemo
    When ele cria, edita ou exclui entidades
    Then as operações são executadas durante a sessão
    When a sessão termina (logout ou timeout 8h)
    Then todas as alterações são revertidas (transaction rollback)

  Scenario: Rate limiting em operações admin
    Given que um admin autenticado
    When ele faz 31 requisições em 1 minuto
    Then a 31ª requisição retorna 429 Too Many Requests

  Scenario: Exclusão de usuário com confirmação em 2 passos
    Given que o admin seleciona um usuário para excluir
    When ele clica em "Excluir"
    Then uma mensagem de confirmação é exibida: "Tem certeza?"
    When ele confirma o primeiro passo
    Then uma segunda confirmação é exibida: "Esta ação é irreversível"
    When ele confirma o segundo passo
    Then o usuário é marcado como inativo (soft delete)
    And o evento é registrado no audit_log
```

### `004-database.feature`
```gherkin
Feature: Database Architecture
  Como um desenvolvedor
  Quero garantir que o banco de dados funcione conforme especificado
  Para manter a integridade, performance e segurança dos dados

  Background:
    Given que o banco PostgreSQL está configurado com o schema da spec 004

  Scenario: 4 ambientes isolados
    Given que a variável DATABASE_URL aponta para o ambiente de desenvolvimento
    When a aplicação inicia
    Then ela conecta-se exclusivamente ao banco de desenvolvimento
    And operações de escrita não afetam produção ou testes

  Scenario: Migrations com rollback automático
    Given que uma migration com erro é aplicada
    When a migration falha (violação de constraint)
    Then o rollback é executado automaticamente
    And o erro é registrado em migrations_history

  Scenario: Unique hash em sorteios_historicos
    Given que existe um registro com hash "abc123" para Mega-Sena
    When uma tentativa de inserir outro registro com mesmo hash é feita
    Then o banco rejeita com erro de unique constraint

  Scenario: Soft delete de usuário
    Given que o usuário "maria@email.com" é marcado como inativo
    When o sistema consulta a listagem ativa de usuários
    Then "maria@email.com" não aparece nos resultados
    And o registro permanece no banco com deleted_at preenchido

  Scenario: Limite de 200 combinações por usuário
    Given que o usuário possui 200 combinações salvas
    When ele tenta salvar uma nova combinação
    Then a aplicação rejeita com erro "Limite de 200 combinações atingido"
    Or a mais antiga não favorita é removida para abrir espaço

  Scenario: BRIN index em usage_events
    Given que a tabela usage_events possui 1 milhão de registros
    When uma consulta por período é executada
    Then o BRIN index em created_at é utilizado (verificar via EXPLAIN)

  Scenario: pg_stat_statements coletando snapshots
    Given que o Celery Beat está configurado
    When o coletor de performance executa a cada 15 minutos
    Then um snapshot é inserido em database_performance_snapshots
```

### `005-backup.feature`
```gherkin
Feature: Backup Automation
  Como um administrador
  Quero garantir que backups do banco sejam executados e validados
  Para recuperar o sistema em caso de desastre

  Scenario: Backup completo programado
    Given que o scheduler está configurado para 03:00 UTC
    When o horário agendado é atingido
    Then pgBackRest executa backup full com criptografia AES-256-GCM
    And o backup é verificado (checksum SHA-256)
    And o resultado é registrado em backup_history

  Scenario: Restore com --force em produção
    Given que um arquivo de backup válido existe
    When o admin executa restore sem a flag --force
    Then o sistema bloqueia com erro "Use --force para restore em produção"
    When o admin executa com --force
    Then o restore é executado e validado

  Scenario: Falha no download com retry
    Given que a URL de download da CEF está fora do ar
    When o coletor de backup tenta baixar
    Then o sistema faz retry com backoff exponencial (até 3 tentativas)
    And após 3 falhas, uma notificação admin é criada

  Scenario: Lockfile impede execução concorrente
    Given que um backup está em execução
    When o scheduler tenta iniciar outro backup
    Then o sistema detecta o lockfile em /var/lock/backup.lock
    And registra "Backup já em execução" no log
```

### `006-env.feature`
```gherkin
Feature: Environment Management
  Como um desenvolvedor
  Quero ambientes isolados com branches específicas
  Para desenvolver sem afetar produção

  Scenario: Gitflow com branches protegidas
    Given que o repositório segue gitflow
    When um desenvolvedor cria feature/nova-funcionalidade a partir de develop
    Then a branch contém o código base + alterações da feature
    And não impacta develop ou main

  Scenario: Deploy em produção requer aprovação manual
    Given que um merge para main foi concluído
    When a pipeline de CD é acionada
    Then ela pausa e exige aprovação manual
    And executa rolling update com health check

  Scenario: Ambiente demo com dados sintéticos
    Given que o ambiente demo está configurado
    When um stakeholder acessa a URL
    Then o sistema está funcional com dados sintéticos
    And nenhum dado real de produção está presente
    And as alterações são efêmeras (reset diário)
```

### `007-megasena.feature`
```gherkin
Feature: Mega-Sena Data Collector
  Como o sistema
  Quero coletar sorteios da Mega-Sena da CEF
  Para manter a base histórica atualizada

  Background:
    Given que a URL da planilha é https://servicebus3.caixa.gov.br/.../Mega-Sena

  Scenario: Carga inicial na primeira execução
    Given que o arquivo ./data/megasena.json não existe
    When o coletor executa
    Then a planilha é baixada e parseada com Polars
    And o JSON é criado com todos os sorteios
    And a tabela loterias_resultados_megasena é populada

  Scenario: Atualização incremental sem novos concursos
    Given que o último concurso no JSON é 2800
    When o scheduler executa e a planilha contém até 2800
    Then nenhum novo registro é adicionado
    And o JSON e o banco não são alterados

  Scenario: Atualização incremental com novos concursos
    Given que o último concurso no JSON é 2800
    When o scheduler executa e a planilha contém até 2802
    Then apenas os concursos 2801 e 2802 são adicionados
    And o JSON é reescrito com os novos registros

  Scenario: Falha no download preserva dados existentes
    Given que a URL da CEF retorna HTTP 500
    When o coletor tenta baixar
    Then o erro é registrado no log
    And os dados anteriores permanecem intactos
    And o arquivo baixado é preservado em ./data/erros/ para diagnóstico

  Scenario: Verificação extra em dia de sorteio
    Given que hoje é terça-feira (dia de sorteio)
    When o relógio marca 22:00 BRT
    Then uma verificação extra é disparada
    (além da verificação periódica de 6h)
```

### `008-lotofacil.feature` ... `017-loteca.feature`
*(Mesma estrutura da 007, adaptada para as regras de cada jogo — dias de sorteio,
número de bolas, colunas específicas, URLs, etc.)*

### `019-export.feature`
```gherkin
Feature: Export & Share
  Como um usuário autenticado
  Quero exportar e compartilhar minhas combinações
  Para usar fora do sistema

  Background:
    Given que o usuário "maria@email.com" está autenticado
    And que o usuário possui 10 combinações salvas

  Scenario: Exportar CSV
    When o usuário acessa GET /api/v1/export/csv
    Then o response é um arquivo CSV baixável
    And contém apenas as combinações do próprio usuário
    And o CSV tem os cabeçalhos: jogo, dezenas, data

  Scenario: Exportar JSON
    When o usuário acessa GET /api/v1/export/json
    Then o response é um JSON array baixável
    And contém as 10 combinações do usuário

  Scenario: Exportar PDF
    When o usuário acessa GET /api/v1/export/pdf
    Then o response é um PDF baixável
    And o PDF contém as combinações formatadas

  Scenario: Compartilhar entre usuários
    Given que o usuário "joao@email.com" existe
    When o usuário compartilha uma combinação com joao@email.com
    Then joao@email.com recebe uma notificação com a combinação

  Scenario: Link expira após 7 dias
    Given que um link de compartilhamento foi gerado
    When 8 dias se passam
    Then o link não é mais válido
    And o acesso retorna 404

  Scenario: Usuário A não exporta dados do usuário B
    Given que "joao@email.com" está autenticado
    When ele tenta exportar as combinações de "maria@email.com"
    Then o sistema retorna apenas as combinações de joao

  Scenario: Sem combinações para exportar
    Given que o usuário não possui combinações salvas
    When ele tenta exportar CSV
    Then o sistema retorna CSV vazio (apenas cabeçalhos)
    Or retorna erro amigável "Nenhuma combinação para exportar"
```

### `020-web.feature`
```gherkin
Feature: Web Frontend
  Como um usuário do sistema
  Quero uma interface web responsiva e acessível
  Para interagir com o Lucky Number

  Background:
    Given que o frontend está servindo em http://localhost:3000

  Scenario: Registro de novo usuário
    When o usuário acessa a página de registro
    And preenche email "novo@email.com" e senha "Str0ng!Pass"
    And clica em "Criar Conta" [data-testid="register-submit-button"]
    Then o usuário é redirecionado para o dashboard
    And o email é exibido no perfil [data-testid="profile-email"]

  Scenario: Geração de apostas com fallback para funcionalidade não implementada
    Given que a API de geração retorna 503 (não implementada)
    When o usuário clica em "Gerar" [data-testid="generate-submit-button"]
    Then uma mensagem amigável é exibida:
    "Esta funcionalidade estará disponível em breve"
    And a UI não quebra (nenhum erro visível no console)

  Scenario: FIFO notification no histórico
    Given que o usuário possui 200 combinações salvas
    When ele gera e salva 5 novas combinações
    Then uma notificação é exibida:
    "Limite de 200 combinações atingido. As 5 mais antigas foram removidas."
    [data-testid="fifo-notification"]

  Scenario: Responsividade em viewport 375px (iPhone SE)
    Given que o viewport é 375x667
    When a página de geração carrega
    Then a navegação usa bottom tabs [data-testid="bottom-nav"]
    And todos os touch targets têm no mínimo 48x48px
    And o layout não tem overflow horizontal

  Scenario: data-testid em todos os elementos interativos
    Given que a página de login está renderizada
    Then o email input tem [data-testid="email-input"]
    And o password input tem [data-testid="password-input"]
    And o botão de submit tem [data-testid="login-submit-button"]
    And a mensagem de erro tem [data-testid="error-login"]

  Scenario: WCAG 2.2 AA sem violações
    Given que todas as páginas foram carregadas
    When o axe-core audit é executado
    Then zero violações WCAG 2.2 AA são reportadas

  Scenario: Session timeout redireciona para login
    Given que o JWT do usuário expirou
    When ele tenta acessar o dashboard
    Then ele é redirecionado para a página de login
    And um toast é exibido: "Sessão expirada. Faça login novamente."

  Scenario: Empty state no histórico
    Given que o usuário não possui combinações salvas
    When ele acessa a página de histórico
    Then uma mensagem é exibida:
    "Você ainda não gerou nenhuma combinação. Que tal começar?"
    [data-testid="empty-state-history"]
    And um CTA "Gerar Agora" está presente [data-testid="empty-state-cta"]
```

### `021-mobile.feature`
```gherkin
Feature: Mobile App
  Como um usuário mobile
  Quero usar o Lucky Number no celular com biometria e offline
  Para acessar minhas combinações em qualquer lugar

  Background:
    Given que o app está instalado no dispositivo

  Scenario: Login com biometria
    Given que o usuário já fez login uma vez e ativou biometria
    When ele abre o app
    Then o Face ID / fingerprint é solicitado
    When a biometria é bem-sucedida
    Then o usuário acessa o Home sem digitar credenciais

  Scenario: Geração offline bloqueada
    Given que o dispositivo está offline
    When o usuário tenta gerar combinações
    Then uma mensagem é exibida:
    "Geração requer conexão com a internet"
    And o botão "Gerar" permanece desabilitado

  Scenario: Histórico visível offline (cache)
    Given que o usuário possui combinações em cache local (SQLite)
    When o dispositivo está offline
    When ele acessa o histórico
    Then as combinações em cache são exibidas
    And um banner é mostrado: "Você está offline"

  Scenario: Swipe para excluir
    Given que o usuário está no histórico
    When ele desliza uma combinação para a esquerda
    Then um botão "Excluir" é revelado
    When ele toca em "Excluir"
    Then a combinação é removida

  Scenario: Push notification para novo sorteio
    Given que as permissões de push estão ativadas
    When um novo sorteio da Mega-Sena é publicado
    Then o usuário recebe uma notificação:
    "Mega-Sena: novo sorteio disponível!"
    When ele toca na notificação
    Then o app abre na tela de geração com Mega-Sena pré-selecionada

  Scenario: Deep link de promessa compartilhada
    Given que um link luckynumber://promise/abc123 foi gerado
    When o usuário toca no link
    Then o app abre na tela de detalhes da promessa
    And exibe as combinações do snapshot

  Scenario: Tema escuro segue configuração do sistema
    Given que o dispositivo está configurado com tema escuro
    When o app é aberto
    Then o tema escuro é aplicado automaticamente
    And todos os componentes respeitam as cores do tema

  Scenario: Fallback de biometria para senha
    Given que a biometria falhou 3 vezes consecutivas
    When o usuário tenta autenticar
    Then o sistema solicita a senha da conta
    And a biometria fica bloqueada para a sessão atual
```

---

## 4. Relatórios e Métricas

| Relatório | Frequência | Ferramenta |
|---|---|---|
| Cobertura de código | Por PR | pytest-cov + Codecov |
| Resultado dos cenários Gherkin | Por ciclo manual | Planilha ou Test Management |
| Performance (p95) | Semanal | Locust + Grafana |
| Acessibilidade | Semanal | Lighthouse CI |
| Segurança (OWASP) | Mensal | ZAP + Bandit + Safety |
| Testes manuais executados | Por release | Relatório assinado pelo QA |

---

## 5. Glossário

| Termo | Definição |
|---|---|
| **FIFO** | First In, First Out — política de remoção dos registros mais antigos |
| **Gherkin** | Linguagem BDD (Given-When-Then) para descrever cenários de teste |
| **WCAG** | Web Content Accessibility Guidelines |
| **data-testid** | Atributo HTML para localização de elementos em testes automatizados |
| **Soft delete** | Marcação de registro como inativo sem remoção física |
| **Snapshot** | Cópia dos dados no momento da criação (promessa) |
