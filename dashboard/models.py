from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxLengthValidator, RegexValidator, MaxValueValidator
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .utils import translate_country_to_english


class CompanyProfile(models.Model):
    INDUSTRY_CHOICES = [
        ('healthcare', _('Healthcare')),
        ('government', _('Government')),
        ('retail', _('Retail')),
        ('finance', _('Finance')),
        ('education', _('Education')),
        ('entertainment', _('Entertainment')),
        ('technology', _('Technology')),
        ('others', _('Others')),
    ]

    name = models.CharField(
        _("Name"),
        max_length=255,
        help_text=_("Enter the full legal name of the company.")
    )

    headquarters_country = models.CharField(
        _("Headquarters Country"),
        max_length=255,
        help_text=_("Specify the country where the company's main headquarters is located.")
    )

    headquarters_country_en = models.CharField(
        _("Headquarters Country (English)"),
        max_length=255,
        editable=False
    )

    industry_type = models.CharField(
        _("Industry Type"),
        max_length=20,
        choices=INDUSTRY_CHOICES,
        default='others',
        help_text=_("Select the primary industry or sector in which the company operates.")
    )

    employee_count = models.PositiveIntegerField(
        _("Employee Count"),
        validators=[MinValueValidator(1)],
        help_text=_("Enter the total number of individuals employed by the company.")
    )

    updated_inventory = models.BooleanField(
        _("Updated Inventory"),
        default=False,
        help_text=_("Check this box if the company maintains an up-to-date inventory of all assets.")
    )

    backup_maintenance = models.BooleanField(
        _("Backup Maintenance"),
        default=False,
        help_text=_("Check this box if the company maintains regular backups of critical data.")
    )

    risk_prioritization = models.BooleanField(
        _("Risk Prioritization"),
        default=False,
        help_text=_("Check this box if the company actively prioritizes risks based on their potential impact and likelihood.")
    )

    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Data de Criação"),
        help_text=_("Data e hora de criação do registro")
    )

    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Data de Atualização"),
        help_text=_("Data e hora da última atualização do registro")
    )

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Traduz o nome do país para inglês
        self.headquarters_country_en = translate_country_to_english(self.headquarters_country)
        super().save(*args, **kwargs)
        
    def to_dict(self):
        return {
            'name': self.name,
            'headquarters_country': self.headquarters_country_en,  
            'industry_type': self.industry_type,
            'employee_count': self.employee_count,
            'updated_inventory': self.updated_inventory,
            'backup_maintenance': self.backup_maintenance,
            'risk_prioritization': self.risk_prioritization,
        }

    class Meta:
        verbose_name = _("Company Profile")
        verbose_name_plural = _("Company Profiles")


class AnnualRevenue(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='annual_revenues')
    year = models.PositiveIntegerField(_("Year"))
    amount = models.DecimalField(_("Annual Revenue"), max_digits=14, decimal_places=2)

    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Data de Criação"),
        help_text=_("Data e hora de criação do registro")
    )

    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Data de Atualização"),
        help_text=_("Data e hora da última atualização do registro")
    )

    class Meta:
        unique_together = ('company', 'year')
        verbose_name = _("Annual Revenue")
        verbose_name_plural = _("Annual Revenues")

    def __str__(self):
        return f"{self.company.name} - {self.year}: {self.amount}"

    def to_dict(self):
        return {
            'company': self.company.name,
            'year': self.year,
            'amount': str(self.amount),
        }

class CybersecuritySpending(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='cybersecurity_spendings')
    year = models.PositiveIntegerField(_("Year"))
    amount = models.DecimalField(_("Cybersecurity Spending"), max_digits=14, decimal_places=2)

    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Data de Criação"),
        help_text=_("Data e hora de criação do registro")
    )

    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Data de Atualização"),
        help_text=_("Data e hora da última atualização do registro")
    )

    class Meta:
        unique_together = ('company', 'year')
        verbose_name = _("Cybersecurity Spending")
        verbose_name_plural = _("Cybersecurity Spendings")

    def __str__(self):
        return f"{self.company.name} - {self.year}: {self.amount}"
    
    def to_dict(self):
        return {
            'company': self.company.name,
            'year': self.year,
            'amount': str(self.amount),  # Convert Decimal to string
            'data_criacao': self.data_criacao,
            'data_atualizacao': self.data_atualizacao,
        }


