from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import CompanyProfile, AnnualRevenue, CybersecuritySpending, CompanyAssets, AdvancedCompanyProfile, Region, AttackType, AttackHistory, RiskAndEconomic, SandboxCompany, SandboxAsset, SandboxAttack
from django.urls import reverse
from .models import Scope, Region, Sector, Report, CyberSecurityData

class AnnualRevenueInline(admin.TabularInline):
    model = AnnualRevenue
    extra = 0

class CybersecuritySpendingInline(admin.TabularInline):
    model = CybersecuritySpending
    extra = 0

class CompanyAssetsInline(admin.TabularInline):
    model = CompanyAssets
    extra = 0

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'headquarters_country', 'industry_type', 'employee_count')
    list_filter = ('industry_type',)
    search_fields = ('name', 'headquarters_country')
    inlines = [AnnualRevenueInline, CybersecuritySpendingInline, CompanyAssetsInline]

class AttackHistoryInline(admin.TabularInline):
    model = AttackHistory
    extra = 0

class RiskAndEconomicInLine(admin.TabularInline):
    model = RiskAndEconomic
    extra = 0

@admin.register(AdvancedCompanyProfile)
class AdvancedCompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_size', 'remote_work_rate', 'global_presence')
    list_filter = ('company_size', 'global_presence')
    search_fields = ('name',)
    inlines = [AnnualRevenueInline, CybersecuritySpendingInline, CompanyAssetsInline, AttackHistoryInline]
    fieldsets = (
        (_('Business Dimension'), {
            'fields': ('company_locations', 'company_size', 'remote_work_rate', 'global_presence')
        }),
        (_('Technical Dimension'), {
            'fields': (
                'authentication_factors', 'cloud_solution_type', 'it_system_monitoring',
                'periodic_system_updates', 'data_encryption_in_storage', 'data_encryption_in_transit',
                'vpn_for_remote_access', 'cybersecurity_awareness_and_training', 'documented_response_plan',
                'response_plan_update', 'operational_recovery_capacity', 'credentials_maintenance',
                'vulnerability_identification', 'network_systems_traffic_monitoring', 'threat_identification_process',
                'it_records_presence', 'antivirus', 'firewall', 'intrusion_detection_system',
                'endpoint_detection_and_response', 'it_security_team'
            )
        }),
        (_('Company Profile'), {
            'fields': ('name', 'headquarters_country', 'industry_type', 'employee_count',
                       'updated_inventory', 'backup_maintenance', 'risk_prioritization')
        }),
    )


@admin.register(AttackType)
class AttackTypeAdmin(admin.ModelAdmin):
    list_display = ('get_attack_type_display',)

################################ 

@admin.register(RiskAndEconomic)
class RiskAndEconomicAdmin(admin.ModelAdmin):
    # Mostre apenas o que você quer
    list_display = ('company_name',)  # Adicione apenas os campos desejados
    search_fields = ('company__name',)  # Buscar pelo nome da empresa

    # Função para exibir o nome da empresa
    def company_name(self, obj):
        return obj.company.name
    company_name.admin_order_field = 'company'  # Habilita a ordenação pelo nome da empresa
    company_name.short_description = 'Company Name'  # Nome da coluna

@admin.register(Scope)
class ScopeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'continent')
    list_filter = ('type', 'continent')
    search_fields = ('name',)


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class CyberSecurityDataInline(admin.TabularInline):
    model = CyberSecurityData
    extra = 1
    readonly_fields = ('data_criacao', 'data_atualizacao')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'company', 'number_of_participants', 'participant_profiles', 'years_covered')
    list_filter = ('year', 'participant_profiles', 'scopes', 'regions', 'sectors')
    search_fields = ('name', 'company', 'years_covered')
    filter_horizontal = ('scopes', 'regions', 'sectors')
    inlines = [CyberSecurityDataInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'year', 'years_covered', 'company', 'number_of_participants', 'participant_profiles')
        }),
        (_('Scopes'), {
            'fields': ('scopes',)
        }),
        (_('Regions'), {
            'fields': ('regions',)
        }),
        (_('Sectors'), {
            'fields': ('sectors',)
        }),
    )


@admin.register(CyberSecurityData)
class CyberSecurityDataAdmin(admin.ModelAdmin):
    list_display = ('prob_a_priori', 'prob_marginal', 'p_a_given_b', 'c', 'p_c_given_p_a_given_b', 'report', 'data_criacao', 'data_atualizacao')
    list_filter = ('report', 'data_criacao', 'data_atualizacao')
    search_fields = ('prob_a_priori', 'prob_marginal', 'report__name')
    readonly_fields = ('data_criacao', 'data_atualizacao')

    fieldsets = (
        (None, {
            'fields': ('prob_a_priori', 'prob_marginal', 'p_a_given_b', 'c', 'p_c_given_p_a_given_b', 'report')
        }),
        (_('Metadata'), {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SandboxCompany)
class SandboxCompanyAdmin(admin.ModelAdmin):
    list_display = ('company', 'is_on')  # Campos que você quer mostrar na lista
    search_fields = ('company__name',)  # Campos para pesquisa

@admin.register(SandboxAsset)
class SandboxAssetAdmin(admin.ModelAdmin):
    list_display = ('sandbox_company', 'asset')  # Campos a mostrar
    search_fields = ('asset__name',)  # Campos para pesquisa

@admin.register(SandboxAttack)
class SandboxAttackAdmin(admin.ModelAdmin):
    list_display = ('asset', 'name', 'value', 'prob', 'invest')  # Campos a mostrar
    search_fields = ('name',)  # Campos para pesquisa