# AGENTS.md

Este arquivo fornece instruções e contexto para agentes de IA que trabalham no projeto **LinguistFlow AI**.

## Visão Geral do Projeto
Plataforma de EdTech imersiva para aprendizado de idiomas, com tutor adaptativo, análise de fluência multimodal e grafo de conhecimento.

## Tecnologias Utilizadas
- **Backend:** Spring Boot 3, Spring AI, MongoDB, Neo4j (Grafo de Conhecimento).
- **AI Engine:** FastAPI, PyTorch, OpenAI Whisper (STT), Librosa (Análise de Fonemas).
- **Frontend:** Streamlit.
- **Infraestrutura:** Docker & NVIDIA GPU Acceleration.

## Estrutura de Pastas
- `backend/`: Orquestração educacional em Spring Boot.
- `ai-engine/`: Motor de processamento de áudio e ML em Python.
- `dashboard.py`: Frontend em Streamlit.

## Comandos Principais
- Build/Instalação: `pip install -r requirements.txt` (no ai-engine)
- Execução AI Engine: `uvicorn main:app --port 8002`
- Execução Backend: `./mvnw spring-boot:run`
- Docker: `docker-compose up --build`

## Diretrizes de Desenvolvimento
- **Adaptabilidade:** Gere lições dinâmicas baseadas no Grafo de Conhecimento e hobbies do aluno.
- **Privacidade:** Processamento de áudio efêmero ou anonimizado.
- **Performance:** Otimize transcrição com `faster-whisper` ou TensorRT.
- **Segurança:** Filtro de conteúdo para evitar lições inadequadas.
