# 🍀 Lucky Number - Como Executar

## 🚀 Execução Rápida

### Opção 1: Usando o script auxiliar
```bash
# Rodar o servidor (porta 8000)
python run_server.py
```

### Opção 2: Comando direto
```bash
# Instalar dependências (se não tiver)
pip install fastapi uvicorn pydantic httpx

# Rodar o servidor
uvicorn lucky_number.main:app --host 127.0.0.1 --port 8000
```

## 🌐 Acessar a Aplicação

Após iniciar o servidor, acesse:
- **Interface Web:** http://localhost:8000/
- **Documentação API:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/v1/health
- **Jogos Disponíveis:** http://localhost:8000/api/v1/jogos-disponiveis

## 💻 Estrutura do Projeto

```
lucky_number/
├── run_server.py      # Script para rodar o servidor facilmente
├── pyproject.toml     # Configuração do pacote
├── README.md          # Documentação
├── src/               # Código fonte
│   └── lucky_number/  # Pacote principal
│       ├── main.py    # App principal
│       ├── config.py  # Configurações
│       ├── models.py  # Modelos Pydantic
│       ├── api/       # Rotas da API
│       └── services/  # Serviços (API da Caixa, cache, gerador)
├── static/            # Interface web
│   └── index.html
└── tests/             # Testes unitários
```

## 🧪 Rodar os Testes

```bash
# Rodar todos os testes
PYTHONPATH=src pytest tests/

# Rodar testes específicos
PYTHONPATH=src pytest tests/test_config.py
PYTHONPATH=src pytest tests/test_models.py
```

## 🎯 Funcionalidades

- **6 Jogos Suportados:** Mega-Sena, Lotofácil, Quina, Dupla Sena, Federal, Dia de Sorte
- **Geração Inteligente:** Combinações que NUNCA foram sorteadas
- **Interface Web Intuitiva:** Com seleção de jogos e configuração
- **API RESTful:** Com validação automática e documentação

## ⚠️ Observações

- A API da Caixa não é oficial e pode ficar indisponível
- Primeira execução pode ser lenta (busca histórico completo)
- Dados são armazenados em cache durante a sessão

## 🛠 Troubleshooting

Se tiver problemas:

1. **Instalar dependências:**
   ```bash
   pip install -e .
   ```

2. **Verificar imports:**
   ```bash
   python -c "from lucky_number import __version__; print(__version__)"
   ```

3. **Rodar com PYTHONPATH:**
   ```bash
   PYTHONPATH=src python -m lucky_number.main
   ```