class CompanyAssets(models.Model):
    SERVER = 'server'
    DATABASE = 'database'
    WEBSITE = 'website'
    OTHER = 'other'

    ITEM_CHOICES = [
        (SERVER, _("Server")),
        (DATABASE, _("Database")),
        (WEBSITE, _("Website")),
        (OTHER, _("Other")),
    ]

    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='company_assets')
    item = models.CharField(_("Item"), max_length=255, choices=ITEM_CHOICES)
    value = models.DecimalField(_("Value"), max_digits=14, decimal_places=2)

    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Data de Criação"),
        help_text=_("Data e hora de criação do registro")
    )

    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Data de Atualização"),
        help_text=_("Data e hora da última atualização do registro")
    )

    class Meta:
        unique_together = ('company', 'item')
        verbose_name = _("Company Asset")
        verbose_name_plural = _("Company Assets")

    def __str__(self):
        return f"{self.company.name} - {self.item}: {self.value}"
    
    def to_dict(self):
        return {
            'company': self.company.name,
            'item': self.item,
            'value': str(self.value),  # Convert Decimal to string
            'data_criacao': self.data_criacao,
            'data_atualizacao': self.data_atualizacao,
        }

######################################
# Simulacoes econômicas Sandbox
######################################

class SandboxCompany(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='sandbox_profile')
    is_on = models.BooleanField(default = False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='SandboxCompany',
        verbose_name=_("User"),
        default = 0
    )

class SandboxAsset(models.Model):
    MALWARE = 'Malware'
    PHISHING = 'Phishing'
    DDOS = 'DDoS'
    GERAL = 'Geral'

    ITEM_CHOICES = [
        (MALWARE, _("Malware")),
        (PHISHING, _("Phishing")),
        (DDOS, _("DDoS")),
        (GERAL, _("Geral")),
    ]

    sandbox_company = models.ForeignKey(SandboxCompany, on_delete=models.CASCADE, related_name='sandbox_profile')
    asset = models.ForeignKey(CompanyAssets, on_delete=models.CASCADE, related_name='company_assets')
    grafico = models.CharField(_("Name"), max_length=255, choices=ITEM_CHOICES, default = GERAL)
    alpha = models.DecimalField(_("alpha"), max_digits=14, decimal_places=8, default = 0.001)
    saved_alpha = models.DecimalField(_("alpha"), max_digits=14, decimal_places=8, default = 0.001)

class SandboxAttack(models.Model):
    MALWARE = 'Malware'
    PHISHING = 'Phishing'
    DDOS = 'DDoS'
    GERAL = 'Geral'

    ITEM_CHOICES = [
        (MALWARE, _("Malware")),
        (PHISHING, _("Phishing")),
        (DDOS, _("DDoS")),
        (GERAL, _("Geral")),
    ]

    IMPACT_CHOICES = [
        ("Alto", _("Alto")),
        ("Medio", _("Medio")),
        ("Baixo", _("Baixo")),
    ]

    impact_direct = models.CharField(_("Direct_impact"), max_length=255, choices=IMPACT_CHOICES, default = "Medio")
    impact_indirect = models.CharField(_("Indirect_impact"), max_length=255, choices=IMPACT_CHOICES, default = "Medio")

    asset = models.ForeignKey(SandboxAsset, on_delete=models.CASCADE, related_name='sandbox_asset')
    name = models.CharField(_("Name"), max_length=255, choices=ITEM_CHOICES, default = '')
    value = models.IntegerField(_("Value"), default = 0)
    prob = models.DecimalField(_("Prob"), max_digits=14, decimal_places=4, default = 0)
    invest = models.IntegerField(_("Invested"), default = 0)

    save_value = models.IntegerField(_("Saved Value"), default = 0)
    save_prob = models.DecimalField(_("Saved Prob"), max_digits=14, decimal_places=4, default = 0)
    save_invest = models.IntegerField(_("Saved Invested"), default = 0)




######################################
# company profile avançado
######################################

