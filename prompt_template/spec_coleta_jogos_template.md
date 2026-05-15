/speckit.specify

Com base nas informações a seguir, **escreva** a especificação técnica para coleta de sorteios da Caixa Econômica Federal (CEF), específica para o jogo **Loteca**.

**Nome do arquivo (padrão):** `./specs/017-loteca-data-collector/spec.md`

---

## 1. Fonte de dados

- **Link direto (planilha Excel):**  
  `https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Loteca`

- **Formato:** Planilha eletrônica com histórico completo, ordenado por número de concurso crescente.
- **Campos por linha:**

| Concurso | Data Sorteio | Coluna 1 | Coluna 2 | Coluna 3 | Coluna 4 | Coluna 5 | Coluna 6 | Coluna 7 | Ganhadores 7 acertos  | Cidade / UF | Rateio 7 acertos | Ganhadores 6 acertos | Rateio 6 acertos | Ganhadores 5 acertos | Rateio 5 acertos | Ganhadores 4 acertos | Rateio 4 acertos | Ganhadores 3 acertos | Rateio 3 acertos | Acumulado 7 acertos | Arrecadação Total | Estimativa Prêmio | Observação |

---

## 2. Comportamento esperado

### 2.1 Primeira execução (carga inicial)
- Baixar a planilha integralmente.
- Converter todos os sorteios para um array JSON (um objeto por sorteio).
- Salvar em `./data/loteca.json` (ou conforme variável de ambiente `DATA_PATH`).
- Inserir os mesmos dados na tabela `loterias_resultado_loteca` do banco de dados definido na spec 004-database-architecture (o esquema será adaptado posteriormente; por ora, usar os mesmos nomes de colunas dos campos JSON).

### 2.2 Atualizações periódicas
- **Intervalo fixo:** 6 horas (configurável via variável `UPDATE_INTERVAL_HOURS`).
- **Mecanismo:**
  1. Baixar novamente a planilha completa.
  2. Comparar o maior número de `Concurso` (ou data) já armazenado no JSON local com os valores da nova planilha.
  3. Se **não houver novos concursos** → descartar o download (não reescrever JSON/BD).
  4. Se **houver novos sorteios** (sempre no final da planilha, por ordenação crescente):
     - Adicionar **apenas os novos registros** ao array JSON existente (ler → acrescentar → reescrever o arquivo inteiro – não fazer append direto).
     - Inserir **apenas os novos registros** na tabela do banco de dados (operação incremental, sem recarregar histórico).
     - Registrar métricas de sucesso (quantidade de novos concursos, tempo de processamento).

### 2.3 Sorteios extraordinários (calendário conhecido)
- A Loteca concorre **Os concursos da Loteca são realizados semanalmente e os resultados divulgados no início de cada semana. Se algum jogo não for realizado no período programado, por motivo de antecipação, adiamento ou cancelamento, o resultado da partida (para fins do concurso da Loteca) será definido por sorteio.**.
- Embora o sistema já verifique a cada 6 horas, adicione uma **verificação extra  a cada 1:30 hora a partir das 20h dos Domingos até 23:00 das Segundas-feiras.** para minimizar atrasos de publicação.
- O projeto **não deve depender de horários oficiais exatos** (a CEF pode atrasar). A verificação extra é uma heurística, não uma garantia.

---

## 3. Stack técnica obrigatória (estritamente Open Source)

Utilize **exatamente** os componentes abaixo, sem adicionar tecnologias não solicitadas. O código deve ser auto-contido e seguir as boas práticas de cada ferramenta.

| Camada                     | Componente                           | Versão / Observação                                                  |
|----------------------------|--------------------------------------|----------------------------------------------------------------------|
| API (REST)                 | FastAPI                              | Assíncrono, com Pydantic v2                                          |
| Cliente HTTP assíncrono    | HTTPX                                | Suporte a streaming e timeouts                                       |
| Processamento de dados     | Polars                               | Leitura da planilha Excel (lazy se possível)                         |
| Banco de dados             | PostgreSQL 15+                       | Tabela separada para cada jogo                                       |
| Driver BD assíncrono       | asyncpg                              | Uso de `copy_from` para bulk insert                                  |
| Serialização JSON          | orjson                               | Para leitura/escrita do arquivo `.json`                              |
| Agendamento de tarefas     | Celery + Redis (broker)              | Utilizar Celery Beat para periodicidade                              |
| Containerização            | Docker (Moby)                        | Com `docker-compose` para desenvolvimento                            |
| Orquestração (opcional)    | Kubernetes                           | Apenas se explicitamente demandado                                   |
| Monitoramento              | Prometheus + Grafana (OSS)           | Exportar métricas: `download_duration_seconds`, `new_contests_count` |
| Logs centralizados         | Loki + Promtail                      | Estruturados em JSON                                                 |
| Rastreamento de erros      | GlitchTip (ou Sentry On‑Premise)     | Configurar captura de exceções                                       |
| Rate limiting              | slowapi + Redis                      | Aplicar na API (se houver endpoint manual)                           |
| Autenticação               | python-jose (JWT) + OAuth2 (FastAPI) | Para endpoints protegidos (opcional)                                 |
| Segurança de arquivos      | ClamAV                               | Escaneamento opcional (recomendado em produção)                      |


