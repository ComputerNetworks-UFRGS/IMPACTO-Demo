from django.core.management.base import BaseCommand
from dashboard.models import (
    CompanyProfile, AnnualRevenue, CybersecuritySpending, 
    CompanyAssets, AdvancedCompanyProfile, AttackType, AttackHistory, Region
)
from accounts.models import User, Instructor
from dotenv import load_dotenv
import os
from decimal import Decimal

class Command(BaseCommand):
    help = "Popula o banco de dados com dados de exemplo"


    def handle(self, *args, **kwargs):
        # Carrega Variaveis do env
        load_dotenv()

        # Cria super usuário gt (com os dados da env)
        try:
            superuser = User.objects.create_superuser(
                username=os.getenv('ADMIN_USERNAME'),
                email=os.getenv('ADMIN_EMAIL'),
                password=os.getenv('ADMIN_PASSWORD'),
                name='GT Impacto',
                institution='UFRGS',
                job='Professor',
                role='Coordinator',
                user_type='instructor'
            )
            Instructor.objects.create(user=superuser)
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Superuser already exists or error: {e}'))

        # 0. Limpa eventuais duplicatas de AttackType
        for attack in ['malware', 'phishing', 'ddos', 'breach', 'ransomware']:
            duplicates = AttackType.objects.filter(attack_type=attack)
            if duplicates.count() > 1:
                self.stdout.write(f'Removing duplicates for {attack}...')
                first = duplicates.first()
                duplicates.exclude(id=first.id).delete()

        # 0.1. Get ou cria AttackTypes
        attack_types = {}
        for attack in ['malware', 'phishing', 'ddos', 'breach', 'ransomware']:
            attack_obj, created = AttackType.objects.get_or_create(attack_type=attack)
            attack_types[attack] = attack_obj
            if created:
                self.stdout.write(f'Created {attack} attack type')
            else:
                self.stdout.write(f'Using existing {attack} attack type')

        # tipos de ataques para uso posterior
        malware = attack_types['malware']
        phishing = attack_types['phishing']
        ddos = attack_types['ddos']
        breach = attack_types['breach']
        ransomware = attack_types['ransomware']

        # 1. Buscar ou Criar Regiões
        brasil, _ = Region.objects.get_or_create(name='Brazil', type='country', continent='south_america')
        europa, _ = Region.objects.get_or_create(name='Europe', type='continent')
        estados_unidos, _ = Region.objects.get_or_create(name='United States', type='country', continent='north_america')
        asia, _ = Region.objects.get_or_create(name='Asia', type='continent')

        # 2. Buscar Tipos de Ataques Existentes
        malware = AttackType.objects.get(attack_type='malware')
        phishing = AttackType.objects.get(attack_type='phishing')
        ddos = AttackType.objects.get(attack_type='ddos')
        breach = AttackType.objects.get(attack_type='breach')

        # 3. Criar Perfis de Empresas Avançadas

        # Empresa 1: Amazon
        amazon = AdvancedCompanyProfile.objects.create(
            name="Amazon",
            headquarters_country="United States",
            headquarters_country_en="United States",
            industry_type="retail",
            employee_count=1600000,  # Aproximadamente 1.6 milhões de funcionários
            company_size="large",
            remote_work_rate=25.0,  # Parcela significativa dos funcionários trabalha remotamente
            global_presence=True,
            authentication_factors=2,
            cloud_solution_type='wan',
            it_system_monitoring=True,
            periodic_system_updates=True,
            data_encryption_in_storage=True,
            data_encryption_in_transit=True,
            vpn_for_remote_access=True,
            cybersecurity_awareness_and_training=True,
            documented_response_plan=True,
            response_plan_update=True,
            operational_recovery_capacity=True,
            credentials_maintenance=True,
            vulnerability_identification=True,
            network_systems_traffic_monitoring=True,
            threat_identification_process=True,
            it_records_presence=True,
            antivirus=True,
            firewall=True,
            intrusion_detection_system=True,
            endpoint_detection_and_response=True,
            it_security_team=True,
            updated_inventory=True,
            backup_maintenance=True,
            risk_prioritization=True,
        )

        # Empresa 2: Microsoft
        microsoft = AdvancedCompanyProfile.objects.create(
            name="Microsoft",
            headquarters_country="United States",
            headquarters_country_en="United States",
            industry_type="technology",
            employee_count=220000,  # Aproximadamente 220.000 funcionários
            company_size="large",
            remote_work_rate=60.0,  # Alta taxa de trabalho remoto
            global_presence=True,
            authentication_factors=2,
            cloud_solution_type='wan',
            it_system_monitoring=True,
            periodic_system_updates=True,
            data_encryption_in_storage=True,
            data_encryption_in_transit=True,
            vpn_for_remote_access=True,
            cybersecurity_awareness_and_training=True,
            documented_response_plan=True,
            response_plan_update=True,
            operational_recovery_capacity=True,
            credentials_maintenance=True,
            vulnerability_identification=True,
            network_systems_traffic_monitoring=True,
            threat_identification_process=True,
            it_records_presence=True,
            antivirus=True,
            firewall=True,
            intrusion_detection_system=True,
            endpoint_detection_and_response=True,
            it_security_team=True,
            updated_inventory=True,
            backup_maintenance=True,
            risk_prioritization=True,
        )

        # Empresa 3: Americanas S.A.
        americanas = AdvancedCompanyProfile.objects.create(
            name="Americanas S.A.",
            headquarters_country="Brazil",
            headquarters_country_en="Brazil",
            industry_type="retail",
            employee_count=20000,  
            company_size="large",
            remote_work_rate=10.0,  
            global_presence=False,  
            authentication_factors=2,  
            cloud_solution_type='wan',  
            it_system_monitoring=True,
            periodic_system_updates=True,
            data_encryption_in_storage=True,
            data_encryption_in_transit=True,
            vpn_for_remote_access=True,  
            cybersecurity_awareness_and_training=True,  
            documented_response_plan=True,
            response_plan_update=True,
            operational_recovery_capacity=True,
            credentials_maintenance=True,
            vulnerability_identification=True,
            network_systems_traffic_monitoring=True,
            threat_identification_process=True,
            it_records_presence=True,
            antivirus=True,
            firewall=True,
            intrusion_detection_system=True,
            endpoint_detection_and_response=True,
            it_security_team=True,  
            updated_inventory=True,
            backup_maintenance=True,
            risk_prioritization=True,
        )

        # Empresa 4: Bank of America
        bank_of_america = AdvancedCompanyProfile.objects.create(
            name="Bank of America",
            headquarters_country="United States",
            headquarters_country_en="United States",
            industry_type="finance",
            employee_count=208000,  
            company_size="large",
            remote_work_rate=40.0, 
            global_presence=True,  
            authentication_factors=3, 
            cloud_solution_type='wan', 
            it_system_monitoring=True,
            periodic_system_updates=True,
            data_encryption_in_storage=True,
            data_encryption_in_transit=True,
            vpn_for_remote_access=True,  
            cybersecurity_awareness_and_training=True,  
            documented_response_plan=True,
            response_plan_update=True,
            operational_recovery_capacity=True,
            credentials_maintenance=True,
            vulnerability_identification=True,
            network_systems_traffic_monitoring=True,
            threat_identification_process=True,
            it_records_presence=True,
            antivirus=True,
            firewall=True,
            intrusion_detection_system=True,
            endpoint_detection_and_response=True,
            it_security_team=True,
            updated_inventory=True,
            backup_maintenance=True,
            risk_prioritization=True,
        )

        # 4. Criar Históricos de Ataques

        # Históricos de ataques para Amazon
        AttackHistory.objects.create(company=amazon, attack_type=malware, year=2023, count=12)
        AttackHistory.objects.create(company=amazon, attack_type=phishing, year=2023, count=25)
        AttackHistory.objects.create(company=amazon, attack_type=ddos, year=2023, count=8)
        AttackHistory.objects.create(company=amazon, attack_type=breach, year=2023, count=3)

        # Históricos de ataques para Microsoft
        AttackHistory.objects.create(company=microsoft, attack_type=malware, year=2023, count=18)
        AttackHistory.objects.create(company=microsoft, attack_type=phishing, year=2023, count=30)
        AttackHistory.objects.create(company=microsoft, attack_type=ddos, year=2023, count=10)
        AttackHistory.objects.create(company=microsoft, attack_type=breach, year=2023, count=5)

        # Históricos de ataques para Americanas
        AttackHistory.objects.create(company=americanas, attack_type=malware, year=2023, count=10)
        AttackHistory.objects.create(company=americanas, attack_type=phishing, year=2023, count=15)

        # Históricos de ataques para Bank of America
        AttackHistory.objects.create(company=bank_of_america, attack_type=ddos, year=2023, count=5)
        AttackHistory.objects.create(company=bank_of_america, attack_type=breach, year=2023, count=1)

        # 5. Criar Receitas, Gastos de Cibersegurança e Ativos para Empresas Avançadas

        # Amazon
        AnnualRevenue.objects.create(company=amazon, year=2023, amount=Decimal('469820000000.00'))  # Receita anual em USD
        CybersecuritySpending.objects.create(company=amazon, year=2023, amount=Decimal('250000000.00'))  # Gastos estimados
        CompanyAssets.objects.create(company=amazon, item='server', value=Decimal('500000000.00'))
        CompanyAssets.objects.create(company=amazon, item='website', value=Decimal('1000000000.00'))  # E-commerce é um ativo crucial

        # Microsoft
        AnnualRevenue.objects.create(company=microsoft, year=2023, amount=Decimal('198270000000.00'))  # Receita anual em USD
        CybersecuritySpending.objects.create(company=microsoft, year=2023, amount=Decimal('300000000.00'))  # Gastos estimados
        CompanyAssets.objects.create(company=microsoft, item='server', value=Decimal('700000000.00'))
        CompanyAssets.objects.create(company=microsoft, item='database', value=Decimal('1200000000.00'))

        # Americanas S.A.
        AnnualRevenue.objects.create(company=americanas, year=2023, amount=Decimal('19800000000.00'))  # Receita anual em BRL
        CybersecuritySpending.objects.create(company=americanas, year=2023, amount=Decimal('500000.00'))  # Gastos estimados
        CompanyAssets.objects.create(company=americanas, item='server', value=Decimal('15000000.00'))
        CompanyAssets.objects.create(company=americanas, item='website', value=Decimal('80000000.00'))  # E-commerce é um ativo crucial

        # Bank of America
        AnnualRevenue.objects.create(company=bank_of_america, year=2023, amount=Decimal('94000000000.00'))  # Receita anual em USD
        CybersecuritySpending.objects.create(company=bank_of_america, year=2023, amount=Decimal('100000000.00'))  # Gastos significativos
        CompanyAssets.objects.create(company=bank_of_america, item='server', value=Decimal('500000000.00'))
        CompanyAssets.objects.create(company=bank_of_america, item='database', value=Decimal('1000000000.00'))

        # 6. Criar Perfis de Empresas Básicas

        # Empresa 5: National Health Service (NHS)
        nhs = CompanyProfile.objects.create(
            name="National Health Service (NHS)",
            headquarters_country="United Kingdom",
            headquarters_country_en="United Kingdom",
            industry_type="healthcare",
            employee_count=1500000,
            updated_inventory=True,
            backup_maintenance=True,
            risk_prioritization=True,
        )
        AnnualRevenue.objects.create(company=nhs, year=2023, amount=Decimal('150000000000.00'))
        CybersecuritySpending.objects.create(company=nhs, year=2023, amount=Decimal('25000000.00'))
        CompanyAssets.objects.create(company=nhs, item='server', value=Decimal('200000000.00'))
        CompanyAssets.objects.create(company=nhs, item='database', value=Decimal('400000000.00'))

        # Empresa 6: Harvard University
        harvard = CompanyProfile.objects.create(
            name="Harvard University",
            headquarters_country="United States",
            headquarters_country_en="United States",
            industry_type="education",
            employee_count=18000,
            updated_inventory=True,
            backup_maintenance=True,
            risk_prioritization=True,
        )
        AnnualRevenue.objects.create(company=harvard, year=2023, amount=Decimal('5000000000.00'))
        CybersecuritySpending.objects.create(company=harvard, year=2023, amount=Decimal('2000000.00'))
        CompanyAssets.objects.create(company=harvard, item='server', value=Decimal('100000000.00'))
        CompanyAssets.objects.create(company=harvard, item='database', value=Decimal('150000000.00'))

        # Empresa 7: Apple Inc.
        apple = CompanyProfile.objects.create(
            name="Apple Inc.",
            headquarters_country="United States",
            headquarters_country_en="United States",
            industry_type="technology",
            employee_count=147000,
            updated_inventory=True,
            backup_maintenance=True,
            risk_prioritization=True,
        )
        AnnualRevenue.objects.create(company=apple, year=2023, amount=Decimal('274515000000.00'))
        CybersecuritySpending.objects.create(company=apple, year=2023, amount=Decimal('100000000.00'))
        CompanyAssets.objects.create(company=apple, item='server', value=Decimal('300000000.00'))
        CompanyAssets.objects.create(company=apple, item='database', value=Decimal('500000000.00'))

        # Empresa 8: Google LLC
        google = CompanyProfile.objects.create(
            name="Google LLC",
            headquarters_country="United States",
            headquarters_country_en="United States",
            industry_type="technology",
            employee_count=135301,
            updated_inventory=True,
            backup_maintenance=True,
            risk_prioritization=True,
        )
        AnnualRevenue.objects.create(company=google, year=2023, amount=Decimal('181690000000.00'))
        CybersecuritySpending.objects.create(company=google, year=2023, amount=Decimal('150000000.00'))
        CompanyAssets.objects.create(company=google, item='server', value=Decimal('400000000.00'))
        CompanyAssets.objects.create(company=google, item='database', value=Decimal('600000000.00'))

        # Empresas Básicas Regionais

        # APAC - Finance
        apac_finance = CompanyProfile.objects.create(
            name="APAC Finance Corp",
            headquarters_country="Malaysia",
            headquarters_country_en="Malaysia",
            industry_type="finance",
            employee_count=12000,
            updated_inventory=True,
            backup_maintenance=True,
            risk_prioritization=True,
        )
        AnnualRevenue.objects.create(company=apac_finance, year=2023, amount=Decimal('30000000000.00'))
        CybersecuritySpending.objects.create(company=apac_finance, year=2023, amount=Decimal('10000000.00'))
        CompanyAssets.objects.create(company=apac_finance, item='server', value=Decimal('50000000.00'))
        CompanyAssets.objects.create(company=apac_finance, item='database', value=Decimal('90000000.00'))

        # LATAM - Finance
        latam_finance = CompanyProfile.objects.create(
            name="Banrisul",
            headquarters_country="Brazil",
            headquarters_country_en="Brazil",
            industry_type="finance",
            employee_count=15000,
            updated_inventory=True,
            backup_maintenance=True,
            risk_prioritization=True,
        )
        AnnualRevenue.objects.create(company=latam_finance, year=2023, amount=Decimal('25000000000.00'))
        CybersecuritySpending.objects.create(company=latam_finance, year=2023, amount=Decimal('8000000.00'))
        CompanyAssets.objects.create(company=latam_finance, item='server', value=Decimal('60000000.00'))
        CompanyAssets.objects.create(company=latam_finance, item='database', value=Decimal('80000000.00'))

        # EMEA - Retail
        emea_retail = CompanyProfile.objects.create(
            name="ALDI",
            headquarters_country="Germany",
            headquarters_country_en="Germany",
            industry_type="retail",
            employee_count=20000,
            updated_inventory=True,
            backup_maintenance=True,
            risk_prioritization=True,
        )
        AnnualRevenue.objects.create(company=emea_retail, year=2023, amount=Decimal('40000000000.00'))
        CybersecuritySpending.objects.create(company=emea_retail, year=2023, amount=Decimal('15000000.00'))
        CompanyAssets.objects.create(company=emea_retail, item='server', value=Decimal('80000000.00'))
        CompanyAssets.objects.create(company=emea_retail, item='website', value=Decimal('150000000.00'))

        # NA - Retail
        na_retail = CompanyProfile.objects.create(
            name="Walmart Inc. NA",
            headquarters_country="United States",
            headquarters_country_en="United States",
            industry_type="retail",
            employee_count=25000,
            updated_inventory=True,
            backup_maintenance=True,
            risk_prioritization=True,
        )
        AnnualRevenue.objects.create(company=na_retail, year=2023, amount=Decimal('55000000000.00'))
        CybersecuritySpending.objects.create(company=na_retail, year=2023, amount=Decimal('20000000.00'))
        CompanyAssets.objects.create(company=na_retail, item='server', value=Decimal('100000000.00'))
        CompanyAssets.objects.create(company=na_retail, item='website', value=Decimal('175000000.00'))

        self.stdout.write(self.style.SUCCESS("Banco de dados populado com empresas do mundo real com sucesso!"))

        ##### Empresas de exemplo com menos proteçoes #####

        # Empresa 1: Startup Tech Solutions
        startup_tech = AdvancedCompanyProfile.objects.create(
            name="Startup Tech Solutions",
            headquarters_country="Brazil",
            headquarters_country_en="Brazil",
            industry_type="technology",
            employee_count=50,  # Empresa de pequeno porte
            company_size="small",
            remote_work_rate=80.0,  # Alta taxa de trabalho remoto
            global_presence=False,  # Presença global limitada
            authentication_factors=1,  # Apenas uma camada de autenticação
            cloud_solution_type='lan',  # Solução de nuvem local
            it_system_monitoring=False,  # Não possui monitoramento de sistemas de TI
            periodic_system_updates=True,  # Realiza atualizações periódicas
            data_encryption_in_storage=False,  # Não possui criptografia de dados em armazenamento
            data_encryption_in_transit=True,  # Criptografia em trânsito apenas
            vpn_for_remote_access=True,  # Usa VPN para acesso remoto
            cybersecurity_awareness_and_training=False,  # Sem treinamento de segurança cibernética
            documented_response_plan=False,  # Plano de resposta não documentado
            response_plan_update=False,  # Plano de resposta não atualizado regularmente
            operational_recovery_capacity=False,  # Capacidade de recuperação operacional limitada
            credentials_maintenance=True,  # Manutenção regular de credenciais
            vulnerability_identification=False,  # Não possui identificação de vulnerabilidades
            network_systems_traffic_monitoring=False,  # Não monitora tráfego de sistemas de rede
            threat_identification_process=False,  # Processo de identificação de ameaças ausente
            it_records_presence=False,  # Não mantém registros de TI
            antivirus=True,  # Possui antivírus
            firewall=True,  # Possui firewall
            intrusion_detection_system=False,  # Sem sistema de detecção de intrusões
            endpoint_detection_and_response=False,  # Sem EDR
            it_security_team=False,  # Sem equipe de segurança de TI dedicada
        )

        # Receita, Gastos e Ativos para Startup Tech Solutions
        AnnualRevenue.objects.create(company=startup_tech, year=2023, amount=Decimal('5000000.00'))  # Receita anual em BRL
        CybersecuritySpending.objects.create(company=startup_tech, year=2023, amount=Decimal('5000.00'))  # Gastos em cibersegurança
        CompanyAssets.objects.create(company=startup_tech, item='server', value=Decimal('200000.00'))
        CompanyAssets.objects.create(company=startup_tech, item='database', value=Decimal('500000.00'))

        # Histórico de Ataques para Startup Tech Solutions
        AttackHistory.objects.create(company=startup_tech, attack_type=malware, year=2023, count=20)
        AttackHistory.objects.create(company=startup_tech, attack_type=phishing, year=2023, count=50)
        AttackHistory.objects.create(company=startup_tech, attack_type=ddos, year=2023, count=10)

        # Empresa 2: Small Finance Corp
        small_finance = AdvancedCompanyProfile.objects.create(
            name="Small Finance Corp",
            headquarters_country="United States",
            headquarters_country_en="United States",
            industry_type="finance",
            employee_count=150,  # Empresa de porte médio
            company_size="medium",
            remote_work_rate=50.0,  # Metade dos funcionários trabalha remotamente
            global_presence=False,  # Presença global limitada
            authentication_factors=2,  # Dois fatores de autenticação
            cloud_solution_type='wan',  # Solução de nuvem de área ampla
            it_system_monitoring=True,  # Possui monitoramento de sistemas de TI
            periodic_system_updates=True,  # Realiza atualizações periódicas
            data_encryption_in_storage=False,  # Não possui criptografia de dados em armazenamento
            data_encryption_in_transit=True,  # Criptografia em trânsito
            vpn_for_remote_access=True,  # Usa VPN para acesso remoto
            cybersecurity_awareness_and_training=False,  # Sem treinamento de segurança cibernética
            documented_response_plan=True,  # Plano de resposta documentado
            response_plan_update=False,  # Plano de resposta não atualizado regularmente
            operational_recovery_capacity=False,  # Capacidade de recuperação operacional limitada
            credentials_maintenance=True,  # Manutenção regular de credenciais
            vulnerability_identification=True,  # Identificação de vulnerabilidades implementada
            network_systems_traffic_monitoring=False,  # Não monitora tráfego de sistemas de rede
            threat_identification_process=False,  # Processo de identificação de ameaças ausente
            it_records_presence=True,  # Mantém registros de TI
            antivirus=True,  # Possui antivírus
            firewall=True,  # Possui firewall
            intrusion_detection_system=False,  # Sem sistema de detecção de intrusões
            endpoint_detection_and_response=False,  # Sem EDR
            it_security_team=True,  # Possui uma pequena equipe de segurança de TI
        )

        # Receita, Gastos e Ativos para Small Finance Corp
        AnnualRevenue.objects.create(company=small_finance, year=2023, amount=Decimal('10000000.00'))  # Receita anual em USD
        CybersecuritySpending.objects.create(company=small_finance, year=2023, amount=Decimal('10000.00'))  # Gastos em cibersegurança
        CompanyAssets.objects.create(company=small_finance, item='server', value=Decimal('300000.00'))
        CompanyAssets.objects.create(company=small_finance, item='database', value=Decimal('700000.00'))

        # Histórico de Ataques para Small Finance Corp
        AttackHistory.objects.create(company=small_finance, attack_type=malware, year=2023, count=15)
        AttackHistory.objects.create(company=small_finance, attack_type=phishing, year=2023, count=40)
        AttackHistory.objects.create(company=small_finance, attack_type=ddos, year=2023, count=5)

        # Empresa 3: Regional Retail Group
        regional_retail = AdvancedCompanyProfile.objects.create(
            name="Regional Retail Group",
            headquarters_country="Brazil",
            headquarters_country_en="Brazil",
            industry_type="retail",
            employee_count=300,  # Empresa de porte médio
            company_size="medium",
            remote_work_rate=20.0,  # Pequena parte dos funcionários trabalha remotamente
            global_presence=False,  # Presença global limitada
            authentication_factors=1,  # Apenas uma camada de autenticação
            cloud_solution_type='lan',  # Solução de nuvem local
            it_system_monitoring=False,  # Não possui monitoramento de sistemas de TI
            periodic_system_updates=False,  # Não realiza atualizações periódicas
            data_encryption_in_storage=False,  # Não possui criptografia de dados em armazenamento
            data_encryption_in_transit=False,  # Sem criptografia de dados em trânsito
            vpn_for_remote_access=False,  # Não usa VPN para acesso remoto
            cybersecurity_awareness_and_training=False,  # Sem treinamento de segurança cibernética
            documented_response_plan=False,  # Plano de resposta não documentado
            response_plan_update=False,  # Plano de resposta não atualizado regularmente
            operational_recovery_capacity=False,  # Capacidade de recuperação operacional limitada
            credentials_maintenance=False,  # Não realiza manutenção regular de credenciais
            vulnerability_identification=False,  # Não possui identificação de vulnerabilidades
            network_systems_traffic_monitoring=False,  # Não monitora tráfego de sistemas de rede
            threat_identification_process=False,  # Processo de identificação de ameaças ausente
            it_records_presence=False,  # Não mantém registros de TI
            antivirus=True,  # Possui antivírus básico
            firewall=True,  # Possui firewall básico
            intrusion_detection_system=False,  # Sem sistema de detecção de intrusões
            endpoint_detection_and_response=False,  # Sem EDR
            it_security_team=False,  # Sem equipe de segurança de TI dedicada
        )

        # Receita, Gastos e Ativos para Regional Retail Group
        AnnualRevenue.objects.create(company=regional_retail, year=2023, amount=Decimal('20000000.00'))  # Receita anual em BRL
        CybersecuritySpending.objects.create(company=regional_retail, year=2023, amount=Decimal('8000.00'))  # Gastos em cibersegurança
        CompanyAssets.objects.create(company=regional_retail, item='server', value=Decimal('150000.00'))
        CompanyAssets.objects.create(company=regional_retail, item='website', value=Decimal('300000.00'))

        # Histórico de Ataques para Regional Retail Group
        AttackHistory.objects.create(company=regional_retail, attack_type=malware, year=2023, count=25)
        AttackHistory.objects.create(company=regional_retail, attack_type=phishing, year=2023, count=60)
        AttackHistory.objects.create(company=regional_retail, attack_type=ddos, year=2023, count=15)


        self.stdout.write(self.style.SUCCESS("Banco de dados populado com empresas fictícias de menor porte com sucesso!"))
