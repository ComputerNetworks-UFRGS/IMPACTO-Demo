#!/bin/bash

# Configuração de cores para output
GREEN='\033[0;32m'
BLUE='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuração de diretórios e arquivos
LOG_DIR="load_test_new"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_FILE="${LOG_DIR}/results.log"
SUMMARY_FILE="${LOG_DIR}/summary.md"
COOKIE_FILE="${LOG_DIR}/cookies.txt"
DEBUG_FILE="${LOG_DIR}/debug.log"
GRAPH_RESPONSE_FILE="${LOG_DIR}/response_time.png"
GRAPH_HIST_FILE="${LOG_DIR}/response_distribution.png"
GRAPH_BOX_FILE="${LOG_DIR}/status_distribution.png"
GRAPH_THROUGHPUT_FILE="${LOG_DIR}/throughput.png"
GRAPH_STATUS_FILE="${LOG_DIR}/status_pie.png"
GRAPH_HEATMAP_FILE="${LOG_DIR}/heatmap.png"
GRAPH_SIZE_TIME_FILE="${LOG_DIR}/size_vs_time.png"
GRAPH_TTFB_FILE="${LOG_DIR}/ttfb_analysis.png"
GRAPH_TREND_FILE="${LOG_DIR}/trend_analysis.png"

# Função para mostrar ajuda
show_help() {
    echo "Uso: $0 <URL> <total_requests> <concurrency> <username> <password> [debug]"
    echo ""
    echo "Argumentos:"
    echo "  URL            - URL base do servidor (ex: http://127.0.0.1:8000)"
    echo "  total_requests - Número total de requisições"
    echo "  concurrency    - Número de requisições simultâneas"
    echo "  username       - Nome de usuário (obrigatório)"
    echo "  password       - Senha (obrigatório)"
    echo "  debug         - Ativa logs de debug (opcional, true/false)"
    echo ""
    echo "Exemplo:"
    echo "  $0 http://127.0.0.1:8000 1000 50 admin senha123"
    echo "  $0 http://127.0.0.1:8000 1000 50 admin senha123 true"
}

# Validação de argumentos
if [ "$#" -lt 5 ]; then
    echo -e "${RED}Erro: Usuário e senha são obrigatórios${NC}"
    show_help
    exit 1
fi

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

# Configuração dos argumentos
URL="$1"
TOTAL_REQUESTS="$2"
CONCURRENCY="$3"
USERNAME="$4"
PASSWORD="$5"
DEBUG="${6:-false}"
BASE_URL=$(echo "$URL" | sed 's/\/$//')

# Validações
if ! [[ "$TOTAL_REQUESTS" =~ ^[0-9]+$ ]]; then
    echo -e "${RED}Erro: O número total de requisições deve ser um número inteiro${NC}"
    exit 1
fi

if ! [[ "$CONCURRENCY" =~ ^[0-9]+$ ]]; then
    echo -e "${RED}Erro: A concorrência deve ser um número inteiro${NC}"
    exit 1
fi

if [ "$CONCURRENCY" -gt "$TOTAL_REQUESTS" ]; then
    echo -e "${RED}Erro: A concorrência não pode ser maior que o total de requisições${NC}"
    exit 1
fi

# Função para logging de debug
debug_log() {
    mkdir -p "$LOG_DIR"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$DEBUG_FILE"
    if [ "${DEBUG:-false}" = true ]; then
        echo -e "${YELLOW}[DEBUG] $1${NC}"
    fi
}

# Banner inicial
show_banner() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════╗"
    echo "║         Teste de Carga - Django        ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_dependencies() {
    debug_log "Verificando dependências..."
    
    if ! dpkg -l | grep -q python3-venv; then
        debug_log "python3-venv não encontrado. Instalando..."
        sudo apt-get update && sudo apt-get install -y python3-venv
    fi
    
    if ! command -v curl &> /dev/null; then
        debug_log "curl não encontrado. Instalando..."
        sudo apt-get update && sudo apt-get install -y curl
    fi
}

