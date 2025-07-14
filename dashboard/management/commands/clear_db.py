from django.core.management.base import BaseCommand
from dashboard.models import (
    CompanyProfile, AnnualRevenue, CybersecuritySpending, 
    CompanyAssets, AdvancedCompanyProfile, AttackHistory, Region
)
from collections import Counter


class Command(BaseCommand):
    help = 'Apaga todas as entradas do banco de dados, exceto os objetos da classe AttackType. Também remove duplicatas na tabela Region.'

    def handle(self, *args, **kwargs):
        # Remover duplicatas na tabela Region
        self.remove_region_duplicates()

        # Apagar todas as entradas das tabelas relacionadas
        models_to_clear = [
            CompanyProfile,
            AnnualRevenue,
            CybersecuritySpending,
            CompanyAssets,
            AdvancedCompanyProfile,
            AttackHistory
        ]
        
        for model in models_to_clear:
            model.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"Todos os registros da tabela '{model.__name__}' foram apagados."))

        self.stdout.write(self.style.SUCCESS("Operação concluída com sucesso."))

    def remove_region_duplicates(self):
        regions = Region.objects.values_list('name', 'type', 'continent')
        duplicated = [item for item, count in Counter(regions).items() if count > 1]

        for name, type, continent in duplicated:
            duplicates = Region.objects.filter(name=name, type=type, continent=continent)
            duplicates.exclude(id=duplicates.first().id).delete()  # Mantém o primeiro e remove os outros

        self.stdout.write(self.style.SUCCESS("Duplicatas removidas da tabela 'Region'."))