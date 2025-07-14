#!/bin/bash
# filepath: system_monitor.sh

# Diretório para armazenar dados
DIR="./monitor_data"
DATA_FILE="${DIR}/system_metrics.csv"
PID_FILE="${DIR}/monitor.pid"

# Função para iniciar o monitoramento
start_monitoring() {
    # Verificar se já está em execução
    if [ -f "$PID_FILE" ] && ps -p $(cat "$PID_FILE" 2>/dev/null) > /dev/null 2>&1; then
        echo "Monitor já está em execução com PID $(cat "$PID_FILE")"
        exit 1
    fi
    
    # Criar diretório e cabeçalho do CSV
    mkdir -p "$DIR"
    echo "timestamp,cpu_usage,mem_used,mem_free,swap_used,net_rx,net_tx" > "$DATA_FILE"
    
    # Script de monitoramento
    cat > "${DIR}/runner.sh" << 'EOF'
#!/bin/bash
INTERVAL=2
DATA_FILE="./monitor_data/system_metrics.csv"
INTERFACE=$(ip route | grep default | awk '{print $5}' || echo "eth0")
prev_rx=0; prev_tx=0; prev_time=0;

while true; do
    timestamp=$(date +%s)
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
    mem_info=$(free -m | grep Mem)
    mem_used=$(echo "$mem_info" | awk '{print $3}')
    mem_free=$(echo "$mem_info" | awk '{print $4}')
    swap_used=$(free -m | grep Swap | awk '{print $3}')
    
    net_line=$(grep $INTERFACE /proc/net/dev)
    rx_bytes=$(echo "$net_line" | awk '{print $2}')
    tx_bytes=$(echo "$net_line" | awk '{print $10}')
    
    if [ "$prev_time" -eq 0 ]; then
        prev_rx=$rx_bytes; prev_tx=$tx_bytes; prev_time=$timestamp
        sleep $INTERVAL; continue
    fi
    
    time_diff=$(($timestamp - $prev_time))
    if [ $time_diff -eq 0 ]; then time_diff=1; fi
    
    rx_rate=$(echo "scale=2; ($rx_bytes - $prev_rx) / $time_diff / 1024" | bc)
    tx_rate=$(echo "scale=2; ($tx_bytes - $prev_tx) / $time_diff / 1024" | bc)
    
    prev_rx=$rx_bytes; prev_tx=$tx_bytes; prev_time=$timestamp
    
    echo "$timestamp,$cpu_usage,$mem_used,$mem_free,$swap_used,$rx_rate,$tx_rate" >> "$DATA_FILE"
    
    if [ $(($timestamp % 30)) -eq 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] CPU: ${cpu_usage}% | Mem: ${mem_used}MB | Net: ${rx_rate}KB/s↓ ${tx_rate}KB/s↑"
    fi
    
    sleep $INTERVAL
done
EOF

    # Tornar executável e iniciar
    chmod +x "${DIR}/runner.sh"
    nohup "${DIR}/runner.sh" > "${DIR}/monitor.log" 2>&1 &
    echo $! > "$PID_FILE"
    
    echo "Monitor iniciado com PID $(cat "$PID_FILE")"
    echo "Dados sendo coletados em: $DATA_FILE"
    echo "Log disponível em: ${DIR}/monitor.log"
}

# Função para parar o monitoramento
stop_monitoring() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Monitor não está em execução"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    if ! ps -p $PID > /dev/null; then
        echo "Processo $PID não encontrado"
        rm -f "$PID_FILE"
        return 1
    fi
    
    echo "Parando monitor (PID $PID)..."
    kill $PID
    rm -f "$PID_FILE"
    
    # Verificar dados
    if [ ! -f "$DATA_FILE" ] || [ $(wc -l < "$DATA_FILE") -lt 2 ]; then
        echo "Dados insuficientes para análise"
        return 1
    fi
    
    # Gerar apenas o relatório básico de texto
    generate_report
    
    echo "Monitoramento finalizado!"
    echo "Arquivo CSV gerado: $DATA_FILE"
    echo "Você pode usar este arquivo para gerar gráficos com matplotlib."
}

# Função para gerar relatório de texto simples
generate_report() {
    echo "Gerando relatório básico..."
    
    awk -F, '
    BEGIN { cpu_total=0; mem_total=0; rx_total=0; tx_total=0; count=0; }
    NR>1 { 
        cpu_total += $2; mem_total += $3; 
        rx_total += $6; tx_total += $7; 
        if ($2 > cpu_max) cpu_max = $2;
        if ($3 > mem_max) mem_max = $3;
        if ($6 > rx_max) rx_max = $6;
        if ($7 > tx_max) tx_max = $7;
        count++;
    }
    END {
        if (count > 0) {
            print "Total registros: " count;
            print "CPU média: " cpu_total/count "%, máxima: " cpu_max "%";
            print "Memória média: " mem_total/count " MB, máxima: " mem_max " MB";
            print "Download médio: " rx_total/count " KB/s, máximo: " rx_max " KB/s";
            print "Upload médio: " tx_total/count " KB/s, máximo: " tx_max " KB/s";
        }
    }' "$DATA_FILE" > "${DIR}/report.txt"
    
    echo "✅ Relatório salvo em ${DIR}/report.txt"
    cat "${DIR}/report.txt"
}

# Função para verificar status
check_status() {
    if [ -f "$PID_FILE" ] && ps -p $(cat "$PID_FILE" 2>/dev/null) > /dev/null 2>&1; then
        echo "Monitor está em execução com PID $(cat "$PID_FILE")"
        if [ -f "$DATA_FILE" ]; then
            count=$(wc -l < "$DATA_FILE")
            echo "Registros coletados: $count"
            echo "Arquivo CSV: $DATA_FILE"
        fi
    else
        echo "Monitor não está em execução"
    fi
}

# Menu de comandos
case "$1" in
    start)
        start_monitoring
        ;;
    stop)
        stop_monitoring
        ;;
    status)
        check_status
        ;;
    report)
        generate_report
        ;;
    *)
        echo "Uso: $0 [start|stop|status|report]"
        echo ""
        echo "Comandos:"
        echo "  start   - Inicia o monitoramento"
        echo "  stop    - Para o monitoramento e gera relatório básico"
        echo "  status  - Verifica status do monitoramento"
        echo "  report  - Gera apenas relatório de texto com estatísticas"
        ;;
esac    