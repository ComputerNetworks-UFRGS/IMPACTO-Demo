import csv
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

from dashboard.models import Report, Scope, Region, Sector
from django.db import IntegrityError

def import_reports(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Pula linhas vazias ou com nome de relatório vazio
            if not row['Report Name'] or not row['Year Published']:
                continue

            try:
                # Verifica se o report já existe pelo nome e ano
                report, created = Report.objects.get_or_create(
                    name=row['Report Name'],
                    year=int(row['Year Published']),
                    defaults={
                        'years_covered': row['Years Covered'],
                        'company': row['Company'],
                        'number_of_participants': None if not row['Number of Participants'] or row['Number of Participants'].lower() == 'not informed' else int(row['Number of Participants']),
                        'participant_profiles': get_participant_profile(row['Participants Profile'])
                    }
                )

                if not created:
                    # Se o relatório já existe, atualize os campos necessários
                    report.years_covered = row['Years Covered']
                    report.company = row['Company']
                    report.number_of_participants = None if not row['Number of Participants'] or row['Number of Participants'].lower() == 'not informed' else int(row['Number of Participants'])
                    report.participant_profiles = get_participant_profile(row['Participants Profile'])
                    report.save()

                # Atualiza as relações many-to-many
                update_scopes(report, row['Scope'])
                update_regions(report, row['Region-Specific'])
                update_sectors(report, row['Sectors'])

                print(f'Successfully imported or updated report: {report.name}')
            except Exception as e:
                print(f"Error importing report {row.get('Report Name', 'Unknown')}: {str(e)}")

def get_participant_profile(profile):
    if not profile:
        return 'others'
    profile = profile.lower()
    if profile == 'not informed':
        return 'others'
    elif 'real-world devices' in profile:
        return 'real_devices'
    elif 'real-world cases' in profile:
        return 'real_cases'
    elif 'experts' in profile:
        return 'experts'
    elif 'organizations' in profile:
        return 'organizations'
    else:
        return 'others'

def update_scopes(report, scopes_str):
    report.scopes.clear()  # Limpa as relações anteriores
    if scopes_str and scopes_str.lower() != 'none':
        scopes = [scope.strip() for scope in scopes_str.split(',')]
        for scope in scopes:
            if scope:  # Verifica se não está vazio
                try:
                    scope_obj, _ = Scope.objects.get_or_create(name=scope)
                    report.scopes.add(scope_obj)
                except IntegrityError:
                    # Se houver erro de integridade, tenta buscar o objeto existente
                    scope_obj = Scope.objects.filter(name=scope).first()
                    if scope_obj:
                        report.scopes.add(scope_obj)

def update_regions(report, regions_str):
    report.regions.clear()  # Limpa as relações anteriores
    if regions_str and regions_str.lower() != 'none':
        # Remove espaços extras e divide por vírgula
        regions = [region.strip() for region in regions_str.split(',')]
        # Remove duplicatas da lista
        regions = list(dict.fromkeys(regions))
        
        for region in regions:
            if region:  # Verifica se não está vazio
                try:
                    # Primeiro tenta encontrar uma região existente
                    region_obj = Region.objects.filter(name__iexact=region).first()
                    if not region_obj:
                        # Se não encontrar, cria uma nova
                        region_obj = Region.objects.create(name=region)
                    report.regions.add(region_obj)
                except IntegrityError:
                    # Se houver erro de integridade, apenas usa o objeto existente
                    region_obj = Region.objects.filter(name__iexact=region).first()
                    if region_obj:
                        report.regions.add(region_obj)

def update_sectors(report, sectors_str):
    report.sectors.clear()  # Limpa as relações anteriores
    if sectors_str and sectors_str.lower() != 'none':
        sectors = [sector.strip() for sector in sectors_str.split(',')]
        for sector in sectors:
            if sector:  # Verifica se não está vazio
                try:
                    sector_obj, _ = Sector.objects.get_or_create(name=sector)
                    report.sectors.add(sector_obj)
                except IntegrityError:
                    # Se houver erro de integridade, tenta buscar o objeto existente
                    sector_obj = Sector.objects.filter(name=sector).first()
                    if sector_obj:
                        report.sectors.add(sector_obj)

if __name__ == "__main__":
    csv_file_path = os.path.join(project_root, "data", "reports_source.csv")
    print(f"Tentando importar de: {csv_file_path}")
    if not os.path.exists(csv_file_path):
        print(f"Arquivo CSV não encontrado em: {csv_file_path}")
        sys.exit(1)
    import_reports(csv_file_path)