class Region(models.Model):
    CONTINENT_CHOICES = [
        ('europe', _('Europe')),
        ('south_america', _('South America')),
        ('north_america', _('North America')),
        ('africa', _('Africa')),
        ('asia', _('Asia')),
        ('oceania', _('Oceania')),
    ]
    
    name = models.CharField(
        max_length=255, 
        verbose_name=_("Region"), 
        help_text=_("Enter the name of the region. Example: 'Brazil', 'Europe'")
    )
    type = models.CharField(
        max_length=10, 
        choices=[('continent', _('Continent')), ('country', _('Country'))], 
        help_text=_("Select whether this region is a continent or a country")
    )
    continent = models.CharField(
        max_length=20, 
        choices=CONTINENT_CHOICES, 
        null=True, 
        blank=True, 
        help_text=_("If this region is a country, select the continent it belongs to. Example: 'Brazil' -> 'South America'")
    )

    class Meta:
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")
        unique_together = ('name', 'type', 'continent')  # Adiciona unicidade para nome, tipo e continente

    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"

class AdvancedCompanyProfile(CompanyProfile):
    SIZE_CHOICES = [
        ('small', _('Small')),
        ('medium', _('Medium')),
        ('large', _('Large')),
    ]

    CLOUD_SOLUTION_CHOICES = [
        ('lan', _('LAN')),
        ('wan', _('WAN')),
        ('none', _('None')),
    ]

    # Business Dimension
    '''
    company_locations = models.ManyToManyField(
        Region, 
        related_name='companies', 
        verbose_name=_('Company Locations'), 
        help_text=_("Select the regions where the company operates. Example: 'Brazil', 'United States', 'Europe'")
    )
    '''
    company_size = models.CharField(
        _('Company Size'), 
        max_length=10, 
        choices=SIZE_CHOICES, 
        help_text=_("Select the size of the company. Example: 'Small' (less than 50 employees), 'Medium' (50-250 employees), 'Large' (more than 250 employees)")
    )
    remote_work_rate = models.FloatField(
        _('Remote Work Rate'), 
        help_text=_('Enter the percentage of employees working remotely. Example: 20.5 for 20.5%')
    )
    global_presence = models.BooleanField(
        _('Global Presence'), 
        default=False, 
        help_text=_("Indicate whether the company has a global presence or not")
    )

    # Technical Dimension
    authentication_factors = models.PositiveIntegerField(
        _('Authentication Factors'), 
        help_text=_("Enter the number of authentication factors used by the company. Example: 2 for two-factor authentication (2FA)")
    )
    cloud_solution_type = models.CharField(
        _('Cloud Solution Type'), 
        max_length=20, 
        choices=CLOUD_SOLUTION_CHOICES, 
        help_text=_("Select the type of cloud solution used by the company. Example: 'LAN' for local area network, 'WAN' for wide area network, 'None' if no cloud solution is used")
    )
    it_system_monitoring = models.BooleanField(
        _('IT System Monitoring'), 
        default=False, 
        help_text=_("Indicate whether the company has IT system monitoring in place")
    )
    periodic_system_updates = models.BooleanField(
        _('Periodic System Updates'), 
        default=False, 
        help_text=_("Indicate whether the company performs periodic system updates")
    )
    data_encryption_in_storage = models.BooleanField(
        _('Data Encryption in Storage'), 
        default=False, 
        help_text=_("Indicate whether the company encrypts data at rest (in storage)")
    )
    data_encryption_in_transit = models.BooleanField(
        _('Data Encryption in Transit'), 
        default=False, 
        help_text=_("Indicate whether the company encrypts data in transit (during transmission)")
    )
    vpn_for_remote_access = models.BooleanField(
        _('VPN for Remote Access'), 
        default=False, 
        help_text=_("Indicate whether the company uses a VPN for remote access")
    )
    cybersecurity_awareness_and_training = models.BooleanField(
        _('Cybersecurity Awareness and Training'), 
        default=False, 
        help_text=_("Indicate whether the company provides cybersecurity awareness and training")
    )
    documented_response_plan = models.BooleanField(
        _('Documented Response Plan'), 
        default=False, 
        help_text=_("Indicate whether the company has a documented response plan")
    )
    response_plan_update = models.BooleanField(
        _('Response Plan Update'), 
        default=False, 
        help_text=_("Indicate whether the company regularly updates its response plan")
    )
    operational_recovery_capacity = models.BooleanField(
        _('Operational Recovery Capacity'), 
        default=False, 
        help_text=_("Indicate whether the company has operational recovery capacity")
    )
    credentials_maintenance = models.BooleanField(
        _('Credentials Maintenance'), 
        default=False, 
        help_text=_("Indicate whether the company performs regular credentials maintenance")
    )
    vulnerability_identification = models.BooleanField(
        _('Vulnerability Identification'), 
        default=False, 
        help_text=_("Indicate whether the company has a process for identifying vulnerabilities")
    )
    network_systems_traffic_monitoring = models.BooleanField(
        _('Network Systems Traffic Monitoring'), 
        default=False, 
        help_text=_("Indicate whether the company monitors network systems traffic")
    )
    threat_identification_process = models.BooleanField(
        _('Threat Identification Process'), 
        default=False, 
        help_text=_("Indicate whether the company has a process for identifying threats")
    )
    it_records_presence = models.BooleanField(
        _('IT Records Presence'), 
        default=False, 
        help_text=_("Indicate whether the company maintains IT records")
    )
    antivirus = models.BooleanField(
        _('Antivirus'), 
        default=False, 
        help_text=_("Indicate whether the company uses antivirus software")
    )
    firewall = models.BooleanField(
        _('Firewall'), 
        default=False, 
        help_text=_("Indicate whether the company uses a firewall")
    )
    intrusion_detection_system = models.BooleanField(
        _('Intrusion Detection System (IDS)'), 
        default=False, 
        help_text=_("Indicate whether the company uses an intrusion detection system (IDS)")
    )
    endpoint_detection_and_response = models.BooleanField(
        _('Endpoint Detection and Response (EDR)'), 
        default=False, 
        help_text=_("Indicate whether the company uses an endpoint detection and response (EDR) system")
    )
    it_security_team = models.BooleanField(
        _('IT Security Team'), 
        default=False, 
        help_text=_("Indicate whether the company has a dedicated IT security team")
    )

    class Meta:
        verbose_name = _('Advanced Company Profile')
        verbose_name_plural = _('Advanced Company Profiles')

    def to_dict(self):
        return {
            'name': self.name,
            'headquarters_country': self.headquarters_country,
            'industry_type': self.industry_type,
            'employee_count': self.employee_count,
            'company_size': self.company_size,
            'remote_work_rate': self.remote_work_rate,
            'global_presence': self.global_presence,
            'authentication_factors': self.authentication_factors,
            'cloud_solution_type': self.cloud_solution_type,
            'it_system_monitoring': self.it_system_monitoring,
            'periodic_system_updates': self.periodic_system_updates,
            'data_encryption_in_storage': self.data_encryption_in_storage,
            'data_encryption_in_transit': self.data_encryption_in_transit,
            'vpn_for_remote_access': self.vpn_for_remote_access,
            'cybersecurity_awareness_and_training': self.cybersecurity_awareness_and_training,
            'documented_response_plan': self.documented_response_plan,
            'response_plan_update': self.response_plan_update,
            'operational_recovery_capacity': self.operational_recovery_capacity,
            'credentials_maintenance': self.credentials_maintenance,
            'vulnerability_identification': self.vulnerability_identification,
            'network_systems_traffic_monitoring': self.network_systems_traffic_monitoring,
            'threat_identification_process': self.threat_identification_process,
            'it_records_presence': self.it_records_presence,
            'antivirus': self.antivirus,
            'firewall': self.firewall,
            'intrusion_detection_system': self.intrusion_detection_system,
            'endpoint_detection_and_response': self.endpoint_detection_and_response,
            'it_security_team': self.it_security_team,
        }
    def get_cybersecurity_measures(self):
        return {
            'it_system_monitoring': self.it_system_monitoring,
            'periodic_system_updates': self.periodic_system_updates,
            'data_encryption_in_storage': self.data_encryption_in_storage,
            'data_encryption_in_transit': self.data_encryption_in_transit,
            'vpn_for_remote_access': self.vpn_for_remote_access,
            'cybersecurity_awareness_and_training': self.cybersecurity_awareness_and_training,
            'documented_response_plan': self.documented_response_plan,
            'response_plan_update': self.response_plan_update,
            'operational_recovery_capacity': self.operational_recovery_capacity,
            'credentials_maintenance': self.credentials_maintenance,
            'vulnerability_identification': self.vulnerability_identification,
            'network_systems_traffic_monitoring': self.network_systems_traffic_monitoring,
            'threat_identification_process': self.threat_identification_process,
            'it_records_presence': self.it_records_presence,
            'antivirus': self.antivirus,
            'firewall': self.firewall,
            'intrusion_detection_system': self.intrusion_detection_system,
            'endpoint_detection_and_response': self.endpoint_detection_and_response,
            'it_security_team': self.it_security_team,
        }
    
    def get_relevant_fields(self):
        """Retorna os campos relevantes para cada setor de indústria"""
        # Campos básicos comuns para cada indústria
        base_fields = [
            ('firewall', _("Firewall")),
            ('antivirus', _("Antivirus")),
            ('periodic_system_updates', _("Periodic System Updates"))
        ]

        industry_specific = {
            'healthcare': [
                ('data_encryption_in_storage', _("Data Encryption in Storage")),
                ('data_encryption_in_transit', _("Data Encryption in Transit")),
                ('credentials_maintenance', _("Credentials Maintenance")),
                ('operational_recovery_capacity', _("Operational Recovery Capacity"))
            ],
            'finance': [
                ('intrusion_detection_system', _("Intrusion Detection System (IDS)")),
                ('endpoint_detection_and_response', _("Endpoint Detection and Response (EDR)")),
                ('network_systems_traffic_monitoring', _("Network Systems Traffic Monitoring")),
                ('it_security_team', _("IT Security Team"))
            ],
            'government': [
                ('vpn_for_remote_access', _("VPN for Remote Access")),
                ('documented_response_plan', _("Documented Response Plan")),
                ('threat_identification_process', _("Threat Identification Process")),
                ('cybersecurity_awareness_and_training', _("Cybersecurity Awareness and Training"))
            ],
            'retail': [
                ('data_encryption_in_transit', _("Data Encryption in Transit")),
                ('vulnerability_identification', _("Vulnerability Identification")),
                ('network_systems_traffic_monitoring', _("Network Systems Traffic Monitoring")),
                ('it_system_monitoring', _("IT System Monitoring"))
            ],
            'technology': [
                ('endpoint_detection_and_response', _("Endpoint Detection and Response (EDR)")),
                ('it_security_team', _("IT Security Team")),
                ('threat_identification_process', _("Threat Identification Process")),
                ('vulnerability_identification', _("Vulnerability Identification"))
            ]
        }

        # Retorna os campos específicos de cada setor
        specific_fields = industry_specific.get(self.industry_type, [])
        
        # Junta os campos básicos com os específicos
        return base_fields + specific_fields