**Proibido:** Pandas, requests síncrono, sqlite3, arquitetura puramente síncrona, bibliotecas proprietárias ou com licenças não‑OSI.

---

## 4. Requisitos de segurança (OWASP / CWE)

A especificação **deve** incorporar as seguintes recomendações (nenhuma é opcional):

| ID (OWASP/CWE)                                        | Prática                                                                            | Implementação na stack                                     |
|-------------------------------------------------------|------------------------------------------------------------------------------------|------------------------------------------------------------|
| **CWE-89** (SQL Injection)                            | Uso obrigatório de prepared statements / consultas parametrizadas                  | `asyncpg` já utiliza; não permitir concatenação de strings |
| **CWE-20** (Improper Input Validation)                | Validar todos os campos da planilha antes de inserir no BD                         | Modelos Pydantic para cada sorteio                         |
| **CWE-200** (Exposure of Sensitive Info)              | Logs não devem conter dados dos sorteios (apenas metadados como concurso, data)    | Configurar níveis de log e sanitização                     |
| **OWASP A05:2021** (Security Misconfiguration)        | Containers rodam com usuário não‑root; remover serviços desnecessários             | Dockerfile com `USER appuser`                              |
| **OWASP A07:2021** (Identification and Auth Failures) | Endpoints administrativos exigem autenticação JWT                                  | FastAPI com dependência `Depends(get_current_user)`        |
| **CWE-400** (Uncontrolled Resource Consumption)       | Timeouts no download (HTTPX: timeout total 30s) e limites de memória por container | Configurar `limits.memory` no Docker                       |
| **CWE-73** (External Control of File Name)            | Nunca usar dados da planilha para nomear arquivos internos; usar sequência fixa    | Nome do JSON fixo (`loteca.json`)                  |
| **CWE-434** (Unrestricted Upload)                     | Se a API aceitar uploads, validar extensão/MIME e escanear com ClamAV              | (Não aplicável ao download, mas manter ClamAV como camada) |

---

## 5. Coexistência com múltiplos jogos (padrão reutilizável)

O sistema deve ser projetado para permitir a adição futura de outros jogos (Mega‑Sena, loteca, etc.) **sem duplicação de código** e **sem interferência entre as tarefas**.

### 5.1 Estratégia de isolamento

- **Tabelas separadas no PostgreSQL**  
  Padrão: `loterias_resultados_<jogo>` (ex.: `loterias_resultados_lotofacil`, `loterias_resultados_loteca`).

- **Arquivos JSON separados**  
  `./data/<jogo>.json` (ex.: `./data/duplasena.json`, `./data/lotofacil.json`, `./data/loteca.json`).

- **Tarefas Celery distintas**  
  Cada jogo terá sua própria tarefa periódica (ex.: `celery_beat_schedule` com entradas para `collect_duplasena`, `collect_lotofacil`, `collect_loteca`, etc.).  
  As tarefas **não compartilham estado** além do broker Redis.

- **Variáveis de ambiente por jogo**  
  ```env
  LOTO_FACIL_URL=https://...
  LOTO_FACIL_TABLE=loterias_resultados_loteca
  LOTO_FACIL_JSON_PATH=./data/loteca.json
  MEGA_SENA_URL=...
  ```

### 5.2 Código reutilizável (base class)

Criar uma classe abstrata `BaseLotteryCollector` (em Python) que implemente:

- `download_excel()`
- `parse_to_dataframe()`
- `get_last_contest_from_json()`
- `filter_new_contests()`
- `append_to_json()`
- `bulk_insert_to_db()`

Cada jogo específico (ex.:`LotecaCollector`) herda e configura apenas URL, nomes de colunas, tabela e arquivo JSON.  
**Não é permitido** gerar collectors individuais com lógica duplicada.

---

## 6. Estrutura de arquivos esperada (projeto)

```
.
├── docker-compose.yml
├── .env.example
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py          # endpoints: GET /health, POST /collect/manual
│   │   └── dependencies.py    # auth, rate limiting
│   ├── collectors/
│   │   ├── base.py            # BaseLotteryCollector
│   │   ├── loteca.py       # LotecaCollector
│   │   └── (futuros: duplasena.py, megasena.py)
│   ├── models/
│   │   ├── schemas.py         # Pydantic models para validação
│   │   └── database.py        # asyncpg conexão, queries
│   ├── tasks/
│   │   ├── celery_app.py
│   │   └── periodic.py        # tarefas agendadas (Celery Beat)
│   ├── utils/
│   │   ├── logging_config.py
│   │   ├── metrics.py         # Prometheus
│   │   └── security.py        # sanitização, validação
│   └── main.py                # FastAPI app
├── data/                      # montado como volume
│   └── loteca.json
├── tests/
│   ├── test_collector.py
│   └── test_api.py
└── requirements.txt
```