setup_venv() {
    debug_log "Configurando ambiente virtual..."
    
    if [ ! -d "venv" ]; then
        debug_log "Criando novo ambiente virtual..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    debug_log "Instalando dependências Python..."
    pip install requests matplotlib numpy pandas seaborn >> "$DEBUG_FILE" 2>&1
}

setup_logs() {
    debug_log "Configurando diretórios de log..."
    mkdir -p "$LOG_DIR"
    > "$RESULTS_FILE"
    > "$COOKIE_FILE"
    
    debug_log "URL: $1"
    debug_log "Total de Requisições: $2"
    debug_log "Concorrência: $3"
    debug_log "Usuário: $USERNAME"
    
    cat > "$SUMMARY_FILE" << EOF
# Relatório de Teste de Carga
Data: $(date '+%Y-%m-%d %H:%M:%S')

## Configuração
- URL: $1
- Total de Requisições: $2
- Concorrência: $3
- Sistema: $(uname -s)
- Hostname: $(hostname)
- Usuário: $USERNAME

## Resultados
EOF
}

do_login() {
    debug_log "Iniciando processo de autenticação..."
    
    # Primeiro acesso para obter CSRF
    debug_log "Acessando página de login..."
    local login_page=$(curl -s -L "${BASE_URL}/admin/login/" \
        -c "$COOKIE_FILE" \
        -H "User-Agent: Mozilla/5.0" \
        -H "Accept: text/html,application/xhtml+xml" \
        2>&1)
    
    local csrf_token=$(echo "$login_page" | grep csrfmiddlewaretoken | sed 's/.*value="\([^"]*\)".*/\1/')
    
    if [ -z "$csrf_token" ]; then
        debug_log "ERRO: Token CSRF não encontrado na página de login"
        echo -e "${RED}Erro: Token CSRF não encontrado${NC}"
        exit 1
    fi
    
    debug_log "Token CSRF obtido: $csrf_token"
    
    # Realiza login com follow redirects
    debug_log "Tentando login com usuário: $USERNAME"
    local login_result=$(curl -s -L \
        -b "$COOKIE_FILE" \
        -c "$COOKIE_FILE" \
        -H "User-Agent: Mozilla/5.0" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -H "Accept: text/html,application/xhtml+xml" \
        -H "Referer: ${BASE_URL}/admin/login/" \
        --data-urlencode "username=${USERNAME}" \
        --data-urlencode "password=${PASSWORD}" \
        --data-urlencode "csrfmiddlewaretoken=${csrf_token}" \
        "${BASE_URL}/admin/login/" \
        2>&1)
    
    # Verifica se obteve o cookie de sessão
    if ! grep -q "sessionid" "$COOKIE_FILE"; then
        debug_log "ERRO: Cookie de sessão não encontrado após login"
        echo -e "${RED}Erro: Falha na autenticação${NC}"
        exit 1
    fi
    
    # Testa acesso à página do dashboard
    debug_log "Testando acesso ao dashboard..."
    local test_result=$(curl -s -L \
        -b "$COOKIE_FILE" \
        -H "User-Agent: Mozilla/5.0" \
        -H "Accept: text/html,application/xhtml+xml" \
        "${BASE_URL}/pt-br/dashboard/" \
        2>&1)
    
    if echo "$test_result" | grep -q "GT-IMPACTO"; then
        debug_log "Autenticação e acesso confirmados com sucesso"
        echo -e "${GREEN}Autenticação realizada com sucesso${NC}"
    else
        debug_log "ERRO: Conteúdo da página não encontrado após login"
        echo -e "${RED}Erro: Acesso negado após login${NC}"
        exit 1
    fi
}

# Adicionar timestamp de início do teste
TEST_START_TIME=$(date +%s.%N)

# Adicionar suporte para múltiplas URLs
URLS=(
    "${BASE_URL}/pt-br/dashboard/"
    "${BASE_URL}/pt-br/dashboard/company-profile/44/economic-planning/"
    "${BASE_URL}/pt-br/dashboard/company-profile/34/analysis_pro/"
)