class AttackType(models.Model):
    ATTACK_CHOICES = [
        ('malware', _('Malware')),
        ('phishing', _('Phishing')),
        ('ddos', _('DDoS')),
        ('breach', _('Breach')),
    ]

    attack_type = models.CharField(
        _('Attack Type'), 
        max_length=20, 
        choices=ATTACK_CHOICES, 
        help_text=_("Select the type of attack. Example: 'Malware', 'Phishing', 'DDoS', 'Breach'")
    )

    class Meta:
        verbose_name = _('Attack Type')
        verbose_name_plural = _('Attack Types')

    def __str__(self):
        return self.get_attack_type_display()
    
    def to_dict(self):
        return {
            'attack_type': self.get_attack_type_display(),
        }

class AttackHistory(models.Model):
    company = models.ForeignKey(
        AdvancedCompanyProfile, 
        on_delete=models.CASCADE, 
        related_name='attack_histories', 
        help_text=_("Select the company for which the attack history is being recorded")
    )
    attack_type = models.ForeignKey(
        AttackType, 
        on_delete=models.CASCADE, 
        related_name='attack_histories', 
        help_text=_("Select the type of attack. Example: 'Malware', 'Phishing', 'DDoS', 'Breach'")
    )
    year = models.PositiveIntegerField(
        _('Year'), 
        help_text=_("Enter the year in which the attack occurred. Example: 2023")
    )
    count = models.PositiveIntegerField(
        _('Count'), 
        default=1, 
        help_text=_("Enter the number of attacks of this type that occurred in the specified year. Example: 3")
    )

    class Meta:
        unique_together = ('company', 'attack_type', 'year')
        verbose_name = _('Attack History')
        verbose_name_plural = _('Attack Histories')

    def __str__(self):
        return f"{self.company.name} - {self.attack_type} - {self.year}: {self.count}"
    
    def to_dict(self):
        return {
            'company': self.company.name,
            'attack_type': self.attack_type.get_attack_type_display(),
            'year': self.year,
            'count': self.count,
        }


