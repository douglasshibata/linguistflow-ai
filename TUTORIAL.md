# 📘 Tutorial de Operação e Instalação: LinguistFlow AI

Guia passo a passo para configuração, inicialização, execução de testes e resolução de problemas no projeto **LinguistFlow AI** (`linguistflow-ai`).

---

## 🛠️ 1. Visão Geral e Arquitetura

O **LinguistFlow AI** é um ecossistema educacional de alta escalabilidade voltado ao aprendizado adaptativo de idiomas. Combina orquestração dinâmica Multi-LLM, análise fonética e acústica assíncrona (Whisper + Librosa), mapas conceituais relacionais em grafos (Neo4j) e matrizes de fluência espaçadas (MongoDB Motor).

- **Tecnologias Principais:** Python 3.12, FastAPI 0.115, Pydantic v2, LiteLLM, Librosa, Whisper, Motor, Neo4j
- **Diretório do Módulo:** `linguistflow-ai`

---

## 📋 2. Pré-requisitos do Sistema

- **Python 3.12+**
- **Docker Engine & Docker Compose**
- **NVIDIA Container Toolkit** (opcional para aceleração por GPU)

---

## 🚀 3. Passo a Passo de Setup e Instalação

### Passo 1: Acessar a Pasta da API
```bash
cd linguistflow-ai/api
```

### Passo 2: Instalação de Dependências
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### Subindo Infraestrutura via Docker Compose
No diretório `linguistflow-ai`:

```bash
# Iniciar serviços em background
docker compose up -d --build

# Iniciar modo híbrido com Ollama local
docker compose --profile local-llm up -d --build
```

---

## ⚙️ 4. Configuração do Ambiente

Configure o arquivo de variáveis de ambiente (`.env`) localizado no diretório raiz de `linguistflow-ai`:

```ini
APP_ENV=development
LOG_LEVEL=INFO

MONGO_URI=mongodb://root:Secr3tMongoPass@db-mongo:27017/?authSource=admin
MONGO_DATABASE=linguistflow

NEO4J_URI=bolt://db-neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=Secr3tNeo4jPass

LLM_DEFAULT_PROVIDER=ollama
LLM_OLLAMA_ENABLED=true
LLM_OLLAMA_BASE_URL=http://ollama:11434
LLM_OLLAMA_MODELS=llama3.2,mistral
```

---

## 💻 5. Guia de Execução

### Inicializando a API FastAPI
Dentro de `linguistflow-ai/api`:
```bash
uvicorn app.main:app --reload --port 8000
```

### Inicializando o Frontend Streamlit
Dentro de `linguistflow-ai/frontend`:
```bash
streamlit run app.py --server.port 8501
```

---

## 🧪 6. Testes e Validação

Para validar o funcionamento da API e garantir que não há regressões de segurança:

```bash
cd linguistflow-ai/api
python3 -m pytest tests/ -v
```

---

## 🔍 7. Troubleshooting e Resolução de Problemas

1. **Porta em uso ou Conflito de Rede:**
   - Cancele processos pendentes na porta 8000/8501 ou utilize `docker compose down` e suba novamente.
2. **Formato de Áudio Inválido (HTTP 415):**
   - O sistema valida Magic Bytes no cabeçalho binário. Verifique se o arquivo é um WAV, MP3, OGG ou FLAC autêntico.
3. **Bloqueio por Guardrails de Prompt (HTTP 403):**
   - Textos contendo instruções de jailbreak (`ignore previous instructions`, `system prompt override`) são rejeitados preventivamente.