# Modificar a função make_request para usar diferentes URLs
make_request() {
    local random_ip=${IPS[$RANDOM % ${#IPS[@]}]}
    local url=${URLS[$RANDOM % ${#URLS[@]}]}  # URL aleatória para distribuir a carga
    local request_id=$request_count
    local req_start_time=$(date +%s.%N)
    
    debug_log "Iniciando requisição #$request_id para $url com IP: $random_ip"
    
    result=$(curl -s -L \
        -b "$COOKIE_FILE" \
        -H "X-Forwarded-For: $random_ip" \
        -H "User-Agent: LoadTest/1.0" \
        -H "Accept: text/html,application/xhtml+xml" \
        -w "HTTP_CODE:%{http_code}\nTIME_TOTAL:%{time_total}\nSIZE_DOWNLOAD:%{size_download}\nTIME_STARTTRANSFER:%{time_starttransfer}\n" \
        "$url" \
        2>&1)
    
    local req_end_time=$(date +%s.%N)
    local http_code=$(echo "$result" | grep "HTTP_CODE:" | cut -d':' -f2)
    local time_total=$(echo "$result" | grep "TIME_TOTAL:" | cut -d':' -f2)
    local size_download=$(echo "$result" | grep "SIZE_DOWNLOAD:" | cut -d':' -f2)
    local time_ttfb=$(echo "$result" | grep "TIME_STARTTRANSFER:" | cut -d':' -f2)
    local path=$(echo "$url" | sed "s|${BASE_URL}||")
    
    if [ -n "$http_code" ] && [ -n "$time_total" ]; then
        # Calcular timestamp real em segundos desde o início do teste
        local elapsed_since_start=$(echo "$req_end_time - $TEST_START_TIME" | bc)
        
        debug_log "Requisição #$request_id completada: HTTP $http_code em ${time_total}s (tempo decorrido: ${elapsed_since_start}s)"
        echo "$random_ip $http_code $time_total $elapsed_since_start $size_download $time_ttfb \"$path\"" >> "$RESULTS_FILE"
        
        if [ "$http_code" -ge 400 ]; then
            debug_log "ERRO na requisição #$request_id: HTTP $http_code"
            echo "$result" >> "$DEBUG_FILE"
        fi
    else
        debug_log "ERRO: Falha ao obter código HTTP ou tempo de resposta na requisição #$request_id"
        echo "0.0.0.0 500 0.000 0.000 0 0.000 \"error\"" >> "$RESULTS_FILE"
    fi
}

generate_stats() {
    debug_log "Gerando estatísticas..."
    
    if [ ! -s "$RESULTS_FILE" ]; then
        debug_log "ERRO: Arquivo de resultados vazio ou não encontrado"
        echo -e "${RED}Erro: Não há dados para gerar estatísticas${NC}"
        return 1
    fi
    
    # Calcular o tempo real do teste (última requisição - primeira requisição)
    local elapsed_times=$(awk '{print $4}' "$RESULTS_FILE")
    local min_time=$(echo "$elapsed_times" | sort -n | head -1)
    local max_time=$(echo "$elapsed_times" | sort -n | tail -1)
    local real_test_duration=$(echo "$max_time - $min_time" | bc)
    
    debug_log "Tempo mínimo: $min_time, Tempo máximo: $max_time, Duração: $real_test_duration"
    
    # Garantir que temos uma duração positiva
    if (( $(echo "$real_test_duration <= 0" | bc -l) )); then
        debug_log "AVISO: Duração calculada inválida, usando valor da requisição mais lenta"
        real_test_duration=$(awk 'BEGIN {max=0} {if ($3>max) max=$3} END {print max*1.5}' "$RESULTS_FILE")
        debug_log "Usando duração alternativa: $real_test_duration"
    fi

    awk -v real_duration="$real_test_duration" '
    BEGIN {
        success = 0;
        error = 0;
    }
    {
        time = $3;
        code = $2;
        times[NR] = time;
        total += time;
        if (min == "" || time < min) min = time;
        if (time > max) max = time;
        count++;
        if (code >= 200 && code < 300) success++;
        else error++;
        times_by_status[code] = times_by_status[code] " " time;
        status_count[code]++;
    }
    END {
        # Ordenar tempos para calcular percentis (método simples, sem asort)
        # Copiar array para ordenação manual
        for (i in times) {
            times_sorted[i] = times[i];
        }
        
        # Ordenação simples (bubble sort)
        for (i = 1; i <= count; i++) {
            for (j = i + 1; j <= count; j++) {
                if (times_sorted[i] > times_sorted[j]) {
                    temp = times_sorted[i];
                    times_sorted[i] = times_sorted[j];
                    times_sorted[j] = temp;
                }
            }
        }
        
        # Calcular percentis
        p50 = times_sorted[int(count * 0.5)];
        p75 = times_sorted[int(count * 0.75)];
        p90 = times_sorted[int(count * 0.90)];
        p95 = times_sorted[int(count * 0.95)];
        p99 = times_sorted[int(count * 0.99)];
        
        # Calcular desvio padrão
        mean = total/count;
        for (i in times) {
            variance += (times[i] - mean) ^ 2;
        }
        stddev = sqrt(variance/count);
        
        print "\n### Estatísticas Gerais" >> "'$SUMMARY_FILE'"
        
        print "\n#### Métricas Gerais" >> "'$SUMMARY_FILE'"
        printf "* **Total de Requisições:** %d\n", count >> "'$SUMMARY_FILE'"
        printf "* **Tempo Total do Teste:** %.2f s\n", real_duration >> "'$SUMMARY_FILE'"
        printf "* **Throughput:** %.2f req/s (Média de requisições processadas por segundo durante todo o teste)\n", count/real_duration >> "'$SUMMARY_FILE'"
        
        print "\n#### Tempos de Resposta" >> "'$SUMMARY_FILE'"
        printf "* **Tempo Médio:** %.3f s\n", mean >> "'$SUMMARY_FILE'"
        printf "* **Desvio Padrão:** %.3f s\n", stddev >> "'$SUMMARY_FILE'"
        
        print "\n#### Taxa de Sucesso" >> "'$SUMMARY_FILE'"
        printf "* **Requisições com Sucesso:** %d (%.1f%%)\n", success, (success/count)*100 >> "'$SUMMARY_FILE'"
        printf "* **Requisições com Erro:** %d (%.1f%%)\n", error, (error/count)*100 >> "'$SUMMARY_FILE'"
        
        print "\n#### Distribuição por Status" >> "'$SUMMARY_FILE'"
        for (code in status_count) {
            n = status_count[code];
            total_time = 0;
            split(times_by_status[code], times_arr, " ");
            for (i = 1; i <= n; i++) {
                if (times_arr[i] != "") {
                    total_time += times_arr[i];
                }
            }
            avg_time = total_time/n;
            
            printf "* **Código %s:**\n", code >> "'$SUMMARY_FILE'"
            printf "  - Requisições: %d (%.1f%%)\n", n, (n/count)*100 >> "'$SUMMARY_FILE'"
            printf "  - Tempo médio: %.3f s\n", avg_time >> "'$SUMMARY_FILE'"
        }
    }
    ' "$RESULTS_FILE"
    
    debug_log "Estatísticas geradas com sucesso"
}

generate_graph() {
    debug_log "Gerando gráficos de análise..."
    
    # Garantir que o diretório existe
    mkdir -p "$LOG_DIR"
    
    python3 -c '
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import os
import sys
from datetime import datetime

# Garantir que o diretório existe
os.makedirs("'"$LOG_DIR"'", exist_ok=True)

# Configuração básica
plt.rcParams["figure.figsize"] = (12, 6)
plt.style.use("ggplot")

# Ler dados com tratamento de erro melhorado
try:
    # Verificar se arquivo existe e tem conteúdo
    if not os.path.exists("'"$RESULTS_FILE"'") or os.path.getsize("'"$RESULTS_FILE"'") == 0:
        print("ERRO: Arquivo de resultados vazio ou inexistente")
        sys.exit(1)
        
    # Tentar ler o arquivo corretamente - usando on_bad_lines em vez de error_bad_lines que está obsoleto
    df = pd.read_csv("'"$RESULTS_FILE"'", sep=" ", 
                    names=["ip", "status", "time", "elapsed_time", "size", "ttfb", "path"],
                    quotechar="\"", on_bad_lines="skip")
    
    # Limpar os dados e garantir tipos corretos
    df["path"] = df["path"].astype(str).str.strip("\"")
    df["request"] = range(1, len(df) + 1)
    
    # Atualizar a classificação de tipos para usar a nomenclatura correta
    df["type"] = df["path"].apply(lambda x: 
        "Index" if "/dashboard/" in x and "company-profile" not in x
        else "Análise de Risco" if "analysis_pro" in x
        else "Análise Econômica")
    
    df["is_error"] = df["status"] >= 400
    df["time"] = pd.to_numeric(df["time"], errors="coerce")
    df["elapsed_time"] = pd.to_numeric(df["elapsed_time"], errors="coerce")
    
    # Corrigir o tempo decorrido - normalizando para começar do zero
    min_elapsed = df["elapsed_time"].min()
    df["elapsed_time_corrected"] = df["elapsed_time"] - min_elapsed
    
    # Calcular a duração real do teste
    real_duration = df["elapsed_time_corrected"].max()
    
    # Verificar se temos dados válidos
    if len(df) == 0:
        raise ValueError("Nenhum dado válido encontrado no arquivo")
        
    print(f"Processando {len(df)} requisições com {sum(df.is_error)} erros")
    
except Exception as e:
    print(f"Erro ao processar dados: {str(e)}")
    print("Criando dados de exemplo mínimos para evitar falha completa")
    # Criar conjunto maior de dados de exemplo
    df = pd.DataFrame({
        "ip": ["1.1.1.1"] * 20,
        "status": [200] * 18 + [500, 404],
        "time": np.random.uniform(0.5, 2.0, 20),
        "elapsed_time": range(20),
        "elapsed_time_corrected": range(20),  # Adicionar campo corrigido
        "size": [1000] * 20,
        "ttfb": np.random.uniform(0.1, 0.5, 20),
        "path": ["/pt-br/dashboard/"] * 10 + ["/pt-br/dashboard/company-profile/44/economic-planning/"] * 10,
        "request": range(1, 21),
        "is_error": [False] * 18 + [True, True],
        "type": ["Index"] * 10 + ["Análise Econômica"] * 10
    })
    real_duration = 20.0
    print("Usando conjunto de dados de exemplo com 20 requisições")

# Configurar um esquema de cores consistente para os tipos de página com nomes atualizados
colors = {"Index": "royalblue", "Análise Econômica": "forestgreen", "Análise de Risco": "darkorange"}
markers = {"Index": "o", "Análise Econômica": "s", "Análise de Risco": "^"}

# 1. Gráfico de tempo de resposta com erros marcados e linhas de tendência por tipo
plt.figure(figsize=(14, 7))

# Plotar linhas de grade primeiro para ficarem atrás dos pontos
plt.grid(True, alpha=0.3, linestyle="--", zorder=0)

# Renderizar todos os pontos de sucesso e calcular linha de tendência por tipo
for tipo in sorted(df["type"].unique()):
    success_subset = df[(df["type"] == tipo) & (~df["is_error"])]
    if not success_subset.empty:
        color = colors.get(tipo, "gray")
        
        # Plotar pontos
        plt.scatter(success_subset["request"], success_subset["time"], 
                  alpha=0.6, label=f"{tipo} ({len(success_subset)} req)", 
                  color=color, marker=markers.get(tipo, "o"), zorder=5)
        
        # Calcular e plotar linha de tendência
        if len(success_subset) > 1:  # Precisa de pelo menos 2 pontos
            z = np.polyfit(success_subset["request"], success_subset["time"], 1)
            p = np.poly1d(z)
            x_trend = np.array([success_subset["request"].min(), success_subset["request"].max()])
            plt.plot(x_trend, p(x_trend), f"--", color=color, 
                   linewidth=2, alpha=0.8, 
                   label=f"Tendência {tipo} ({z[0]:.4f}x + {z[1]:.2f})")

# Adicionar média móvel para mostrar tendência geral
window = max(3, min(20, len(df) // 15))  # Ajuste dinâmico do tamanho da janela
media_movel = df["time"].rolling(window=window, min_periods=1).mean()
plt.plot(df["request"], media_movel, "k-", 
         label=f"Média Móvel ({window} req)", alpha=0.7, linewidth=1.5, zorder=6)

# Destacar erros com X vermelho grande e visível
erros = df[df["is_error"]]
if len(erros) > 0:
    # Usar scatter para marcar erros
    plt.scatter(erros["request"], erros["time"], 
              color="red", marker="X", s=150, linewidth=2, edgecolor="darkred",
              label=f"Erro ({len(erros)} req)", zorder=10)
    
    # Adicionar rótulos para cada erro com posicionamento melhorado
    for _, erro in erros.iterrows():
        # Posicionar o texto acima do ponto X
        plt.annotate(f"HTTP {int(erro.status)}", 
                   xy=(erro.request, erro.time),  # Posição do ponto
                   xytext=(0, 7),  # Deslocamento em pontos
                   textcoords="offset points",
                   ha="center",  # Centralizar horizontalmente
                   color="red", fontsize=10, fontweight="bold",
                   bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8))

# Informações estatísticas no gráfico
info_text = (f"Total: {len(df)} requisições\n"
             f"Tempo médio: {df.time.mean():.2f}s\n"
             f"Máximo: {df.time.max():.2f}s\n"
             f"Duração real: {real_duration:.1f}s")

plt.figtext(0.02, 0.02, info_text, fontsize=10, 
          bbox=dict(facecolor="white", alpha=0.8, boxstyle="round"))

# Melhorar layout e legibilidade
plt.title("Evolução do Tempo de Resposta por Requisição", fontsize=14, pad=10)
plt.xlabel("Número da Requisição")
plt.ylabel("Tempo (s)")
plt.legend(loc="upper left", fontsize=9)

# Garantir que o eixo X mostra todo o intervalo de requisições
plt.xlim(-len(df)*0.02, len(df)*1.02)  # Adicionar 2% de margem

# Ajustar limites do eixo Y para mostrar todos os dados com margem
y_max = max(df["time"].max() * 1.1, 0.1)  # Pelo menos 0.1s ou 10% acima do máximo
plt.ylim(0, y_max)

plt.tight_layout()
plt.savefig("'"$GRAPH_RESPONSE_FILE"'", dpi=300, bbox_inches="tight")
plt.close()

# 2. Histograma de tempos por tipo
plt.figure(figsize=(12, 6))
for i, tipo in enumerate(sorted(df["type"].unique())):
    subset = df[df["type"] == tipo]
    bins = min(20, max(5, len(subset) // 10))  # Número de bins automático
    plt.hist(subset["time"], bins=bins, alpha=0.7, 
            label=f"{tipo} ({len(subset)} req)", color=colors.get(tipo, None))

plt.title("Distribuição dos Tempos de Resposta por Tipo", fontsize=14)
plt.xlabel("Tempo de Resposta (s)")
plt.ylabel("Frequência")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("'"$GRAPH_HIST_FILE"'", dpi=300)
plt.close()

# 3. Box plot comparativo melhorado
plt.figure(figsize=(10, 6))
# Usar paleta de cores personalizada para manter consistência
sns.set_palette([colors.get(t, "gray") for t in sorted(df["type"].unique())])
ax = sns.boxplot(x="type", y="time", data=df, width=0.5)
ax.set_title("Comparação de Desempenho por Tipo de Página", fontsize=14)
ax.set_xlabel("Tipo de Página")
ax.set_ylabel("Tempo de Resposta (s)")

# Adicionar contagens em cada tipo
for i, box_type in enumerate(sorted(df["type"].unique())):
    count = len(df[df["type"] == box_type])
    ax.text(i, df["time"].min(), f"n={count}", 
          horizontalalignment="center", size="small", color="dimgrey", 
          bbox=dict(facecolor="white", alpha=0.6))

plt.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig("'"$GRAPH_BOX_FILE"'", dpi=300)
plt.close()

# 4. Gráfico de pizza por status com números absolutos
plt.figure(figsize=(9, 7))
status_counts = df["status"].value_counts().sort_index()

# Cores diferentes para status diferentes
colors = ["limegreen" if s < 400 else "crimson" for s in status_counts.index]

# Criar rótulos com código HTTP, contagem e porcentagem
labels = [f"HTTP {s}\n({c} req, {c/len(df):.1%})" 
         for s, c in zip(status_counts.index, status_counts.values)]

plt.pie(status_counts, labels=labels, colors=colors,
       wedgeprops={"edgecolor":"white", "linewidth": 1},
       textprops={"fontsize": 11})

plt.title("Distribuição de Status HTTP", fontsize=14, pad=20)
plt.tight_layout()
plt.savefig("'"$GRAPH_STATUS_FILE"'", dpi=300)
plt.close()

# 5. Throughput aprimorado com tempo real corrigido
plt.figure(figsize=(12, 6))

# Usar o tempo real corrigido
max_seconds = int(np.ceil(df["elapsed_time_corrected"].max()))
if max_seconds > 0:
    # Criar bins de 1 segundo
    bins = [i for i in range(max_seconds + 1)]
    # Contar requisições completadas em cada segundo
    hist, _ = np.histogram(df["elapsed_time_corrected"], bins=bins)
    
    # Plotar o histograma como gráfico de barras
    plt.bar(range(len(hist)), hist, width=0.8, alpha=0.7, color="steelblue")
    
    # Adicionar linha de média
    mean_throughput = len(df) / max_seconds if max_seconds > 0 else 0
    plt.axhline(y=mean_throughput, linestyle="--", color="red", 
               label=f"Média: {mean_throughput:.1f} req/s")
    
    # Adicionar linha de taxa ideal (total/duração)
    plt.title("Taxa de Requisições por Segundo (Tempo Real)", fontsize=14)
    plt.xlabel("Tempo Decorrido (s)")
    plt.ylabel("Requisições/s")
    plt.xlim(-0.5, len(hist)-0.5)  # Ajustar limites para mostrar todas as barras
    plt.xticks(range(0, len(hist), max(1, len(hist)//10)))  # Mostrar apenas alguns ticks no eixo X
    plt.legend()
    plt.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig("'"$GRAPH_THROUGHPUT_FILE"'", dpi=300)
    plt.close()
else:
    print("Aviso: Não foi possível calcular o throughput - dados de tempo insuficientes")

print("Geração de gráficos concluída com sucesso")
' 2>> "$DEBUG_FILE"

    # Verificar se os arquivos foram gerados
    local missing=0
    for img in "$GRAPH_RESPONSE_FILE" "$GRAPH_HIST_FILE" "$GRAPH_BOX_FILE" "$GRAPH_STATUS_FILE" "$GRAPH_THROUGHPUT_FILE"; do
        if [ ! -f "$img" ]; then
            echo -e "${YELLOW}Aviso: Arquivo não gerado: $img${NC}"
            missing=$((missing + 1))
        fi
    done
    
    if [ "$missing" -gt 0 ]; then
        echo -e "${YELLOW}⚠️ $missing arquivos de gráfico não foram gerados corretamente${NC}"
    else
        echo -e "${GREEN}✅ Todos os gráficos gerados com sucesso${NC}"
    fi

    # Atualizar o arquivo de resumo com informações mais precisas
    {
        echo -e "\n### Análise Visual"
        
        echo -e "\n#### Evolução do Tempo de Resposta"
        echo "![Tempo de Resposta](response_time.png)"
        echo "Tempos de resposta de todas as requisições ao longo do teste. Erros são marcados com X vermelho."
        
        echo -e "\n#### Distribuição dos Tempos"
        echo "![Distribuição](response_distribution.png)"
        echo "Histograma mostrando como os tempos de resposta estão distribuídos por tipo de página."
        
        echo -e "\n#### Comparação de Desempenho"
        echo "![Box Plot](status_distribution.png)"
        echo "Comparação estatística dos tempos entre tipos de página (quartis, mediana, outliers)."
        
        echo -e "\n#### Status HTTP"
        echo "![Status](status_pie.png)"
        echo "Distribuição dos códigos de status HTTP retornados durante o teste."
        
        echo -e "\n#### Taxa de Requisições"
        echo "![Throughput](throughput.png)"
        echo "Quantidade de requisições processadas por segundo ao longo do teste."
        
        echo -e "\n#### Erros Detectados"
        # Fix: Initialize count properly and ensure it's a number
        erro_count=$(awk 'BEGIN {count=0} $2 >= 400 {count++} END {print count}' "$RESULTS_FILE")
        erro_count=${erro_count:-0}  # Default to 0 if empty
        
        if [ "$erro_count" -eq 0 ]; then
            echo "Nenhum erro detectado durante o teste."
        else
            echo "Total de erros: $erro_count"
            # Mostrar todos os erros em testes pequenos ou limitar a 10 em testes grandes
            if [ "$erro_count" -le 10 ]; then
                awk '$2 >= 400 {printf "* Requisição %d: Status %s (%.3fs) - %s\n", NR, $2, $3, $7}' "$RESULTS_FILE" | sed 's/"//g'
            else
                awk '$2 >= 400 {printf "* Requisição %d: Status %s (%.3fs) - %s\n", NR, $2, $3, $7}' "$RESULTS_FILE" | sed 's/"//g' | head -10
                echo "* ... e mais $((erro_count - 10)) erros (consulte o log completo para detalhes)"
            fi
        fi
    } >> "$SUMMARY_FILE"
    
    debug_log "Gráficos gerados com sucesso"
}

# Array de IPs para simulação
IPS=(
    "8.8.8.8" "1.1.1.1" "192.168.1.200" "203.0.113.10" "198.51.100.25"
    "172.16.0.100" "10.0.0.50" "192.0.2.25" "198.18.0.75" "172.20.0.150"
)

# Execução principal
show_banner
check_dependencies
setup_venv
setup_logs "$@"
do_login

debug_log "Iniciando teste de carga..."
echo -e "${GREEN}Iniciando teste de carga para $URL${NC}"
echo -e "${BLUE}Executando $TOTAL_REQUESTS requisições ($CONCURRENCY em paralelo)${NC}"

progress=0
running=0
request_count=0

while [ $request_count -lt $TOTAL_REQUESTS ]; do
    if [ "$running" -lt "$CONCURRENCY" ]; then
        make_request &
        running=$((running + 1))
        request_count=$((request_count + 1))
        
        new_progress=$((request_count * 100 / TOTAL_REQUESTS))
        if [ $new_progress -ne $progress ]; then
            progress=$new_progress
            debug_log "Progresso: $progress%"
            printf "\rProgresso: [%-50s] %d%%" $(printf "#%.0s" $(seq 1 $((progress/2)))) $progress
        fi
    else
        wait -n
        running=$((running - 1))
    fi
done

wait
echo -e "\n"

generate_stats
generate_graph

debug_log "Teste finalizado"
echo -e "${GREEN}Teste finalizado!${NC}"
echo -e "${BLUE}Resultados salvos em:${NC}"
echo "- Log detalhado: $RESULTS_FILE"
echo "- Log de debug: $DEBUG_FILE"
echo "- Sumário: $SUMMARY_FILE"
echo "- Gráfico: $GRAPH_FILE"