class RiskAndEconomic(models.Model):

    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE, 
        related_name='risks_and_economics',
    )
    company_profile_type = models.BooleanField(
        _('Profile Type of a Company'), 
        default=False, 
        help_text=_("Enter the company's profile type")
    )
    final_score = models.FloatField(
        _('Final Score'), 
        help_text=_('Enter the final score'),
        default=0,
        null=True,
        blank=True
    )
    text_score = models.CharField(
         _('Text Score'), 
        max_length=64, 
        help_text=_("Write the text score"),
        blank=True
    )
    malware_region_value = models.FloatField(
        _('Region Value'), 
        help_text=_('Enter the malware region value'),
        default=0,
        null=True,
        blank=True
    )
    malware_sector_value = models.FloatField(
        _('Sector Value'), 
        help_text=_('Enter the malware sector value'),
        default=0,
        null=True,
        blank=True
    )
    malware_resilience_value = models.FloatField(
        _('Resilience Value'), 
        help_text=_('Enter the malware resilience value'),
        default=0,
        null=True,
        blank=True
    )
    malware_final_score = models.FloatField(
        _('Malware Final Score'), 
        help_text=_('Enter the malware final score'),
        default=0,
        null=True,
        blank=True
    )
    phishing_region_value = models.FloatField(
        _('Region Value'), 
        help_text=_('Enter the phishing region value'),
        default=0,
        null=True,
        blank=True
    )
    phishing_sector_value = models.FloatField(
        _('Sector Value'), 
        help_text=_('Enter the phishing sector value'),
        default=0,
        null=True,
        blank=True
    )
    phishing_resilience_value = models.FloatField(
        _('Resilience Value'), 
        help_text=_('Enter the phishing resilience value'),
        default=0,
        null=True,
        blank=True
    )
    phishing_final_score = models.FloatField(
        _('Phishing Final Score'), 
        help_text=_('Enter the phishing final score'),
        default=0,
        null=True,
        blank=True
    )
    ddos_region_value = models.FloatField(
        _('Region Value'), 
        help_text=_('Enter the DDoS region value'),
        default=0,
        null=True,
        blank=True
    )
    ddos_sector_value = models.FloatField(
        _('Sector Value'), 
        help_text=_('Enter the DDoS sector value'),
        default=0,
        null=True,
        blank=True
    )
    ddos_resilience_value = models.FloatField(
        _('Resilience Value'), 
        help_text=_('Enter the DDoS resilience value'),
        default=0,
        null=True,
        blank=True
    )
    ddos_final_score = models.FloatField(
        _('DDoS Final Score'), 
        help_text=_('Enter the DDoS final score'),
        default=0,
        null=True,
        blank=True
    )
    insights_pos = models.JSONField(
        _('Insights Positivos'), 
        default=list,
        blank=True
    )
    insights_neg = models.JSONField(
        _('Insights Negativos'), 
        default=list,
        blank=True
    )
    malware_succ = models.FloatField(
        _('Malware Success Rate'), 
        help_text=_('Enter the malware success rate'),
        null=True,
        blank=True
    )
    phishing_succ = models.FloatField(
        _('Phishing Success Rate'), 
        help_text=_('Enter the phishing success rate'),
        null=True,
        blank=True
    )
    ddos_succ = models.FloatField(
        _('DDoS Success Rate'), 
        help_text=_('Enter the ddos success rate'),
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.company.name}"
    
    def to_dict(self):
        return {
            'company': self.company.name,
            'final_score': self.final_score,
            'text_score': self.text_score,
            'insights_pos': self.insights_pos,
            'insights_neg': self.insights_neg,
            'malware_succ': self.malware_succ,
            'phishing_succ': self.phishing_succ,
            'ddos_att_succ': self.ddos_succ
        }
    
