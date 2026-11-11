# LinguistFlow AI - CLAUDE.md (v2.1)

Guia operacional para engenharia e desenvolvimento no LinguistFlow AI.

## Build e Execução

### API (FastAPI + LiteLLM + Whisper + Librosa)

```bash
cd linguistflow-ai/api
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend (Streamlit)

```bash
cd linguistflow-ai/frontend
pip install -r requirements.txt
streamlit run app.py
```

### Docker (Stack Completa)

```bash
cp .env.example .env
docker compose up -d --build
```

### Ollama Opcional (LLM Local)

```bash
docker compose --profile local-llm up -d
docker exec linguist-ollama ollama pull llama3.2
```

## Endpoints

| Método | Rota | Descrição |
| --- | --- | --- |
| GET | `/healthz` | Liveness |
| GET | `/readyz` | Readiness + providers ativos |
| GET | `/api/v1/lessons/providers` | Lista providers habilitados e modelos |
| POST | `/api/v1/lessons` | Gera lição personalizada via POST JSON |
| POST | `/api/speech/analyze` | Multipart file + student_id com validação Magic Bytes |
| POST | `/api/llm/chat` | Roteamento unificado multi-LLM |

## Segurança e Blindagem

- **Proteção contra Vazamento de URL (CWE-598):** Endpoint canônico `POST /api/v1/lessons` substitui passagem sensível de parâmetros via GET query strings.
- **Guardrails Semânticos Multilíngues:** Normalização Unicode NFKC preservando diacríticos, acentos e alfabetos internacionais enquanto neutraliza jailbreaks estruturais.
- **Inspeção de Áudio e DoS Mitigation:** Validação de Magic Bytes (`python-magic`), teto estrito de 10 MB e 30 s de duração, execução assíncrona em worker pool com `asyncio.to_thread`.
- **Proteção contra Injeção de Banco:** Cypher parametrizado (`$param`) no Neo4j e filtros NoSQL higienizados no MongoDB Motor.
- **Whitelist Restrita de LLM:** Validação de modelos por provedor; `api_base` restrita e estática no backend.
