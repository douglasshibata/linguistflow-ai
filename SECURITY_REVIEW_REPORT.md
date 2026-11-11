# Security Review, Atualização de Versões e Otimizações — LinguistFlow AI

**Data:** 2026-03-11
**Projeto:** LinguistFlow AI — Plataforma de Tutoria Adaptativa de Idiomas
**Escopo:** AI Engine (FastAPI), Backend (Spring Boot), Frontend (Streamlit), Docker Infrastructure

---

## 1. Security Review

### 1.1 Vulnerabilidades CRÍTICAS

| Severidade | Issue | Arquivo | Linha | Descrição |
|:----------:|-------|---------|:-----:|-----------|
| 🔴 CRÍTICA | Credenciais hardcoded Neo4j | `docker-compose.yml` | 19, 49 | Senha `password123` exposta diretamente no arquivo de configuração versionado. Qualquer pessoa com acesso ao repositório tem acesso total ao banco Neo4j. |
| 🔴 CRÍTICA | API Key OpenAI com fallback inseguro | `docker-compose.yml` | 51 | `${OPENAI_API_KEY:-your_api_key_here}` usa fallback que pode ser interpretado como chave válida; sem validação de presença obrigatória. |
| 🔴 CRÍTICA | Zero autenticação nos endpoints REST | `LessonController.java` | 17-23 | Endpoint `/api/lesson` exposto publicamente sem qualquer mecanismo de autenticação ou autorização. |
| 🔴 CRÍTICA | Zero autenticação no endpoint FastAPI | `ai-engine/main.py` | 21-25 | Endpoint `/analyze-speech` aceita requisições de qualquer origem sem autenticação. |
| 🔴 CRÍTICA | MongoDB sem autenticação | `docker-compose.yml` | 4-10 | Container MongoDB exposto na porta 27017 sem credenciais configuradas. Qualquer serviço na rede pode acessar todos os dados. |

**Impacto:** Acesso não autorizado a dados de estudantes, manipulação de lições, uso indevido de API keys, exfiltração completa de dados.

### 1.2 Vulnerabilidades ALTAS

| Severidade | Issue | Arquivo | Linha | Descrição |
|:----------:|-------|---------|:-----:|-----------|
| 🟠 ALTA | Sem validação de input nos parâmetros | `LessonController.java` | 18-21 | Parâmetros `studentId`, `topic`, `hobby` aceitos sem qualquer validação de tamanho, formato ou caracteres permitidos. |
| 🟠 ALTA | Prompt injection via topic/hobby no LLM | `SyllabusService.java` | 22-28 | Valores de `topic` e `hobby` são interpolados diretamente no prompt do LLM sem sanitização. Um atacante pode injetar instruções maliciosas. |
| 🟠 ALTA | Bare `except:` silencia erros de segurança | `frontend/app.py` | 34, 58 | Exceções genéricas capturam e silenciam todos os erros, incluindo erros de autenticação, timeout e falhas de rede, impedindo detecção de incidentes. |
| 🟠 ALTA | Sem CORS configuration | Backend (ausente) | — | Nenhuma política CORS configurada. Em modo permissivo do Spring Boot, qualquer domínio pode fazer requisições ao backend. |
| 🟠 ALTA | Sem security headers (CSP, X-Frame, HSTS) | Backend (ausente) | — | Headers de segurança HTTP ausentes, vulnerável a clickjacking, XSS refletido e man-in-the-middle. |
| 🟠 ALTA | Comunicação HTTP sem TLS entre serviços | `docker-compose.yml` | 50, 62 | Toda comunicação inter-serviços usa HTTP plaintext. Dados sensíveis (áudio, textos, IDs) trafegam sem criptografia. |
| 🟠 ALTA | `student_id` hardcoded no frontend | `frontend/app.py` | 49 | Valor `"STU123"` hardcoded na chamada de análise de pronúncia, ignorando o input do usuário e misturando dados entre estudantes. |

### 1.3 Vulnerabilidades MÉDIAS

| Severidade | Issue | Arquivo | Linha | Descrição |
|:----------:|-------|---------|:-----:|-----------|
| 🟡 MÉDIA | `delete=False` em temp files sem cleanup garantido | `ai-engine/main.py` | 27 | Embora haja `finally` block, o uso de `delete=False` cria risco de acúmulo de arquivos temporários em caso de crash. |
| 🟡 MÉDIA | Sem limite de tamanho no upload de áudio | `ai-engine/main.py` | 22-25 | Nenhum limite configurado para tamanho de arquivo. Um atacante pode enviar arquivos enormes causando DoS por exaustão de memória/disco. |
| 🟡 MÉDIA | Docker images com tag `:latest` | `docker-compose.yml` | 5, 13 | Tags `mongo:latest` e `neo4j:latest` podem introduzir breaking changes silenciosamente e dificultam reprodutibilidade. |
| 🟡 MÉDIA | Containers rodando como root | Todos Dockerfiles | — | Nenhum Dockerfile define `USER` não-root. Processos executam como root, aumentando impacto de eventuais escapes de container. |
| 🟡 MÉDIA | Sem rate limiting nos endpoints | Todos serviços | — | Nenhum mecanismo de rate limiting implementado. Endpoints vulneráveis a brute-force e abuse. |
| 🟡 MÉDIA | Sem validação MIME type no upload | `frontend/app.py` | 41 | Apenas extensões são verificadas (`.wav`, `.mp3`), sem validação real do MIME type do conteúdo. |
| 🟡 MÉDIA | Volume mount do código-fonte em produção | `docker-compose.yml` | 38 | `./ai-engine:/app` monta código-fonte diretamente, expondo código proprietário e permitindo modificação em runtime. |

