# Lucky Number

Gerador de combinações de números aleatórios para loterias da Caixa que **nunca foram sorteadas anteriormente**.

## 🎯 Funcionalidade

O sistema busca todos os resultados históricos das loterias da Caixa via API pública e gera combinações aleatórias que ainda não foram sorteadas. Assim, você obtém números "da sorte" que têm a mesma probabilidade matemática de qualquer outra combinação, mas garantem que você não está repetindo uma aposta já feita.

## 🎰 Jogos Suportados

| Jogo | Números | Mínimo | Máximo |
|------|---------|--------|--------|
| Mega-Sena | 60 | 6 | 15 |
| Lotofácil | 25 | 15 | 20 |
| Quina | 80 | 6 | 15 |
| Dupla Sena | 50 | 6 | 15 |
| Federal | 100.000 | 1 | 5 |
| Dia de Sorte | 31 | 7 | 15 |

## 🚀 Como Executar

### Instalação

```bash
pip install -r requirements.txt
```

Ou instale as dependências diretamente:

```bash
pip install fastapi uvicorn pydantic httpx
```

### Execução

```bash
python -m lucky_number.main
```

Ou:

```bash
uvicorn lucky_number.main:app --reload
```

O servidor estará disponível em:
- **API**: http://localhost:8000/api/v1
- **Interface Web**: http://localhost:8000/
- **Docs Swagger**: http://localhost:8000/docs
- **Docs ReDoc**: http://localhost:8000/redoc

## 📡 API

### GET /api/v1/jogos-disponiveis

Lista todos os jogos disponíveis com suas regras.

```bash
curl http://localhost:8000/api/v1/jogos-disponiveis
```

### POST /api/v1/gerar-apostas

Gera combinações únicas nunca sorteadas.

```bash
curl -X POST http://localhost:8000/api/v1/gerar-apostas \
  -H "Content-Type: application/json" \
  -d '{
    "jogo": "megasena",
    "quantidade_apostas": 5,
    "dezenas_por_aposta": 6
  }'
```

### GET /api/v1/health

Health check.

```bash
curl http://localhost:8000/api/v1/health
```

## 🧪 Testes

```bash
pytest tests/ -v --cov=lucky_number --cov-report=term-missing
```

## ⚙️ Arquitetura

```
lucky_number/
├── config.py           # Configurações dos jogos
├── models.py           # Modelos Pydantic (contratos)
├── main.py             # App FastAPI
├── services/
│   ├── caixa_api.py    # Cliente API da Caixa
│   ├── cache.py        # Cache em memória
│   └── gerador.py      # Lógica de geração
├── api/
│   ├── routes.py       # Endpoints
│   └── dependencies.py
├── static/
│   └── index.html      # Interface web
└── tests/              # Testes unitários
```

## ⚠️ Aviso

Este projeto é apenas para fins educacionais. A API da Caixa não é oficial e pode deixar de funcionar a qualquer momento. Loterias são jogos de azar - não existe estratégia que garanta vitória.

## 📝 Licença

MIT
