# LinguistFlow AI: Plataforma Enterprise de Aprendizado Adaptativo

Plataforma de EdTech imersiva de alta escalabilidade voltada ao aprendizado adaptativo de idiomas. Combina orquestração dinâmica Multi-LLM, análise fonética e acústica assíncrona (Whisper + Librosa), mapas conceituais relacionais em grafos (Neo4j) e matrizes de fluência espaçadas (MongoDB Motor).

## 🏛️ 1. Arquitetura do Sistema e Fluxo Seguro

```
                                  +-------------------------------+
                                  |    Edge Client / Frontend     |
                                  |     (Streamlit / Web PWA)     |
                                  +---------------+---------------+
                                                  |
                                                  | HTTPS / TLS 1.3 (Magic Bytes + Auth)
                                                  v
+-------------------------------------------------------------------------------------------------+
|                                GATEWAY & API LAYER (FastAPI 0.115)                              |
|                                                                                                 |
|   - Strict CSP / HSTS / Permissions Headers       - Rate Limiting Distribuído (Redis/SlowAPI)   |
|   - Validação Mágica de Arquivos (Audio Sniffing) - RBAC & Context Token Validation             |
+------------------------------------------------┬------------------------------------------------+
                                                 │
                         ┌───────────────────────┴───────────────────────┐
                         │                                               │
                         v (Geração de Conteúdo)                         v (Áudio Streaming)
+------------------------------------------------+   +--------------------------------------------+
|            ORQUESTRAÇÃO MULTI-LLM              |   |          ISOLATED AUDIO PIPELINE           |
|                                                |   |                                            |
|   - Whitelist Rígida de Modelos (LiteLLM)      |   |   - Memory-Mapped Buffer & Duration Check  |
|   - Prompt Injection Semantic Guardrails       |   |   - Librosa ThreadPool (Pitch & Stress)    |
|   - Structured JSON Output via Pydantic v2     |   |   - OpenAI Whisper C++ / TensorRT Engine   |
+------------------------┬-----------------------+   +---------------------+----------------------+
                         │                                                 │
                         └───────────────────────┬─────────────────────────┘
                                                 │
                                                 v
+-------------------------------------------------------------------------------------------------+
|                                   DATA STORE & KNOWLEDGE FABRIC                                 |
|                                                                                                 |
|  +-------------------------------------------+  +--------------------------------------------+  |
|  |           Neo4j 5.x Async Graph           |  |           MongoDB Motor 3.6                |  |
|  |  - Parameterized Cypher Queries           |  |  - Heatmap Bulk Write Assíncrono           |  |
|  |  - Mapeamento Semântico de Vocabulário    |  |  - Histórico de Fluência & Repetição (SM2) |  |
|  +-------------------------------------------+  +--------------------------------------------+  |
+-------------------------------------------------------------------------------------------------+
```

## 📁 2. Estrutura Canônica de Diretórios

```
linguistflow-ai/
├── api/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # Entrypoint da aplicação e middlewares
│   │   ├── config.py                   # Pydantic BaseSettings com validações estritas
│   │   ├── deps.py                     # Dependency injection providers
│   │   ├── logging_config.py           # Logging estruturado structlog
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── guardrails.py           # Filtros anti-injection multilingues e detecção de jailbreak
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── mongo.py                # Motor assíncrono para bulk write e sanitização NoSQL
│   │   │   └── neo4j.py                # Consultas Cypher estritamente parametrizadas ($param)
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── registry.py             # Whitelist estrita de provedores e modelos
│   │   │   ├── router.py               # Roteamento seguro LiteLLM
│   │   │   ├── routes.py               # Endpoints REST para chat completions
│   │   │   └── schemas.py              # Schemas Pydantic para chat
│   │   ├── lessons/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py               # POST /api/v1/lessons e listagem de providers
│   │   │   ├── schemas.py              # Schemas Pydantic v2 para lições
│   │   │   └── service.py              # Montagem de prompts com guardrails semânticos
│   │   ├── speech/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py               # Análise acústica com validação binária de áudio
│   │   │   ├── schemas.py              # Schemas Pydantic para fonética e estresse
│   │   │   └── service.py              # Whisper STT + Librosa com limites de CPU/memória
│   │   └── security/
│   │       ├── __init__.py
│   │       ├── headers.py              # Headers defensivos (CSP, HSTS, Referrer, Permissions)
│   │       ├── rate_limit.py           # SlowAPI rate limiting por IP
│   │       └── errors.py               # Handlers sem vazamento de stacktrace
│   ├── Dockerfile                      # Multi-stage, non-root user com tini
│   ├── requirements.txt                # Dependências fixadas
│   ├── pyproject.toml                  # Configurações de linter e pytest
│   └── tests/                          # Suíte de testes automatizados
├── frontend/
│   ├── app.py                          # Streamlit modularizado integrado à API v1
│   ├── polyglot.html                   # Interface interativa polyglot
│   └── requirements.txt
├── docker-compose.yml                  # Cluster orquestrado com Neo4j, Mongo, API e Ollama
├── .env.example
└── README.md
```

## 🛡️ 3. Matriz de Segurança e Governança Técnica

| Vetor de Risco | Mitigação Implementada no LinguistFlow AI |
|---|---|
| Prompt Injection Semântico (OWASP LLM01) | Guardrail estruturado que valida intenções sem usar regex destrutivo que elimine acentuações e caracteres estrangeiros (UTF-8 completo preservado). |
| SSRF e Abuso de Modelos (OWASP LLM07) | Whitelist estrita no backend; a URL base (`api_base`) de provedores como Ollama é fixa no `.env`, impedindo que o cliente defina o host de destino. |
| Audio Bomb / Memory Exhaustion | Inspeção por Magic Bytes (evita binários executáveis disfarçados de áudio) + Limitação de duração a 30 s e teto de 10 MB com execução assíncrona (`asyncio.to_thread`). |
| Cypher / NoSQL Injection | Expressões totalmente parametrizadas (`$param`) no Neo4j e validação via ODM Pydantic antes de atingir o MongoDB Motor. |
| Vazamento de Dados em URLs (CWE-598) | Migração de parâmetros de lição de Query String (GET) para o corpo da requisição (POST `/api/v1/lessons`) criptografado via TLS. |

## 🚀 4. Endpoints da API

| Método | Rota | Descrição |
| --- | --- | --- |
| GET | `/healthz` | Verificação de integridade e liveness |
| GET | `/readyz` | Verificação de prontidão e providers ativos |
| GET | `/api/v1/lessons/providers` | Lista providers e modelos habilitados |
| POST | `/api/v1/lessons` | Criação segura de lição personalizada via payload JSON |
| POST | `/api/speech/analyze` | Análise de áudio acústico e fonético (multipart com magic bytes) |
| POST | `/api/llm/chat` | Roteamento direto de chat multi-LLM |

## 💻 5. Guia de Execução Local

```bash
cd linguistflow-ai/api
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd linguistflow-ai/frontend
pip install -r requirements.txt
streamlit run app.py
```

Docker Compose:
```bash
cp .env.example .env
docker compose up -d --build
# Modo com Ollama local:
docker compose --profile local-llm up -d --build
```
