#!/usr/bin/env python3
# filepath: server_graphs.py

import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime

# Caminhos dos arquivos
csv_path = "server_monitor_data/server_usage_data.csv"
summary_path = "load_test_new/summary.md"
output_dir = "server_monitor_data"

def generate_server_graphs():
    print("Gerando gráficos de monitoramento do servidor...")
    
    # Verificar se os arquivos existem
    if not os.path.exists(csv_path):
        print(f"Erro: Arquivo CSV não encontrado em {csv_path}")
        return False
    
    if not os.path.exists(summary_path):
        print(f"Erro: Arquivo summary.md não encontrado em {summary_path}")
        return False
    
    # Criar diretório se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Carregar os dados
    df = pd.read_csv(csv_path)
    
    # Converter timestamp para datetime para facilitar a plotagem
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    
    # Calcular tempo relativo em segundos desde o início do teste
    start_time = df['timestamp'].min()
    df['elapsed_seconds'] = df['timestamp'] - start_time
    
    # Calcular estatísticas
    cpu_avg = df['cpu_usage'].mean()
    cpu_max = df['cpu_usage'].max()
    mem_used_avg = df['mem_used'].mean()
    mem_used_max = df['mem_used'].max()
    mem_free_avg = df['mem_free'].mean()
    net_rx_avg = df['net_rx'].mean()
    net_rx_max = df['net_rx'].max()
    net_tx_avg = df['net_tx'].mean()
    net_tx_max = df['net_tx'].max()
    
    # Configurar estilo dos gráficos
    plt.style.use('ggplot')
    
    # 1. Gráfico de CPU
    plt.figure(figsize=(10, 6))
    plt.plot(df['elapsed_seconds'], df['cpu_usage'], 'b-', linewidth=2)
    plt.fill_between(df['elapsed_seconds'], 0, df['cpu_usage'], alpha=0.3, color='blue')
    plt.title('Uso de CPU Durante o Teste', fontsize=14)
    plt.xlabel('Tempo (segundos)')
    plt.ylabel('CPU (%)')
    plt.grid(True, alpha=0.3)
    plt.ylim(0, max(100, df['cpu_usage'].max() * 1.1))
    plt.tight_layout()
    cpu_graph = f"{output_dir}/cpu_usage.png"
    plt.savefig(cpu_graph, dpi=300)
    plt.close()
    
    # 2. Gráfico de Memória
    plt.figure(figsize=(10, 6))
    plt.plot(df['elapsed_seconds'], df['mem_used'], 'r-', linewidth=2, label='Usada')
    plt.plot(df['elapsed_seconds'], df['mem_free'], 'g-', linewidth=2, label='Livre')
    plt.title('Uso de Memória Durante o Teste', fontsize=14)
    plt.xlabel('Tempo (segundos)')
    plt.ylabel('Memória (MB)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    mem_graph = f"{output_dir}/memory_usage.png"
    plt.savefig(mem_graph, dpi=300)
    plt.close()
    
    # 3. Gráfico de Rede
    plt.figure(figsize=(10, 6))
    plt.plot(df['elapsed_seconds'], df['net_rx'], 'g-', linewidth=2, label='Download (RX)')
    plt.plot(df['elapsed_seconds'], df['net_tx'], 'b-', linewidth=2, label='Upload (TX)')
    plt.title('Tráfego de Rede Durante o Teste', fontsize=14)
    plt.xlabel('Tempo (segundos)')
    plt.ylabel('Taxa (KB/s)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    net_graph = f"{output_dir}/network_traffic.png"
    plt.savefig(net_graph, dpi=300)
    plt.close()
    
    # Adicionar informações ao summary.md
    print(f"Adicionando informações ao {summary_path}...")
    
    with open(summary_path, 'a') as f:
        f.write("\n\n## Desempenho do Servidor\n\n")
        
        # Estatísticas
        f.write("### Estatísticas do Servidor\n\n")
        
        f.write("#### Uso de CPU\n")
        f.write(f"* **Uso Médio:** {cpu_avg:.2f}%\n")
        f.write(f"* **Uso Máximo:** {cpu_max:.2f}%\n\n")
        
        f.write("#### Uso de Memória\n")
        f.write(f"* **Memória Usada (Média):** {mem_used_avg:.2f} MB\n")
        f.write(f"* **Memória Usada (Máxima):** {mem_used_max:.2f} MB\n")
        f.write(f"* **Memória Livre (Média):** {mem_free_avg:.2f} MB\n\n")
        
        f.write("#### Tráfego de Rede\n")
        f.write(f"* **Download Médio:** {net_rx_avg:.2f} KB/s\n")
        f.write(f"* **Download Máximo:** {net_rx_max:.2f} KB/s\n")
        f.write(f"* **Upload Médio:** {net_tx_avg:.2f} KB/s\n")
        f.write(f"* **Upload Máximo:** {net_tx_max:.2f} KB/s\n\n")
        
        # Gráficos
        f.write("### Gráficos de Monitoramento do Servidor\n\n")
        
        f.write("#### Uso de CPU\n")
        f.write(f"![Uso de CPU](../server_monitor_data/cpu_usage.png)\n\n")
        
        f.write("#### Uso de Memória\n")
        f.write(f"![Uso de Memória](../server_monitor_data/memory_usage.png)\n\n")
        
        f.write("#### Tráfego de Rede\n")
        f.write(f"![Tráfego de Rede](../server_monitor_data/network_traffic.png)\n\n")
    
    print("✅ Gráficos gerados e relatório atualizado com sucesso!")
    return True

if __name__ == "__main__":
    generate_server_graphs()