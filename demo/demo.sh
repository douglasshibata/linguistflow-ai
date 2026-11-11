#!/bin/bash
# =============================================================================
# LinguistFlow AI - Demo Script (v2 — Python unified backend)
# Executa demonstracoes contra o servico FastAPI (lessons + speech + LLM router).
# Requer: curl, jq, servicos rodando (docker compose up -d)
# =============================================================================

set -euo pipefail

# --- Cores ANSI ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

API_URL="${API_URL:-http://localhost:8000}"
OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
LESSON_PROVIDER="${LESSON_PROVIDER:-}"
LESSON_MODEL="${LESSON_MODEL:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SAMPLES_DIR="$SCRIPT_DIR/samples"

TOTAL_TESTS=0
TOTAL_PASS=0

# =============================================================================
# Utilitarios
# =============================================================================

banner() {
    echo -e "${CYAN}"
    cat << 'BANNER'
  _     _                   _     _   _____ _
 | |   (_)_ __   __ _ _   _(_)___| |_|  ___| | _____      __
 | |   | | '_ \ / _` | | | | / __| __| |_  | |/ _ \ \ /\ / /
 | |___| | | | | (_| | |_| | \__ \ |_|  _| | | (_) \ V  V /
 |_____|_|_| |_|\__, |\__,_|_|___/\__|_|   |_|\___/ \_/\_/
                |___/
BANNER
    echo -e "${NC}"
    echo -e "${BOLD}  Aprendizado Adaptativo de Idiomas com IA${NC}"
    echo -e "${DIM}  FastAPI + LiteLLM (multi-LLM) + Whisper + Librosa${NC}"
    echo ""
}

separator() {
    echo -e "${DIM}------------------------------------------------------------------------${NC}"
}

press_enter() {
    echo ""
    echo -e "${DIM}  Pressione ENTER para continuar...${NC}"
    read -r
}

act_header() {
    local num="$1"
    local title="$2"
    echo ""
    separator
    echo -e "${BOLD}${CYAN}  ATO $num: $title${NC}"
    separator
    echo ""
}

success() { echo -e "  ${GREEN}OK${NC} $1"; }
fail()    { echo -e "  ${RED}FAIL${NC} $1"; }
warn()    { echo -e "  ${YELLOW}!${NC} $1"; }
info()    { echo -e "  ${BLUE}>${NC} $1"; }

pretty_json() {
    echo "$1" | jq -C '.' 2>/dev/null || echo "$1"
}

check_deps() {
    local missing=0
    for cmd in curl jq; do
        if ! command -v "$cmd" &> /dev/null; then
            fail "Dependencia nao encontrada: $cmd"
            missing=1
        fi
    done
    if [ "$missing" -eq 1 ]; then
        echo -e "${RED}Instale curl e jq e tente novamente.${NC}"
        exit 1
    fi
}

# =============================================================================
# ATO 0: Health Check
# =============================================================================

health_check() {
    act_header "0" "HEALTH CHECK"

    info "Verificando API em $API_URL/healthz ..."
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if curl -sf "$API_URL/healthz" > /dev/null; then
        success "API FastAPI operacional"
        local r
        r=$(curl -sf "$API_URL/readyz" 2>/dev/null || echo "")
        if [ -n "$r" ]; then
            info "Default provider: $(echo "$r" | jq -r '.default_provider')"
            info "Providers: $(echo "$r" | jq -r '.providers | join(", ")')"
        fi
        TOTAL_PASS=$((TOTAL_PASS + 1))
    else
        fail "API nao respondeu em $API_URL"
        warn "Execute: docker compose up -d"
        return 1
    fi
}

# =============================================================================
# ATO 0.5: Providers habilitados
# =============================================================================

demo_providers() {
    act_header "0.5" "LLM PROVIDERS HABILITADOS"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    local resp
    resp=$(curl -sf "$API_URL/api/lesson/providers" 2>/dev/null || echo "")
    if [ -z "$resp" ]; then
        fail "Endpoint /api/lesson/providers indisponivel"
        return 1
    fi
    info "Default: ${BOLD}$(echo "$resp" | jq -r '.defaultProvider')${NC}"
    echo ""
    echo "$resp" | jq -r '.providers | to_entries[] | "    \(.key):\n      - \(.value | join("\n      - "))"'
    echo ""
    success "Providers listados"
    TOTAL_PASS=$((TOTAL_PASS + 1))
}

# =============================================================================
# ATO 1: Geracao de Aula
# =============================================================================

demo_adaptive_lesson() {
    act_header "1" "GERACAO DE AULA ADAPTATIVA"

    local student_id="STU123"
    local topic="Present+Perfect"
    local hobby="Football"

    info "Aluno:    ${BOLD}$student_id${NC}"
    info "Topico:   ${BOLD}Present Perfect${NC}"
    info "Hobby:    ${BOLD}Football${NC}"
    info "Provider: ${BOLD}${LESSON_PROVIDER:-<default>}${NC}"
    info "Model:    ${BOLD}${LESSON_MODEL:-<default>}${NC}"
    echo ""

    local url="$API_URL/api/lesson?studentId=$student_id&topic=$topic&hobby=$hobby"
    [ -n "$LESSON_PROVIDER" ] && url="$url&provider=$LESSON_PROVIDER"
    [ -n "$LESSON_MODEL" ] && url="$url&model=$LESSON_MODEL"

    info "GET $url"
    echo ""

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    local response
    response=$(curl -sf "$url" --max-time 180 2>/dev/null || echo "")

    if [ -z "$response" ]; then
        fail "Sem resposta da API (timeout ou erro)"
        return 1
    fi

    echo -e "${BOLD}  Resposta da IA:${NC}"
    echo -e "${YELLOW}"
    echo "$response" | head -30 | sed 's/^/    /'
    echo -e "${NC}"

    if [ ${#response} -gt 10 ]; then
        success "Aula adaptativa gerada (${#response} caracteres)"
        TOTAL_PASS=$((TOTAL_PASS + 1))
    else
        fail "Resposta muito curta"
    fi
}

# =============================================================================
# ATO 2: Analise de Pronuncia
# =============================================================================

demo_speech_analysis() {
    act_header "2" "ANALISE DE PRONUNCIA"

    local audio_file="$SAMPLES_DIR/sample_audio.wav"
    if [ ! -f "$audio_file" ]; then
        warn "Arquivo de amostra nao encontrado: $audio_file"
        info "Gerando WAV sintetico (1s silencio)..."
        if command -v python3 &> /dev/null; then
            python3 -c "
import wave, struct
with wave.open('$audio_file', 'w') as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(16000)
    f.writeframes(struct.pack('<' + 'h' * 16000, *([0] * 16000)))
" 2>/dev/null
            if [ -f "$audio_file" ]; then
                success "WAV sintetico criado"
            else
                fail "Falha ao gerar WAV"
                TOTAL_TESTS=$((TOTAL_TESTS + 1))
                return 1
            fi
        else
            fail "python3 nao disponivel"
            TOTAL_TESTS=$((TOTAL_TESTS + 1))
            return 1
        fi
    fi

    info "POST $API_URL/api/speech/analyze (arquivo: $(basename "$audio_file"))"
    echo ""

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    local response
    response=$(curl -sf -X POST "$API_URL/api/speech/analyze" \
        -F "file=@$audio_file;type=audio/wav" \
        -F "student_id=STU123" \
        --max-time 180 2>/dev/null || echo "")

    if [ -z "$response" ]; then
        fail "Sem resposta da API"
        return 1
    fi

    pretty_json "$response"
    echo ""

    success "Analise concluida"
    TOTAL_PASS=$((TOTAL_PASS + 1))
}

# =============================================================================
# ATO 3: Grafo Neo4j (modelo conceitual)
# =============================================================================

demo_knowledge_graph() {
    act_header "3" "GRAFO DE CONHECIMENTO - NEO4J"
    info "Modelo de nos/relacoes no Neo4j:"
    echo -e "${CYAN}"
    cat << 'GRAPH'
    (WordNode)--HAS_ROOT-->(WordNode)
        |
        +--SYNONYM_OF-->(WordNode)
        |
        +--USED_IN_CONTEXT-->(ContextNode)

    (:Word{text:"running"})--HAS_ROOT-->(:Word{text:"run"})
    (:Word{text:"running"})--SYNONYM_OF-->(:Word{text:"jogging"})
GRAPH
    echo -e "${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    TOTAL_PASS=$((TOTAL_PASS + 1))
    success "Modelo documentado (driver async neo4j na API)"
}

# =============================================================================
# ATO 4: Ollama Local
# =============================================================================

demo_ollama_check() {
    act_header "4" "OLLAMA LOCAL (opcional)"
    info "Verificando Ollama em $OLLAMA_URL ..."
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if curl -sf "$OLLAMA_URL/api/tags" > /dev/null; then
        success "Ollama operacional"
        info "Modelos disponiveis:"
        curl -sf "$OLLAMA_URL/api/tags" | jq -r '.models[]?.name' | sed 's/^/    - /' || true
        TOTAL_PASS=$((TOTAL_PASS + 1))
    else
        warn "Ollama nao responde. Inicie com:"
        warn "  docker compose --profile local-llm up -d"
        warn "  docker exec linguist-ollama ollama pull llama3.2"
    fi
}

# =============================================================================
# Relatorio
# =============================================================================

report() {
    echo ""
    separator
    echo -e "${BOLD}${CYAN}  RELATORIO FINAL${NC}"
    separator
    echo ""
    echo -e "  ${BOLD}Testes executados:${NC} $TOTAL_TESTS"
    echo -e "  ${BOLD}Testes passaram:${NC}  ${GREEN}$TOTAL_PASS${NC}"
    echo ""
    if [ "$TOTAL_PASS" -eq "$TOTAL_TESTS" ] && [ "$TOTAL_TESTS" -gt 0 ]; then
        echo -e "  ${GREEN}${BOLD}TODAS AS DEMOS EXECUTADAS COM SUCESSO!${NC}"
    else
        echo -e "  ${YELLOW}Algumas demos podem ter falhado. Veja os logs.${NC}"
    fi
    echo ""
    separator
    echo -e "${DIM}  LinguistFlow AI v2.0 - Aprendizado Adaptativo de Idiomas${NC}"
    separator
    echo ""
}

run_all() {
    banner
    check_deps
    press_enter

    health_check
    press_enter

    demo_providers
    press_enter

    demo_adaptive_lesson
    press_enter

    demo_speech_analysis
    press_enter

    demo_knowledge_graph
    press_enter

    demo_ollama_check
    press_enter

    report
}

case "${1:-all}" in
    health)     health_check ;;
    providers)  demo_providers ;;
    lesson)     demo_adaptive_lesson ;;
    speech)     demo_speech_analysis ;;
    graph)      demo_knowledge_graph ;;
    ollama)     demo_ollama_check ;;
    all)        run_all ;;
    *)
        echo "Uso: $0 [all|health|providers|lesson|speech|graph|ollama]"
        echo ""
        echo "Variaveis de ambiente:"
        echo "  API_URL=http://localhost:8000     URL da API (default)"
        echo "  OLLAMA_URL=http://localhost:11434 URL do Ollama"
        echo "  LESSON_PROVIDER=ollama            Provider para o ato 'lesson'"
        echo "  LESSON_MODEL=llama3.2             Modelo para o ato 'lesson'"
        exit 1
        ;;
esac