---

## 2. Plano de Atualização de Versões

### 2.1 Spring Boot / Java Backend (`pom.xml`)

| Dependência | Versão Atual | Versão Recomendada | Motivo |
|-------------|:------------:|:------------------:|--------|
| Spring Boot Parent | 3.2.4 | **3.4.3** | CVEs corrigidos, melhorias de performance, suporte a Virtual Threads |
| Spring AI | 0.8.1 | **1.0.0-M6** | API estabilizada, breaking changes resolvidos, melhor integração |
| Java | 17 | **21** | LTS atual, Virtual Threads, Pattern Matching, melhor GC |
| + `spring-boot-starter-security` | ausente | **adicionar** | Autenticação, autorização, CORS, security headers |
| + `spring-boot-starter-validation` | ausente | **adicionar** | Bean Validation (`@NotBlank`, `@Size`, etc.) |
| + `spring-boot-starter-actuator` | ausente | **adicionar** | Health checks, métricas, monitoramento |

### 2.2 AI Engine Python (`ai-engine/requirements.txt`)

| Dependência | Versão Atual | Versão Recomendada | Motivo |
|-------------|:------------:|:------------------:|--------|
| fastapi | sem versão | **==0.115.6** | Versão estável com security fixes |
| uvicorn | sem versão | **==0.34.0** | Performance e correções de bugs |
| python-multipart | sem versão | **==0.0.18** | Security fixes em upload handling |
| openai-whisper | sem versão | **==20240930** | Última release estável |
| librosa | sem versão | **==0.10.2** | Versão estável e testada |
| numpy | sem versão | **==1.26.4** | Compatível com torch e librosa |
| torch | sem versão | **==2.5.1** | CUDA 12.1 compatível, performance |
| transformers | sem versão | **==4.47.1** | Últimas correções de segurança |
| pymongo | sem versão | **==4.10.1** | Security fixes e connection pooling |

### 2.3 Frontend Python (`frontend/requirements.txt`)

| Dependência | Versão Atual | Versão Recomendada | Motivo |
|-------------|:------------:|:------------------:|--------|
| streamlit | sem versão | **==1.41.1** | Segurança e performance |
| requests | sem versão | **==2.32.3** | CVE fixes |
| ~~httpx~~ | sem versão | **remover** | Não utilizado no código |
| ~~numpy~~ | sem versão | **remover** | Não utilizado no frontend |
| ~~pandas~~ | sem versão | **remover** | Não utilizado no frontend |

> **Nota:** A remoção de `httpx`, `numpy` e `pandas` reduz ~80MB de memória e o tamanho da imagem Docker significativamente.

### 2.4 Docker Images (`docker-compose.yml`)

| Image | Versão Atual | Versão Recomendada | Motivo |
|-------|:------------:|:------------------:|--------|
| mongo | `latest` | **7.0** | Versão estável, reprodutível |
| neo4j | `latest` | **5.26-community** | Versão estável, reprodutível |

### 2.5 Dockerfiles

| Dockerfile | Base Image Atual | Base Image Recomendada | Motivo |
|------------|:----------------:|:----------------------:|--------|
| ai-engine | `nvidia/cuda:12.1.0-runtime-ubuntu22.04` | **`nvidia/cuda:12.4.1-runtime-ubuntu22.04`** | Security patches Ubuntu |
| backend (build) | `maven:3.9.6-eclipse-temurin-17` | **`maven:3.9.9-eclipse-temurin-21`** | Java 21 LTS |
| backend (runtime) | `eclipse-temurin:17-jre` | **`eclipse-temurin:21-jre-alpine`** | Menor superfície de ataque (~60% menor) |
| frontend | `python:3.10-slim` | **`python:3.12-slim`** | EOL Python 3.10 em Oct 2026; performance 10-15% melhor |

---

## 3. Otimizações de Performance (RAM/CPU)

### 3.1 AI Engine (`main.py`)

