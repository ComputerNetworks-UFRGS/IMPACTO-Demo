import os
import sys
import django

# Diretório do projeto ao PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Configurações do Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Tenta importar as configurações para verificar se o caminho está correto
try:
    from django.conf import settings
    settings.DATABASES  # Tenta acessar uma configuração para ver se carregou corretamente
except ImportError as e:
    print(f"Erro ao importar as configurações: {e}")
    print(f"PYTHONPATH atual: {sys.path}")
    sys.exit(1)

django.setup()

from dashboard.models import Scope, Sector, Report, CyberSecurityData

def delete_all_entries():
    try:
        # Deletar todos os registros do modelo CyberSecurityData
        cybersecurity_data_count = CyberSecurityData.objects.all().count()
        CyberSecurityData.objects.all().delete()
        print(f"Deleted {cybersecurity_data_count} cybersecurity data entries.")

        # Deletar todos os registros do modelo Report
        report_count = Report.objects.all().count()
        Report.objects.all().delete()
        print(f"Deleted {report_count} reports.")

        # Deletar todos os registros do modelo Scope
        scope_count = Scope.objects.all().count()
        Scope.objects.all().delete()
        print(f"Deleted {scope_count} scopes.")

        # Deletar todos os registros do modelo Sector
        sector_count = Sector.objects.all().count()
        Sector.objects.all().delete()
        print(f"Deleted {sector_count} sectors.")
    
    except Exception as e:
        print(f"An error occurred while deleting data: {e}")

if __name__ == "__main__":
    delete_all_entries()