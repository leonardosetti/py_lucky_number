<!-- 
Sync Impact Report
Version change: 1.4.0 -> 1.5.0
Modified principles: None
Added sections: Code Standards expandido: Bloco Code (CWE, Python, Go, TS, Mobile),
 Bloco UI/UX (Web: accessibility, data-testid, responsive, UX laws;
 Mobile: platform conventions, gestures, biometrics),
 Bloco Data (Web: API contracts, caching, DB; Mobile: offline, sync, encrypted storage)
Removed sections: None (anterior "Output Rules" absorvido pelos blocos)
Templates requiring updates: ✅ Nenhum (diretrizes prospectivas para specs 020/021)
-->
**Lucky Number**.

# Lucky Number Constitution

## Core Principles

### I. Data Integrity & Historical Accuracy
Toda combinação de números gerada pelo sistema **nunca deve ter sido sorteada**
em nenhum concurso oficial da Caixa Econômica Federal. O histórico completo de
sorteios deve ser carregado, validado e atualizado periodicamente via coletores
automáticos (specs 007–017). A verificação de combinações já sorteadas é feita
por consulta O(1) ao hash SHA-256 único em cada tabela
`loterias_resultados_{jogo}` (uma por modalidade). A geração de combinações
deve ser uniformemente aleatória dentro do espaço de combinações válidas e
não sorteadas. [SDD Context: Anexo – Regras das Loterias]

### II. User Privacy by Design
O sistema deve funcionar plenamente sem a necessidade de criação de conta (modo
anônimo). A conta é opcional e, quando criada, deve seguir a LGPD: coleta
mínima de dados (e-mail, nome opcional), direito ao esquecimento e
armazenamento seguro de credenciais (bcrypt + JWT). Dados de usuários anônimos
não são persistidos entre sessões.

### III. Controlled Random Generation & Limits
- Por ação, o usuário pode gerar de **1 a 10 combinações** por modalidade de jogo.
- Cada combinação gerada deve respeitar as regras da modalidade (quantidade de
  números, intervalo, trevos, etc.).
- O sistema deve validar os parâmetros antes de executar a geração.
- O espaço de busca para geração exclui combinações já sorteadas (consulta por
  hash SHA-256 em todas as tabelas `loterias_resultados_{jogo}`).
- O espaço de busca também exclui combinações já geradas pelo próprio usuário
  (consulta na tabela `combinacoes_salvas` do usuário).

### IV. User History + Favorites (combinacoes_salvas)
O sistema DEVE manter uma tabela `combinacoes_salvas` que armazena o histórico
das últimas combinações geradas pelo usuário, com as seguintes regras:

**Estrutura da tabela**:
- `id` UUID (PK), `user_id` UUID (FK → users), `jogo` VARCHAR,
  `dezenas` INTEGER[], `dezenas_por_aposta` INTEGER, `favorita` BOOLEAN,
  `hash_combinacao` VARCHAR(64) UNIQUE, `created_at` TIMESTAMPTZ.

**Isolamento por usuário**:
- Cada usuário tem acesso APENAS ao seu próprio histórico.
- Nenhuma combinação de um usuário pode ser visível para outro.
- A geração de novas combinações DEVE excluir do espaço de busca tanto
  as combinações já sorteadas (Princípio I) quanto as já existentes no
  histórico do usuário.

**Limite FIFO de 200 registros**:
- Máximo de 200 combinações armazenadas por usuário.
- Ao atingir 200 registros, o usuário DEVE ser notificado de que o limite
  foi atingido e que novas inserções removerão os registros mais antigos.
- Quando o usuário gera um novo lote de N combinações (ex.: 5), os N
  registros mais antigos da tabela (não-favoritados primeiro) são removidos
  para abrir espaço.
- Favoritos são imunes à exclusão automática (FIFO优先 remove não-favoritos).

**Exclusão manual**:
- O usuário pode selecionar e descartar quantos registros quiser,
  individualmente ou em lote.
