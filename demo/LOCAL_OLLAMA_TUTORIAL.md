# Tutorial — Rodar LinguistFlow AI 100% Local com Ollama

Setup do zero, sem chave de API paga. Usa Ollama (LLM local) + Docker (Mongo, Neo4j, API, Frontend).

---

## 1. Pré-requisitos

| Item | Versão mínima | Observação |
| --- | --- | --- |
| Docker | 24+ | engine + plugin compose v2 |
| Docker Compose | v2 | `docker compose version` |
| RAM | 16 GB | modelos 7B (llama3.2). 8 GB serve com `phi3:mini` ou `qwen2.5:1.5b` |
| Disco | 15 GB livres | imagens + modelos baixados |
| GPU NVIDIA | opcional | `nvidia-container-toolkit` instalado para acelerar Whisper + Ollama |
| OS | Linux / macOS / WSL2 | |

**Sem GPU?** Edite `docker-compose.yml` e remova os blocos `deploy.resources.reservations.devices` dos serviços `api` e `ollama`. O Whisper e o Ollama caem para CPU (lento, mas funciona).

---

## 2. Clonar e configurar `.env`

```bash
git clone <repo> linguistflow-ai
cd linguistflow-ai
cp .env.example .env
```

Edite o `.env`:

```dotenv
# obrigatórios
MONGO_PASSWORD=troque-por-senha-forte
NEO4J_PASSWORD=troque-por-senha-forte

# perfil 100% local
LLM_DEFAULT_PROVIDER=ollama
LLM_OLLAMA_ENABLED=true

# desabilitar providers pagos
LLM_OPENAI_ENABLED=false
LLM_CLAUDE_ENABLED=false
LLM_GEMINI_ENABLED=false
LLM_OPENROUTER_ENABLED=false

# pode deixar todas as chaves de API em branco
```

---

## 3. Subir a stack (com profile `local-llm`)

```bash
docker compose --profile local-llm up -d --build
```

Containers iniciados:

- `linguist-mongo` (porta 27017)
- `linguist-neo4j` (porta 7474 / 7687)
- `linguist-ollama` (porta 11434)
- `linguist-api` (porta 8000) — FastAPI + Whisper + LiteLLM
- `linguist-frontend` (porta 8501) — Streamlit

---

## 4. Aguardar tudo saudável

```bash
docker compose ps
```

Espere ver `(healthy)` em todos os serviços. Pode levar 1–2 minutos no primeiro build (Whisper baixa o modelo `base` na inicialização da API).

Logs em tempo real:

```bash
docker compose logs -f api
# espere: "whisper.loaded" e "llm.ready"
```

---

## 5. Baixar um modelo no Ollama

```bash
docker exec linguist-ollama ollama pull llama3.2
```

Alternativas mais leves:

```bash
docker exec linguist-ollama ollama pull phi3:mini       # ~2 GB
docker exec linguist-ollama ollama pull qwen2.5:1.5b    # ~1 GB
```

Conferir:

```bash
curl -s http://localhost:11434/api/tags | jq
```

---

## 6. Validar via `curl`

Health + providers ativos:

```bash
curl -s http://localhost:8000/healthz
curl -s http://localhost:8000/readyz | jq
curl -s http://localhost:8000/api/lesson/providers | jq
```

Resposta esperada de `/api/lesson/providers`:

```json
{
  "defaultProvider": "ollama",
  "providers": {
    "ollama": ["llama3.2", "mistral", "qwen2.5", "phi3"]
  }
}
```

Gerar uma lição:

```bash
curl "http://localhost:8000/api/lesson?studentId=stu1&topic=viagem&hobby=futebol&provider=ollama&model=llama3.2"
```

> A primeira chamada pode demorar — Ollama carrega o modelo em memória.

Testar análise de áudio (gere um WAV de exemplo primeiro):

```bash
python3 -c "
import wave, struct
with wave.open('sample.wav','w') as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(16000)
    f.writeframes(struct.pack('<' + 'h'*16000, *([0]*16000)))
"
curl -X POST http://localhost:8000/api/speech/analyze \
    -F 'file=@sample.wav;type=audio/wav' \
    -F 'student_id=stu1' | jq
```

---

## 7. Usar via Streamlit

Abra http://localhost:8501.

Na barra lateral:
- **Provider:** `ollama`
- **Model:** `llama3.2` (ou outro que você fez `pull`)

Preencha Topic, Hobby, Student ID → **Generate Lesson**.

> Use o botão **Refresh providers** depois de habilitar um provider novo.

---

## 8. Rodar a demo completa

```bash
bash demo/demo.sh providers          # listar providers ativos
LESSON_PROVIDER=ollama LESSON_MODEL=llama3.2 \
    bash demo/demo.sh lesson         # geração de aula
bash demo/demo.sh ollama             # listar modelos baixados
bash demo/demo.sh all                # tudo em sequência
```

Apresentação:

```bash
# abrir no navegador
xdg-open demo/presentation.html      # Linux
open demo/presentation.html          # macOS
start demo/presentation.html         # Windows
```

Setas para navegar.

---

## 9. Adicionar providers pagos depois

Edite `.env`:

```dotenv
LLM_CLAUDE_ENABLED=true
ANTHROPIC_API_KEY=sk-ant-...
```

Recrie só a API (sem rebuild de imagem):

```bash
docker compose up -d --force-recreate api
```

No Streamlit, clique **Refresh providers** — o dropdown carrega o novo provider.

---

## 10. Troubleshooting

| Problema | Causa | Solução |
| --- | --- | --- |
| `nvidia-container-cli: device error` | Sem GPU ou toolkit | Remover bloco `deploy.resources.reservations.devices` no compose |
| `api` reinicia em loop | Mongo/Neo4j não saudável | `docker compose logs db-mongo` / `db-neo4j`; ver senha no `.env` |
| `429 rate limit exceeded` | Demo bate o limite | `RATE_LIMIT=100/minute` no `.env` e `docker compose up -d --force-recreate api` |
| `provider not enabled: openai` | Provider sem flag/chave | Confira `LLM_<X>_ENABLED=true` e a chave no `.env` |
| `model X not allowed` | Modelo fora da whitelist | Adicione em `LLM_<provider>_MODELS=...` no `.env` |
| `Could not connect to Ollama` | Ollama não subiu | Confira `docker compose --profile local-llm ps` |
| Resposta muito lenta | CPU only | Use modelo menor (`phi3:mini`, `qwen2.5:1.5b`) ou habilite GPU |
| `422 validation failed` | Input inválido | Veja o campo `fields[].loc` no JSON de erro |

---

## 11. Derrubar a stack

```bash
# manter dados (volumes Mongo, Neo4j, modelos Ollama)
docker compose --profile local-llm down

# apagar tudo
docker compose --profile local-llm down -v
```

---

## Resumo dos endpoints

| Método | Rota | Descrição |
| --- | --- | --- |
| GET | `/healthz` | Saúde básica |
| GET | `/readyz` | Saúde + providers ativos |
| GET | `/api/lesson/providers` | Lista providers e modelos disponíveis |
| GET | `/api/lesson?studentId=&topic=&hobby=&provider=&model=` | Gera lição adaptativa |
| POST | `/api/speech/analyze` (multipart `file`, `student_id`) | Transcreve + analisa pronúncia |
