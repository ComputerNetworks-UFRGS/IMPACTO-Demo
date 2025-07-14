# IMPACTO: Plataforma de Capacitação em Cibersegurança Baseada em Simulação de Aspectos Econômicos de Ciberataques

O planejamento em cibersegurança representa um desafio para empresas que operam com recursos técnicos e financeiros limitados, especialmente diante do crescimento de ataques cibernéticos e de seus impactos econômicos. Nesse contexto, a plataforma IMPACTO foi desenvolvida para apoiar a formação de estudantes e profissionais da área, com foco na análise de riscos e no planejamento de investimentos em cibersegurança. A plataforma integra aspectos técnicos e econômicos por meio de simulações baseadas em cenários realistas, utilizando dados de relatórios públicos e modelos econômicos do estado da arte. A plataforma IMPACTO promove um aprendizado aplicado e estruturado, permitindo ao usuário compreender o impacto financeiro de diferentes estratégias de proteção, bem como os riscos em diferentes contextos. Avaliações de usabilidade e funcionalidade foram realizadas, e os resultados indicam uma alta eficácia como ferramenta educacional e de apoio à tomada de decisão.

## Selos considerados para a submissão do Salão de Ferramentas SBSeg25

Os selos considerados são: Disponíveis e Funcionais.

## Servidor de testes

Caso você deseje apenas testar a plataforma IMPACTO, um servidor de testes está disponível em https://gt-impacto.inf.ufrgs.br. Caso você deseje fazer o deploy local da aplicação, siga as instruções abaixo.

## Pré-requisitos (para a execução de run.sh)

- **Linux**
- **Python 3.11.x** (para uso de PostgreSQL)

### Verificar a versão do Python
```bash
python3 --version
```

### Para instalar Python 3.11
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.11
```

---

## Instalação

1. **Clone o repositório:**
   ```bash
   git clone <repository>
   cd IMPACTO
   ```

2. **Execute o script pela primeira vez para criar os arquivos de configuração:**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
   
   Para especificar uma porta diferente (padrão é 8000):
   ```bash
   ./run.sh 8080
   ```

3. **Modifique os arquivos criados:**

   - **`.env`:**
     ```plaintext
     DB_PASSWORD=sua_senha_segura
     ADMIN_USERNAME=nome_login_admin
     ADMIN_PASSWORD=sua_senha_segura
     ADMIN_EMAIL=email_login_admin@email.com
     DJANGO_SECRET_KEY=sua_chave_secreta_segura
     ```

   - **`postgres_setup.sql`:**
     ```sql
     CREATE USER gt_impacto WITH PASSWORD 'sua_senha_segura';
     ```

   - **`reset_db.sql`:**
     ```sql
     CREATE USER gt_impacto WITH PASSWORD 'sua_senha_segura';
     ```

   **IMPORTANTE:** Use a mesma senha em todos os arquivos!

4. **Execute o script novamente para completar a instalação:**
   ```bash
   ./run.sh
   ```

---

## Uso Diário

Para iniciar a plataforma após a instalação inicial:
```bash
chmod +x start.sh
./start.sh
```

Para especificar uma porta diferente (padrão é 8000):
```bash
./start.sh 8080
```

---

## Acesso

- **URL:** [http://localhost:8000/admin](http://localhost:8000/admin)
  (Substitua 8000 pela porta escolhida, caso tenha alterado)
- **Usuário:** Configurado no `ADMIN_USERNAME` do `.env`
- **Senha:** Configurada no `ADMIN_PASSWORD` do `.env`

---

## Notas de Segurança

- O `run.sh` só precisa ser executado na instalação inicial.
- Para uso diário, utilize apenas o `start.sh`.
- Os arquivos de configuração (`.env`, `postgres_setup.sql`, `reset_db.sql`) são ignorados pelo Git por motivos de segurança.
- Mantenha os outros campos dos arquivos de configuração inalterados.

## Teste de Carga

Para realizar testes de carga na aplicação, utilize o script `load_test.sh`:

```bash
chmod +x load_test.sh
./load_test.sh <URL> <total_requests> <concurrency> <username> <password> [debug]
```

### Parâmetros:
- **URL**: URL base do servidor (ex: http://127.0.0.1:8000)
- **total_requests**: Número total de requisições
- **concurrency**: Número de requisições simultâneas
- **username**: Nome de usuário para autenticação
- **password**: Senha do usuário
- **debug**: (opcional) Ativa logs detalhados (true/false)

### Modo Debug

O parâmetro `debug` ativa um log detalhado que inclui:
- Processo de autenticação passo a passo
- Tokens CSRF obtidos
- Cookies de sessão
- Headers HTTP de cada requisição
- Códigos de resposta detalhados
- Tempos de resposta individuais

#### Exemplos de uso:

1. **Sem debug (modo normal):**
```bash
./load_test.sh "http://127.0.0.1:8000" 1000 50 admin senha123
```

2. **Com debug ativado:**
```bash
./load_test.sh "http://127.0.0.1:8000" 1000 50 admin senha123 true
```

## Monitoramento do Servidor e Geração de Gráficos

Para gerar gráficos de desempenho do servidor durante os testes de carga, siga os passos abaixo:

### 1. Monitorar o servidor durante o teste de carga

Antes de iniciar o teste de carga, inicie o monitoramento do servidor:

```bash
./system_monitor.sh start
```

Execute o teste de carga e, após seu término, pare o monitoramento:

```bash
./system_monitor.sh stop
```

### 2. Preparar os dados para geração dos gráficos

Crie a pasta para os dados de monitoramento do servidor:

```bash
mkdir -p server_monitor_data
```

Copie o arquivo CSV de resultado do monitoramento para esta pasta:

```bash
cp ./monitor_data/system_metrics.csv server_monitor_data/server_usage_data.csv
```

### 3. Gerar os gráficos

Execute o script de geração de gráficos:

```bash
python3 server_graphs.py
```

### 4. Resultados

Os gráficos serão gerados na pasta `server_monitor_data` e incluirão:
- Uso de CPU durante o teste
- Uso de memória durante o teste
- Tráfego de rede durante o teste

As estatísticas e links para os gráficos serão automaticamente adicionados ao relatório de teste de carga (`load_test_new/summary.md`).
