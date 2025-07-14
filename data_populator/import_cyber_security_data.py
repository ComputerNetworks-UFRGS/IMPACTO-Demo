import csv
import os
import sys
import django
from decimal import Decimal, InvalidOperation

# Adiciona o diretório do projeto ao PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Configura as configurações do Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Importa as configurações para verificar se o caminho está correto
try:
    from django.conf import settings
    settings.DATABASES  # Acessa uma configuração para ver se carregou corretamente
except ImportError as e:
    print(f"Erro ao importar as configurações: {e}")
    print(f"PYTHONPATH atual: {sys.path}")
    sys.exit(1)

django.setup()

from dashboard.models import Report, CyberSecurityData, Scope

def import_cyber_security_data(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            try:
                # Verifica se o report existe no banco de dados
                try:
                    report = Report.objects.get(name=row['FONTE'])
                except Report.DoesNotExist:
                    print(f"Error: Report '{row['FONTE']}' not found in the database.")
                    continue

                # Verifica se o escopo existe ou cria um novo
                scope, _ = Scope.objects.get_or_create(name=row['PROB A PRIORI'].lower())

                # Cria o registro de CyberSecurityData
                cyber_security_data = CyberSecurityData(
                    prob_a_priori=scope.name,
                    prob_marginal=row['PROB MARGINAL'],
                    p_a_given_b=convert_to_decimal(row['P(A|B)']),
                    c=row['C'].strip(),  # Agora 'C' é salvo corretamente como texto
                    p_c_given_p_a_given_b=convert_to_decimal(row['P(C|P(A|B))']),
                    report=report
                )
                cyber_security_data.save()

                # Associa o escopo ao relatório
                report.scopes.add(scope)

                print(f'Successfully imported cyber security data for {report.name}: {cyber_security_data.prob_a_priori} - {cyber_security_data.prob_marginal}')
            except Exception as e:
                print(f"Error importing cyber security data for {row['FONTE']}: {str(e)}")

def convert_to_decimal(value):
    """Converte uma string para Decimal, tratando casos de erro."""
    try:
        if value in [None, '', '-']:
            return None
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None  # Retorna None se o valor não for um decimal válido

if __name__ == "__main__":
    csv_file_path = os.path.join(project_root, "data", "reports_data.csv")
    print(f"Tentando importar de: {csv_file_path}")
    if not os.path.exists(csv_file_path):
        print(f"Arquivo CSV não encontrado em: {csv_file_path}")
        sys.exit(1)
    import_cyber_security_data(csv_file_path)