---

## 7. Tratamento de erros (obrigatório)

- **Falha no download:** log de erro (`ERROR`) → abortar atualização → não modificar JSON/BD → enviar alerta ao GlitchTip.
- **Falha na leitura da planilha (Polars):** log de erro com detalhes → abortar → manter dados anteriores.
- **Falha na escrita do JSON:** reverter para backup do arquivo anterior (se existir) → log crítico.
- **Falha na inserção no BD:** fazer rollback da transação → log de erro → não confirmar alterações.
- **Timeout no download:** configurar `httpx.Timeout(connect=5.0, read=30.0, write=5.0, pool=5.0)` → tentar novamente até 3 vezes com backoff exponencial (Celery retry).

---

## 8. Métricas e logs (para observabilidade)

### 8.1 Métricas Prometheus (expostas no endpoint `/metrics`)
- `lottery_download_duration_seconds{game"loteca"}`
- `lottery_new_contests_total{game"loteca"}`
- `lottery_last_success_timestamp{game"loteca"}`
- `lottery_errors_total{game"loteca", type="download|parse|db|json"}`

### 8.2 Logs estruturados (formato JSON)
- Cada log deve conter: `timestamp`, `level`, `game`, `contest` (se aplicável), `message`, `trace_id` (correlação).
- Exemplo: `{"level":"INFO","game":"loteca","message":"New contests found","count":3,"timestamp":"2025-..."}`

---

## 9. Instruções anti‑alucinação (para os agentes de IA)

- **Não sugerir** bibliotecas não listadas na stack (ex.: Pandas, SQLAlchemy, Gunicorn sem necessidade, Flask, Django).
- **Não adicionar** camadas de cache além do Redis já especificado.
- **Não propor** arquitetura serverless (AWS Lambda, Google Cloud Functions) a menos que o usuário peça explicitamente.
- **Não modificar** o intervalo de atualização para valores diferentes de 6 horas (a menos que configurável).
- **Não criar** estruturas de tabela que misturem múltiplos jogos em uma única tabela (viola o princípio de coexistência).
- **Não usar** `pandas` para leitura do Excel – use **Polars** (`pl.read_excel()`).
- **Não usar** `json` padrão do Python para leitura/escrita – use **orjson**.

---

## 10. Validação final (checklist)

Antes de entregar a especificação, verifique se:

- [ ] O arquivo está salvo como `./specs/017-loteca-data-collector/spec.md`
- [ ] Todos os componentes da stack OSS estão presentes (nenhum ausente, nenhum extra)
- [ ] As recomendações CWE/OWASP estão explicitamente mapeadas para ações de implementação
- [ ] Há uma seção clara sobre coexistência com outros jogos (base class, tabelas separadas, variáveis de ambiente)
- [ ] O tratamento de erros cobre download, parsing JSON e BD
- [ ] Métricas e logs seguem o padrão definido
- [ ] O documento não contém linguagem ambígua ou “futuro opcional” não solicitado

## Informação adicional:

### Calendário de sorteios

**Loteca**
> Os concursos da Loteca são realizados semanalmente e os resultados divulgados no início de cada semana. Se algum jogo não for realizado no período programado, por motivo de antecipação, adiamento ou cancelamento, o resultado da partida (para fins do concurso da Loteca) será definido por sorteio.

**Mega Sena**
> Terças, quintas e sábados, a partir das 21 horas.

**Loto Fácil**
> Segundas, terças, quartas, quintas, sextas e sábados, a partir das 21 horas.

**Dia de Sorte**
> Terças, quintas e sábados, a partir das 21 horas.

**Dupla Sena**
> Segundas, quartas e sextas-feiras, a partir das 21 horas.

**Quina**
> Segundas, terças, quartas, quintas, sextas e sábados, a partir das 21 horas.

**Loteria Federal**
> Quartas e sábados, a partir das 20 horas.

**Lotomania**
> Segundas, quartas e sextas, a partir das 21 horas.

**Timemania**
> Terças, quintas e sábados, a partir das 21 horas.

**Mais Milionária**
> Quartas e sábados, a partir das 21 horas.

**Super Sete**
> Segundas, quartas e sextas, a partir das 21 horas.


### URLs das planilhas de jogos:

[**Loteca**](https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Loteca)

[**Mega-sena**](https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Mega-Sena)

[**Loto Fácil**](https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Lotof%C3%A1cil)

[**Dia de Sorte**](https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Dia-De-Sorte)

[**Dupla-sena**](https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Dupla-Sena)

[**Quina**](https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Quina)

[**Loteria Federal**](https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=federal)

[**Lotomania**](https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=lotomania)

[**Timemania**](https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Timemania)

[**Mais Milionária**](https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Mais-Milionaria)

[**Super-Sete**](https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Super-Sete)

[**Últimos resultados (todos os jogos e sorteios)**](https://servicebus3.caixa.gov.br/portaldeloterias/api/home/ultimos-resultados)