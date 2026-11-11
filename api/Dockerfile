# --- ESTÁGIO 1: Builder ---
FROM python:3.12-slim-bookworm AS builder

# Configurações de Proxy e Pip
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_TRUSTED_HOST="pypi.org pypi.python.org files.pythonhosted.org" \
    PIP_CONSTRAINT=/tmp/constraints.txt

# 1) Configura certificados e dependências de compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# 2) Bypass SSL para o builder (proxy corporativo)
RUN python3 -c "import ssl; ssl._create_default_https_context = ssl._create_unverified_context"

# 3) Prepara constraints para evitar setuptools v82+ (que quebra o whisper)
RUN printf 'setuptools<75\n' > /tmp/constraints.txt

WORKDIR /build
COPY requirements.txt .

# 4) Instala dependências em um diretório isolado
RUN pip install --prefix=/install setuptools wheel \
    && pip install --prefix=/install -r requirements.txt


# --- ESTÁGIO 2: Runtime (Imagem Final) ---
FROM python:3.12-slim-bookworm AS runtime

LABEL maintainer="LinguistFlow AI Team"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_TRUSTED_HOST="pypi.org pypi.python.org files.pythonhosted.org" \
    NO_PROXY="ollama,localhost,127.0.0.1,api,db-mongo,db-neo4j"

WORKDIR /app

# 1) Instala apenas o necessário para rodar (ffmpeg é essencial para o Whisper)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsndfile1 curl tini ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2) Global SSL Bypass (necessário para o Whisper baixar modelos via HTTPS no seu proxy)
RUN python3 -c "import sysconfig, pathlib; \
    pathlib.Path(sysconfig.get_path('stdlib'), 'sitecustomize.py').write_text( \
    'import ssl\nssl._create_default_https_context = ssl._create_unverified_context\n')"

# 3) Copia apenas os pacotes instalados do builder (reduz MUITO o tamanho)
COPY --from=builder /install /usr/local

# 4) Configuração de usuário e permissões
RUN groupadd -r app && useradd -r -g app -m -d /home/app -s /sbin/nologin app \
    && mkdir -p /app /tmp/uploads \
    && chown -R app:app /app /tmp/uploads /home/app

COPY --chown=app:app app/ ./app/

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -fsS http://localhost:8000/healthz || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "1", \
     "--proxy-headers", "--forwarded-allow-ips", "*"]