######################################
# cópias de usuário das empresas
######################################

class UserCompanyCopy(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='company_copies',
        verbose_name=_("User")
    )
    original_company = models.ForeignKey(
        'CompanyProfile', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='user_copies',
        verbose_name=_("Original Company Profile")
    )
    
    # Usando GenericForeignKey para permitir tanto CompanyProfile quanto AdvancedCompanyProfile
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    copied_company = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = _("User Company Copy")
        verbose_name_plural = _("User Company Copies")
        unique_together = ['user', 'original_company']

    def __str__(self):
        return f"Copy of {self.original_company.name} for {self.user.username}"
     

######################################
# modelagem dos reports
######################################


class Scope(models.Model):
    SCOPE_CHOICES = [
        ('malware', _('Malware')),
        ('phishing', _('Phishing')),
        ('ddos', _('DDoS')),
        ('breach', _('Breach')),
    ]
    name = models.CharField(max_length=255, choices=SCOPE_CHOICES, verbose_name=_("Escopo"))

    class Meta:
        verbose_name = _("Escopo")
        verbose_name_plural = _("Escopos")

    def __str__(self):
        return self.get_name_display()

class Sector(models.Model):
    SECTOR_CHOICES = [
        ('healthcare', _('Healthcare')),
        ('government', _('Government')),
        ('retail', _('Retail')),
        ('finance', _('Finance')),
        ('education', _('Education')),
        ('entertainment', _('Entertainment')),
        ('technology', _('Technology')),
        ('others', _('Others')),
    ]
    name = models.CharField(max_length=255, choices=SECTOR_CHOICES, verbose_name=_("Setor"))

    class Meta:
        verbose_name = _("Setor")
        verbose_name_plural = _("Setores")

    def __str__(self):
        return self.get_name_display()