| Otimização | Impacto | Descrição |
|------------|---------|-----------|
| Whisper model configurável | 🟢 Alto | Usar modelo `tiny` para dev, `base` para prod via env var `WHISPER_MODEL`. Modelo `tiny` usa ~1GB menos de VRAM. |
| Streaming de áudio com `sr=16000` | 🟢 Médio | Forçar sample rate de 16kHz no `librosa.load()` para reduzir consumo de memória e alinhar com input do Whisper. |
| MongoDB connection pooling | 🟢 Médio | Configurar `maxPoolSize=10` e `minPoolSize=2` no MongoClient para evitar overhead de conexões. |
| Batch MongoDB writes | 🟢 Médio | Substituir loop de `update_one` por `bulk_write` para reduzir round-trips ao banco. |
| NumPy float32 | 🟡 Baixo | Usar `float32` ao invés de `float64` para reduzir uso de memória em 50% nos arrays. |
| Tempfile com `delete=True` | 🟡 Baixo | Processar áudio dentro do context manager para cleanup automático. |
| Limite de upload (10MB) | 🟢 Médio | Adicionar `MAX_UPLOAD_SIZE` para prevenir DoS por arquivos grandes. |

### 3.2 Backend Java

| Otimização | Impacto | Descrição |
|------------|---------|-----------|
| JVM tuning flags | 🟢 Alto | `-XX:+UseG1GC -XX:MaxRAMPercentage=75.0 -XX:+UseStringDeduplication` para melhor uso de memória em containers. |
| Virtual Threads (Java 21) | 🟢 Alto | `spring.threads.virtual.enabled=true` — melhora throughput em I/O-bound operations sem overhead de threads OS. |
| Connection pooling | 🟢 Médio | Configurar pool sizes para MongoDB e Neo4j para evitar connection starvation. |
| Response compression | 🟡 Baixo | Habilitar gzip compression para reduzir bandwidth em respostas JSON/text. |

### 3.3 Frontend (`app.py`)

| Otimização | Impacto | Descrição |
|------------|---------|-----------|
| Remover `httpx` | 🟢 Médio | Dependência não utilizada — reduz tamanho da imagem e potencial de vulnerabilidades. |
| Remover `pandas` | 🟢 Alto | ~50MB de memória economizados, não utilizado no código. |
| Remover `numpy` | 🟢 Médio | ~30MB de memória economizados, não utilizado no frontend. |
| Usar `st.session_state` | 🟡 Baixo | Cache de respostas para evitar requisições duplicadas ao backend. |

### 3.4 Docker

| Otimização | Impacto | Descrição |
|------------|---------|-----------|
| Alpine images | 🟢 Alto | Backend runtime com Alpine reduz imagem de ~300MB para ~120MB. |
| `.dockerignore` | 🟢 Médio | Excluir `__pycache__`, `.git`, `*.md`, `tests/` do build context. |
| Health checks | 🟢 Alto | Adicionar health checks em todos os containers para restart automático. |
| Non-root users | 🟢 Alto | Reduzir impacto de container escape executando como usuário não-privilegiado. |

---

## 4. Resumo de Alterações Realizadas

### Arquivos Modificados

| Arquivo | Alterações |
|---------|------------|
| `docker-compose.yml` | Versões pinadas, credenciais via env vars, health checks, MongoDB auth, remoção de volume mount |
| `backend/pom.xml` | Spring Boot 3.4.3, Java 21, Spring AI 1.0.0-M6, security/validation/actuator deps |
| `backend/Dockerfile` | Java 21, Alpine runtime, non-root user, JVM tuning flags |
| `ai-engine/requirements.txt` | Todas dependências com versões fixas |
| `ai-engine/Dockerfile` | CUDA 12.4.1, non-root user |
| `ai-engine/main.py` | File size limit, configurable Whisper model, sr=16000, bulk_write, connection pooling |
| `frontend/requirements.txt` | Versões fixas, removidos httpx/numpy/pandas |
| `frontend/Dockerfile` | Python 3.12, non-root user |
| `frontend/app.py` | Exception handling específico, student_id dinâmico |
| `LessonController.java` | Input validation com `@Valid`, `@NotBlank`, `@Size` |
| `SyllabusService.java` | Input sanitization contra prompt injection |

### Arquivos Criados

| Arquivo | Descrição |
|---------|-----------|
| `SECURITY_REVIEW_REPORT.md` | Este relatório |
| `backend/.../SecurityConfig.java` | CORS, security headers, basic security config |
| `backend/src/main/resources/application.properties` | JVM tuning, Virtual Threads, compression, pool sizes |
| `ai-engine/.dockerignore` | Exclusão de arquivos desnecessários do build |
| `backend/.dockerignore` | Exclusão de arquivos desnecessários do build |
| `frontend/.dockerignore` | Exclusão de arquivos desnecessários do build |

---

## 5. Recomendações Futuras

1. **Implementar autenticação completa** (OAuth2/JWT) nos endpoints REST e FastAPI
2. **Configurar TLS** para comunicação inter-serviços em produção
3. **Adicionar rate limiting** com Redis ou middleware dedicado
4. **Implementar logging centralizado** com ELK Stack ou similar
5. **Adicionar testes de segurança** (SAST/DAST) no pipeline CI/CD
6. **Rotação de credenciais** — implementar secrets management (Vault, AWS Secrets Manager)
7. **Monitoramento** — configurar alertas para tentativas de acesso não autorizado
8. **Backup automatizado** — configurar backup regular do MongoDB e Neo4j