- A exclusão manual pode ser feita por: seleção individual, por página,
  por tipo de jogo, por data, ou por condição numérica ("contém qualquer
  um" ou "contém todos" de uma lista).

**Favoritos**:
- Marcadores de favorito impedem exclusão automática (FIFO).
- Podem ser usados como filtro de consulta.

### V. Promises & Simulation ("Promessa de Aposta")
O usuário pode selecionar qualquer conjunto de combinações (geradas ou do
histórico) e solicitar a **simulação do valor total** das apostas, com base nas
regras de preço de cada modalidade (combinações). Esse conjunto pode ser salvo
como uma **Promessa de Aposta** (ou Desejo de Aposta), armazenada em tabela
separada, com campos: data, título opcional, prioridade (Alta/Média/Baixa),
valor total, e lista de combinações (snapshot ou referência). Promessas podem
ser favoritadas e excluídas manualmente.

### VI. Export & Share Without Lock-in
O sistema deve permitir a exportação de combinações (histórico ou resultado
atual) nos formatos **CSV, JSON, PDF** e também via mensagem de texto.
Compartilhamento deve incluir:
- **WhatsApp**: link `wa.me` com mensagem pré-formatada.
- **Entre usuários registrados**: envio direto por e-mail ou ID interno, com
  notificação ao destinatário.
- **Cópia simples para área de transferência**.

### VII. Cross-Platform App + UI/UX (Web, Mobile, Portabilidade)
O sistema DEVE ser implementado como **aplicação web-based** E **aplicativo
mobile nativo** (Android e iOS). As versões mínimas suportadas serão definidas
após benchmark e análise de mercado.

**Portabilidade**: O sistema NÃO DEVE impor restrições de uso com base em
navegador, sistema operacional desktop ou modelo de smartphone. A experiência
deve ser consistente em todos os ambientes suportados.

**UI/UX e Acessibilidade**:
- Design responsivo (mobile-first) funcional em desktop e dispositivos móveis.
- Seguir as melhores práticas de UI/UX e acessibilidade (WCAG 2.1 AA).
- Menu inferior adaptado para touch (mobile) e lateral (desktop).
- Paginação (ex.: 20 combinações por página).
- Suporte a gestos (swipe para excluir no mobile).
- Tema claro/escuro opcional.
- Feedback claro para ações (exclusão, limite atingido, erro de geração).
- Contraste mínimo, suporte a leitores de tela, navegação por teclado.

### VIII. Open Source & Licensing (FOSS)
Este é um projeto **Open Source**, regido pelas políticas das comunidades
FOSS/OSS. A licença adotada DEVE ser compatível com **GNU** e **MIT**.

**Regras obrigatórias**:
- Todo e qualquer componente do sistema (incluindo dependências) DEVE ser
  Open Source, preferencialmente apoiado em tecnologias e ferramentas
  igualmente Open Source.
- Nenhuma biblioteca proprietária ou com licença não-OSI pode ser utilizada.
- O código-fonte DEVE ser publicado em repositório público.
- Um **Termo de Aceite de Uso** (Terms of Service / EULA aberto) DEVE ser
  gerado como artefato obrigatório na fase final do projeto, definindo
  responsabilidades, limitações e conformidade legal para usuários finais.

## Game Rules Specification (SDD – Annex)

Todas as regras das loterias da CAIXA que o sistema deve obedecer estão
definidas abaixo, em formato SDD. Essas regras são parte integrante desta
Constituição.

### Mega-Sena

min_numbers: 6, max_numbers: 20, range: [1,60]
simple_bet_price: 6.00, draw_days: [ter, qui, sáb]
preço_aposta(k) = 6.00 * C(k,6) / C(6,6)
faixas: Sena(6), Quina(5), Quadra(4) – rateio

### Lotofácil

min:15, max:20, range:[1,25], price:3.50
preço = 3.50 * C(k,15) / 1
faixas: 15,14 (rateio); 13,12,11 (fixo)

### Quina

min:5, max:15, range:[1,80], price:3.00
faixas: 5,4,3,2 acertos – todas rateio

### Lotomania

fixed_numbers:50, range:[0,99], price:3.00
premiação: 20,19,...,15 acertos e 0 acertos (rateio)

### Dupla Sena

min:6, max:15, range:[1,50], price:3.00
dois sorteios por concurso, premiação independente por rateio (3 a 6 acertos)

### Dia de Sorte

min:7, max:15, range:[1,31] + mês(1-12), price:2.00
faixas: 7,6,5 (rateio); 4+mês, 4, mês (fixo)

### Super Sete

7 colunas, dígitos 0-9, min 1 marcam por coluna
price: 3.00 * (produto das marcações)
premiação: 3 acertos fixo; 4-7 rateio

### +Milionária

números: min6 max20 range[1,50]; trevos: min2 max6 range[1,6]
price: 6.00 * C(n,6)/1 * C(t,2)/1
faixas: 6+2 até 2+1 (rateio + fixo)

### Loteca

14 jogos, opções 1/2/3 por jogo, aposta mínima R$4,00
price = combinações (produto) * 1.00, mas deve ser >=4.00
premiação: 14 acertos (70%), 13 acertos (15%), 15% acumula

### Timemania

números: exatos 10, range[1,80]; time do coração (1 de 80)
price:3.50, sorteio:7 números + 1 time
premiação: 7 a 3 números (rateio); time (fixo)

**Nota**: Todas as fórmulas de preço e faixas de rateio devem ser
implementadas conforme regulamento oficial vigente.

## Technical Constraints

- **Backend**: Python + FastAPI (assíncrono), com endpoints RESTful.
- **Database**: PostgreSQL 16+ com SQLAlchemy 2.0 + Alembic.
  - `loterias_resultados_{jogo}` (10 tabelas): dados históricos completos da
    CEF, uma por jogo. Cada tabela possui `hash_combinacao` SHA-256 UNIQUE
    para consulta O(1) de combinações já sorteadas (Princípio I). NÃO existe
    tabela `sorteios_historicos` centralizada — cada jogo tem seus dados em
    sua própria tabela.
  - `combinacoes_salvas`: histórico FIFO das combinações geradas pelo usuário
    (máx. 200), com controle de favoritos e isolamento por usuário.
  - Demais tabelas: `users`, `roles`, `permissions`, `feature_toggles`,
    `promessas`, `system_notifications`, `audit_log`, etc.
  - Cache Redis para sessões anônimas e fila Celery.
- **Data Processing**: Polars (leitura de planilhas), orjson (serialização).
- **Scheduler**: Celery + Redis (Celery Beat) para coleta periódica de sorteios.
- **Frontend (Web)**: React + Next.js (SSR opcional) ou Vue.js com PWA.
- **Mobile**: Android (Kotlin/Compose ou React Native) e iOS (Swift/SwiftUI ou
  React Native) — definido após benchmark.
- **Segurança**: JWT (SECRET_KEY via env var, sem fallback hardcoded — CWE-522),
  bcrypt (custo 12), rate limiting (10 req/min por IP nas APIs de geração,
  5 tentativas/login por minuto, bloqueio de 15 min após 5 falhas — CWE-307),
  prepared statements (CWE-89), validação Pydantic (CWE-20), logs sanitizados
  (CWE-200), containers não-root (OWASP A05), CSRF token em toda mutação
  (CWE-352), senha forte obrigatória (mín. 8 chars, maiúscula, minúscula,
  número, especial — CWE-521), geração criptograficamente segura com
  `secrets.SystemRandom` em vez de `random` (CWE-338).
- **Atualização de dados**: 10 coletores automáticos com scheduler Celery Beat
  e verificação extra em janelas críticas.
- **Containerização**: Docker + Docker Compose (multi-profile), com volumes
  persistentes e rolling update em produção.
- **Backup**: Duas camadas complementares:
  - Físico: pgBackRest (WAL archiving, disaster recovery, restore completo)
  - Lógico: Ferramenta Go (pg_dump + gzip + AES-256-GCM + S3, exportação
    seletiva e população do mirror)
- **Licenciamento**: Todas as dependências DEVEM ser Open Source (OSI-approved).
  Nenhum componente proprietário é permitido.

## Development Workflow

- **Spec-Driven Development (SDD)** obrigatório: qualquer nova funcionalidade
  deve ter um arquivo de especificação em `specs/<id>-<nome>/spec.md`, derivado
  desta Constitution.
- **Test-First (não negocial)** para:
  - Geração de combinações não sorteadas.
  - Cálculo de preço de apostas.
  - Parse de planilhas CEF (Polars).
  - Regras de exclusão condicional.
- **Checklist de qualidade de requisitos** (`/speckit.checklist`) exigido antes
  da implementação de features críticas (geração múltipla, simulação de valor,
  coletores de dados, exclusão por condições).
- **Code review**: toda PR deve incluir verificação de conformidade com os
  princípios desta Constitution, especialmente licenciamento FOSS e segurança
  OWASP/CWE.
- **Branching**: `main` (produção), `develop` (integração), `feature/*`
  (funcionalidades), `hotfix/*` (correções urgentes), `release/*` (preparação
  de versão).

## Code Standards & Security Compliance

### Priority Order
1. **Security & CWE Compliance** — evitar CWE Top 25 (2024). Sem exceções.
2. **Testabilidade** — código testável isoladamente.
3. **Idiomas seguros da linguagem** — padrões modernos da linguagem (PEPs,
   TC39, SE, KEEP).
4. **Correção funcional** — respeitar spec/plan exatamente.
5. **Legibilidade e manutenibilidade** — nomes significativos, comentários
   apenas para lógica não óbvia ou segurança/testabilidade.

---

## Bloco 1 — Code

### CWE Top 25 (2024) — Obrigatório
Comentários no código DEVEM indicar qual CWE está sendo mitigada.

| CWE | Nome | Mitigação |
|-----|------|-----------|
| 89 | SQL Injection | asyncpg parameterized query. Proibida concatenação. |
| 79 | XSS | Output encoding. React: `{data}` escapa. API retorna JSON. |
| 352 | CSRF | Token anti-CSRF em mutações via API. |
| 20 | Input Validation | Pydantic/server-side + client-side apenas para UX. |
| 522 | Credential Protection | bcrypt custo 12. JWT em HttpOnly cookies. Env vars. |
| 918 | SSRF | Validar/allowlistar URLs de download (coletores CEF). |
| 502 | Deserialization | Pydantic/orjson. Nunca `pickle` ou `eval`. |
| 434 | File Upload | Validar extensão/MIME + ClamAV. |
| 22 | Path Traversal | Nunca usar input do usuário para paths. |
| 78 | OS Command Injection | Evitar `os.system()`. `subprocess` com lista. |
| 778/779 | Logging | Logs JSON sem secrets. Auditoria imutável. |
| 284 | Access Control | JWT + RBAC + RLS no PostgreSQL. |

Referência: https://cwe.mitre.org/top25/

### Python (Backend)
- PEP 8, line length ≤ 88. Black + isort + ruff.
- Type hints obrigatórios em funções públicas.
- Async/await para I/O (FastAPI, HTTPX, asyncpg).
- Secrets via env vars (pydantic-settings). Nunca hardcoded.
- Arquivos temporários: `tempfile` module (CWE-379).

### Go (Backup Tool)
- Static binary. Crypto via `crypto/aes` + `crypto/sha256`.
- Lockfile: `/var/lock/backup.lock` (0600). Volume Docker.
- Logs JSON sem secrets.

### JavaScript / TypeScript (Frontend Web)
- TC39 stage 2+ permitido se melhorar segurança/clareza.
- camelCase para variáveis. PascalCase para componentes.
- UPPER_SNAKE_CASE para constantes.
- Nunca `innerHTML` — usar `textContent` ou React `{data}` (CWE-79).
- fetch com timeout configurado. Erros 4xx/5xx tratados genericamente.

### Swift (iOS)
- SE (Swift Evolution) como referência.
- Keychain para tokens JWT. Nunca UserDefaults (CWE-522).
- URLSession com certificate pinning.
- Evitar CWE-200: não logar dados do usuário.
- Evitar CWE-732: entitlement mínimos.

### Kotlin (Android)
- KEEP (Kotlin Evolution) como referência.
- Coroutines + Retrofit + OkHttp.
- EncryptedSharedPreferences ou Android Keystore para tokens (CWE-522).
- ProGuard/R8 para ofuscar release.

### React Native (Cross-Platform)
- AsyncStorage criptografado para tokens (react-native-encrypted-storage).
- fetch nativo com SSL pinning.
- Código compartilhado evita platform-specific APIs.

### Output Rules
- Comentário obrigatório: `# Prevents CWE-NNN: motivo`.
- Front-end: `// data-testid for QA: nome-do-elemento`.
- Nunca gerar secrets — placeholders `${VAR_NAME}`.

---

## Bloco 2 — UI/UX

Estas diretrizes são prospectivas: DEVEM ser seguidas quando as specs de
frontend (020 Web, 021 Mobile) forem criadas.

### 2.1 Web Implementation

#### Priority Order
1. **Accessibility** — WCAG 2.2 AA mínimo.
2. **Testability & QA** — `data-testid` em todo elemento interativo.
3. **Security in UI** — OWASP + CWE.
4. **Retention & Engagement** — onboarding, métricas.
5. **Responsive & Cross-Browser** — mobile-first.
6. **Usability Heuristics** — Nielsen, Hick, Fitts.

#### Accessibility (WCAG 2.2 AA)
- ARIA labels em inputs e botões sem texto visível.
- Gerenciamento de foco em modais. Navegação por teclado.
- Contraste mínimo 4.5:1 (texto normal), 3:1 (texto grande).
- Suporte a leitores de tela: `role`, `aria-live`, `aria-describedby`.
- Gerar scripts de teste: axe-core, Lighthouse CI, pa11y.

#### Testability & QA (data-testid)
- Todo elemento interativo DEVE ter `data-testid` único e estável.
- Formato: `data-testid="{component}-{action}-{state}"`.
- Listas dinâmicas: `data-testid="{item-type}-{entity-id}-{action}"`
  (id estável, não índice de array).
- Loading: `data-testid="loading-spinner"` ou `"{component}-loading"`.
- Erro: `data-testid="error-{context}"` (ex: `error-login`).
- Inputs: `data-testid` igual ao nome do campo (`email-input`).
- Nunca depender de seletores auto-gerados (Vue `data-v-*`, React internal,
  Angular `_ngcontent-*`).
- Componentes stateless, sem mutáveis globais (suporta paralelismo).
- Testar com Playwright ou Cypress usando `data-testid` como seletor único.

#### Security in UI
- Nunca expor IDs de usuário reais em `data-testid` (usar tokens estáveis).
- CSRF token em toda mutação (CWE-352).
- Timeout de sessão configurável (CWE-613).
- Logout forçado após inatividade.

#### Responsive & Cross-Browser
- Mobile-first com `min-width` media queries.
- Breakpoints: 320px (mobile), 768px (tablet), 1024px (desktop),
  1440px (wide).
- Touch targets: mínimo 44x44pt (Apple) / 48x48px (Material).
- Viewports: iPhone SE (375x667), iPhone 12–14 (390x844), Pixel 5 (393x851),
  iPad (768x1024), Desktop 1280x720 e 1920x1080.
- Unidades relativas: `rem`, `em`, `vh`, `vw`, `%`, `clamp()`.
- CSS Grid, Flexbox, container queries. Proibido float/table.
- Navegadores: últimas 2 versões Chrome, Firefox, Safari, Edge. Sem IE11.

#### UX Laws & Heuristics
- Nielsen: visibilidade do sistema, consistência, prevenção de erros.
- Hick: reduzir opções por tela.
- Fitts: botões de ação primária maiores e próximos.
- Doherty Threshold: feedback <400ms.
- Von Restorff: destacar call to action.

### 2.2 Mobile Implementation

#### Platform Conventions
- iOS: Apple Human Interface Guidelines.
- Android: Material Design 3 (Material You).
- React Native: aderir à plataforma alvo automaticamente.

#### Touch & Gestures
- Touch targets: 48x48dp (Material), 44x44pt (iOS).
- Swipe para excluir (Constitution VII).
- Haptic feedback opcional para ações destrutivas.
- Evitar gestos que conflitem com navegação nativa (swipe back).

#### Navigation
- Bottom Tab Navigation (Constitution VII).
- Drawer lateral para tablets em landscape.
- Deep linking para compartilhamento (spec 001/019).

#### Biometrics & Security
- Face ID / Touch ID / fingerprint opcional para login.
- Keychain (iOS) / Keystore (Android) para tokens. Nunca SharedPreferences.
- Session timeout igual ao web (30 dias anônimo).

---

## Bloco 3 — Data

### 3.1 Web Implementation

#### API Contracts (REST)
- FastAPI + Pydantic v2 (CWE-20).
- Respostas JSON. Nunca HTML.
- Erro padronizado: `{ "detail": string, "status_code": int }`.

#### Caching
- Redis: feature flags (TTL 60s), sessões anônimas (TTL 30 dias).
- Browser: `Cache-Control: no-store` para dados sensíveis.
- Service Worker (PWA): cache offline de resultados estáticos.

#### Database Access
- asyncpg parameterized queries (CWE-89).
- SQLAlchemy 2.0 Core + Alembic.
- Row-level security (CWE-284).

### 3.2 Mobile Implementation

#### Offline Storage
- SQLite (WCDB/GRDB iOS, Room Android, expo-sqlite RN).
- Espelhar schema do backend apenas para leitura.
- Queue de operações offline com sincronização futura.

#### Sync Strategy
- Ao voltar online: FIFO para operações pendentes.
- Conflitos: last-write-wins para dados não críticos;
  resolução manual para promessas.
- Cache de resultados: invalidar a cada 6h.

#### Data Security (Mobile)
- SQLite criptografado (SQLCipher ou equivalente).
- Keychain (iOS) / EncryptedSharedPreferences (Android).
- Cache em memória zerado ao entrar em background (CWE-200).

## Governance

- Esta Constituição **prevalece sobre qualquer outra prática ou documentação**
  do projeto.
- Emendas requerem:
  - Documento de proposta de alteração.
  - Aprovação por pelo menos 2 mantenedores.
  - Plano de migração para código existente.
- A complexidade deve ser justificada no próprio código ou no spec
  correspondente.
- Para diretrizes de desenvolvimento em tempo real, utilize o arquivo
  `.specify/GUIDANCE.md` (se disponível).
- **Licensing Governance**: Qualquer dependência proposta DEVE ser verificada
  quanto à compatibilidade com licenças OSI antes da inclusão. Dependências com
  licenças proprietárias ou não-OSI SÃO PROIBIDAS.

## Project Ownership & Signatures

O projeto é de propriedade única e exclusiva do proprietário abaixo, que detém
todos os papéis de liderança (Arquiteto, PM, QA, DevOps, etc.).

- **Proprietário Único**: Leonardo Setti
- **E-mail**: vortex-devnull@protonmail.com

**Version**: 1.5.0
**Ratified**: 2026-05-06
**Last Amended**: 2026-05-14