class Report(models.Model):
    PARTICIPANT_PROFILE_CHOICES = [
        ('real_devices', _('Real-world devices')),
        ('real_cases', _('Real-world cases')),
        ('experts', _('Experts')),
        ('organizations', _('Organizations')),
        ('others', _('Others')),  # Adicionada opção "Others"
    ]

    name = models.CharField(max_length=255, verbose_name=_("Nome do Report"))
    year = models.IntegerField(verbose_name=_("Ano"))
    years_covered = models.CharField(max_length=255, verbose_name=_("Anos Cobertos"))
    company = models.CharField(max_length=255, verbose_name=_("Empresa"))
    number_of_participants = models.IntegerField(null=True, blank=True, verbose_name=_("Número de Participantes"))
    participant_profiles = models.CharField(
        max_length=255, 
        choices=PARTICIPANT_PROFILE_CHOICES, 
        default='others',  # Valor padrão definido como 'others'
        verbose_name=_("Perfil dos Participantes")
    )
    scopes = models.ManyToManyField(Scope, verbose_name=_("Escopos"))
    regions = models.ManyToManyField(Region, blank=True, verbose_name=_("Regiões Específicas"))
    sectors = models.ManyToManyField(Sector, blank=True, verbose_name=_("Setores"))

    class Meta:
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")
        ordering = ['-year']

    def __str__(self):
        return f"{self.name} ({self.year})"

class CyberSecurityData(models.Model):
    prob_a_priori = models.CharField(
        max_length=255,
        verbose_name=_("Probabilidade A Priori"),
        help_text=_("Tipo de ameaça ou evento de segurança"),
    )

    prob_marginal = models.CharField(
        max_length=255,
        verbose_name=_("Probabilidade Marginal"),
        help_text=_("Contexto ou localização da ameaça"),
    )

    p_a_given_b = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("P(A|B)"),
        help_text=_("Probabilidade condicional de A dado B"),
    )

    c = models.CharField(
        max_length=255,
        verbose_name=_("C"),
        help_text=_("Descrição ou contexto adicional relacionado ao dado de cibersegurança"),
        null=True,
        blank=True
    )

    p_c_given_p_a_given_b = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("P(C|P(A|B))"),
        help_text=_("Probabilidade condicional de C dado P(A|B)"),
    )

    report = models.ForeignKey(
        'Report',
        on_delete=models.CASCADE,
        related_name='cyber_security_data',
        verbose_name=_("Report"),
        help_text=_("Report de origem desta informação"),
    )

    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Data de Criação"),
        help_text=_("Data e hora de criação do registro"),
    )

    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Data de Atualização"),
        help_text=_("Data e hora da última atualização do registro"),
    )

    class Meta:
        verbose_name = _("Dado de Cibersegurança")
        verbose_name_plural = _("Dados de Cibersegurança")
        ordering = ['-data_criacao']

    def __str__(self):
        return f"{self.prob_a_priori} - {self.prob_marginal} ({self.report})"
    
    def to_dict(self):
        return {
            'prob_a_priori': self.prob_a_priori,
            'prob_marginal': self.prob_marginal,
            'p_a_given_b': str(self.p_a_given_b),
            'c': self.c,
            'p_c_given_p_a_given_b': str(self.p_c_given_p_a_given_b),
            'report': self.report.name,
        }