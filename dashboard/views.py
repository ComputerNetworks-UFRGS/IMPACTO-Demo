from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.template import loader
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from accounts.decorators import instructor_required
from .forms import CompanyProfileForm, CompanyAssetsFormSet, UserEditForm, AnnualRevenueFormSet, CybersecuritySpendingFormSet, CompanyProfileBaseEditForm, AdvancedCompanyProfileForm, AttackHistoryForm
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.forms.models import inlineformset_factory
from django.db import transaction
from .models import CompanyProfile, CompanyAssets, AnnualRevenue, CybersecuritySpending, AdvancedCompanyProfile, AttackHistory, CyberSecurityData, SandboxCompany, SandboxAsset, SandboxAttack, Region, RiskAndEconomic, UserCompanyCopy
from .report_database_analysis import calcular_media_probabilidades_por_ataque_e_continente, calcular_media_probabilidades_por_ataque_e_setor
from django.forms import modelformset_factory
from .forms import CompanyProfileForm, AnnualRevenueForm, CybersecuritySpendingForm, CompanyAssetsForm
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from accounts.models import User, Student, Instructor
from django.db.models import Sum, Avg, Count, Exists, OuterRef
from django.shortcuts import get_object_or_404
from django.contrib.humanize.templatetags.humanize import intcomma
from django.urls import reverse
from django.utils.translation import activate
from django.contrib import messages
from django.utils.translation import gettext as _
from Company_Profile_Analysis import profile_evaluator_advanced, profile_evaluator_normal
from django.core.serializers.json import DjangoJSONEncoder
from .continents import CONTINENTS
from copy import deepcopy
from decimal import Decimal
from .utils import get_tech_dimension_table, translate_country_to_portuguese
import logging
import requests
import re
import pdb
import json
import os
import logging


current_dir = 'dashboard/Templates/' # Path for specific apps templates
app_name = 'dashboard'

@login_required
def change_language(request, language_code):
    # Activate the new language
    activate(language_code)

    # Redirect back to the referring page or home
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def index(request, pk=None):
    company = None
    if pk is not None:
        company = get_object_or_404(CompanyProfile, pk=pk)
    return render(request, current_dir + 'index.html', {"company": company})


def render_formset_item(form):
    return ''.join([f'<div class="mb-2">{field.label_tag()} {field}</div>' for field in form])

@login_required
@require_http_methods(["GET", "POST"])
@instructor_required
def add_company_profile(request):
    pode_deletar=0 #indica que o botão de deletar entradas nas listas não deve ser mostrado
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST)
        revenue_formset = AnnualRevenueFormSet(request.POST, prefix='annual_revenue')
        spending_formset = CybersecuritySpendingFormSet(request.POST, prefix='cybersecurity_spending')
        assets_formset = CompanyAssetsFormSet(request.POST, prefix='company_assets')
        
        if form.is_valid() and revenue_formset.is_valid() and spending_formset.is_valid() and assets_formset.is_valid():
            try:
                with transaction.atomic():
                    company_profile = form.save()
                    
                    if not revenue_formset.has_changed():
                        raise ValueError("At least one Annual Revenue entry is required.")
                    revenue_formset.instance = company_profile
                    revenue_formset.save()
                    
                    if not spending_formset.has_changed():
                        raise ValueError("At least one Cybersecurity Spending entry is required.")
                    spending_formset.instance = company_profile
                    spending_formset.save()
                    
                    if not assets_formset.has_changed():
                        raise ValueError("At least one Company Asset entry is required.")
                    assets_formset.instance = company_profile
                    assets_formset.save()

                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('dashboard:company_profile_detail', kwargs={'pk': company_profile.pk})
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'errors': str(e)
                })
        else:
            errors = {
                'form': form.errors,
                'revenue': revenue_formset.errors,
                'spending': spending_formset.errors,
                'assets': assets_formset.errors
            }
            return JsonResponse({
                'success': False,
                'errors': errors
            })
    else:
        form = CompanyProfileForm()
        revenue_formset = AnnualRevenueFormSet(prefix='annual_revenue')
        spending_formset = CybersecuritySpendingFormSet(prefix='cybersecurity_spending')
        assets_formset = CompanyAssetsFormSet(prefix='company_assets')
    
    context = {
        'form': form,
        'revenue_formset': revenue_formset,
        'spending_formset': spending_formset,
        'assets_formset': assets_formset,
        'revenue_empty_form': mark_safe(render_formset_item(revenue_formset.empty_form)),
        'spending_empty_form': mark_safe(render_formset_item(spending_formset.empty_form)),
        'assets_empty_form': mark_safe(render_formset_item(assets_formset.empty_form)),
        'pode_deletar': pode_deletar,
    }
    
    return render(request, current_dir + 'add_company_profile.html', context)

@login_required
@require_http_methods(["GET", "POST"])
@instructor_required
def add_advanced_company_profile(request):
    pode_deletar = 0  # Indica que o botão de deletar entradas nas listas não deve ser mostrado

    AttackHistoryFormSetFactory = inlineformset_factory(
        AdvancedCompanyProfile,
        AttackHistory,
        form=AttackHistoryForm,
        extra=1,
        can_delete=False
    )

    if request.method == 'POST':
        form = AdvancedCompanyProfileForm(request.POST)
        annual_revenue_formset = AnnualRevenueFormSet(request.POST, prefix='annual_revenue')
        cybersecurity_spending_formset = CybersecuritySpendingFormSet(request.POST, prefix='cybersecurity_spending')
        company_assets_formset = CompanyAssetsFormSet(request.POST, prefix='company_assets')
        attack_history_formset = AttackHistoryFormSetFactory(request.POST, prefix='attack_history')

        if form.is_valid():
            try:
                with transaction.atomic():
                    company_profile = form.save()
                    
                    annual_revenue_formset.instance = company_profile
                    if annual_revenue_formset.is_valid():
                        annual_revenue_formset.save()
                    else:
                        raise ValueError("Invalid Annual Revenue data")
                    
                    cybersecurity_spending_formset.instance = company_profile
                    if cybersecurity_spending_formset.is_valid():
                        cybersecurity_spending_formset.save()
                    else:
                        raise ValueError("Invalid Cybersecurity Spending data")
                    
                    company_assets_formset.instance = company_profile
                    if company_assets_formset.is_valid():
                        company_assets_formset.save()
                    else:
                        raise ValueError("Invalid Company Assets data")
                    
                    attack_history_formset.instance = company_profile
                    if attack_history_formset.is_valid():
                        attack_history_formset.save()
                    else:
                        raise ValueError("Invalid Attack History data")

                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('dashboard:company_profile_detail', kwargs={'pk': company_profile.pk})
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'errors': str(e)
                })
        else:
            errors = {
                'form': form.errors,
                'annual_revenue': annual_revenue_formset.errors,
                'cybersecurity_spending': cybersecurity_spending_formset.errors,
                'company_assets': company_assets_formset.errors,
                'attack_history': attack_history_formset.errors
            }
            return JsonResponse({
                'success': False,
                'errors': errors
            })
    else:
        form = AdvancedCompanyProfileForm()
        annual_revenue_formset = AnnualRevenueFormSet(prefix='annual_revenue')
        cybersecurity_spending_formset = CybersecuritySpendingFormSet(prefix='cybersecurity_spending')
        company_assets_formset = CompanyAssetsFormSet(prefix='company_assets')
        attack_history_formset = AttackHistoryFormSetFactory(prefix='attack_history')

    context = {
        'form': form,
        'revenue_formset': annual_revenue_formset,
        'spending_formset': cybersecurity_spending_formset,
        'assets_formset': company_assets_formset,
        'attack_history_formset': attack_history_formset,
        'annual_revenue_empty_form': mark_safe(render_formset_item(annual_revenue_formset.empty_form)),
        'cybersecurity_spending_empty_form': mark_safe(render_formset_item(cybersecurity_spending_formset.empty_form)),
        'company_assets_empty_form': mark_safe(render_formset_item(company_assets_formset.empty_form)),
        'attack_history_empty_form': mark_safe(render_formset_item(attack_history_formset.empty_form)),
        'pode_deletar': pode_deletar,
        'is_advanced': True,
    }
    return render(request, current_dir + 'add_advanced_company_profile.html', context)

def is_company_copy(company):
    """
    Função auxiliar para verificar se uma empresa (básica ou avançada) é uma cópia.
    """
    # Verifica se é um perfil avançado
    if isinstance(company, AdvancedCompanyProfile):
        base_company = company
    elif hasattr(company, 'advancedcompanyprofile'):
        base_company = company.advancedcompanyprofile
    else:
        base_company = company

    content_type = ContentType.objects.get_for_model(base_company)
    return UserCompanyCopy.objects.filter(
        content_type=content_type,
        object_id=base_company.id
    ).exists()


@login_required
def company_profile_detail(request, pk):
    from django.utils.translation import get_language
    
    user = request.user
    
    # Tenta obter a empresa como CompanyProfile ou AdvancedCompanyProfile
    company_profile_ct = ContentType.objects.get_for_model(CompanyProfile)
    advanced_company_profile_ct = ContentType.objects.get_for_model(AdvancedCompanyProfile)
    
    company = None
    is_advanced = False
    original_company_name = None
    original_company_pk = None

    # Primeiro, tenta obter como AdvancedCompanyProfile
    try:
        company = AdvancedCompanyProfile.objects.get(id=pk)
        is_advanced = True
    except AdvancedCompanyProfile.DoesNotExist:
        # Se não for AdvancedCompanyProfile, tenta como CompanyProfile
        try:
            company = CompanyProfile.objects.get(id=pk)
        except CompanyProfile.DoesNotExist:
            messages.error(request, "Empresa não encontrada.")
            return redirect('dashboard:company_profile_list')

    # Verifica se é uma cópia e se pertence ao usuário
    user_copy = UserCompanyCopy.objects.filter(
        user=user,
        object_id=company.pk,
        content_type__in=[company_profile_ct, advanced_company_profile_ct]
    ).first()

    is_copy = UserCompanyCopy.objects.filter(
        object_id=company.pk,
        content_type__in=[company_profile_ct, advanced_company_profile_ct]
    ).exists()

    # Se for uma cópia, obtém o nome e pk da empresa original
    if is_copy:
        copy_obj = UserCompanyCopy.objects.filter(
            object_id=company.pk,
            content_type__in=[company_profile_ct, advanced_company_profile_ct]
        ).first()
        if copy_obj and copy_obj.original_company:
            original_company_name = copy_obj.original_company.name
            original_company_pk = copy_obj.original_company.pk

    # Verifica permissão para visualizar
    if is_copy and not user_copy and not user.is_instructor:
        messages.error(request, "Você não tem permissão para ver os detalhes desta empresa.")
        return redirect('dashboard:company_profile_list')

    # Função auxiliar para traduzir o país conforme o idioma
    def get_localized_country(company):
        current_language = get_language()
        
        # Se o idioma atual for português (pt-br), traduz de inglês para português
        if current_language == 'pt-br':
            return translate_country_to_portuguese(company.headquarters_country_en)
        else:
            # Se o idioma for inglês ou outro, usa o campo em inglês
            return company.headquarters_country_en
    
    # Adicionar o país localizado à empresa
    company.localized_country = get_localized_country(company)

    sector_company = company.industry_type
    #print(sector_company)
    region_company = company.headquarters_country
    #print(region_company)

    if is_advanced:
        # Busca os campos relevantes para o setor específico da empresa
        relevant_fields = dict(company.get_relevant_fields())
    else:
        relevant_fields = {}    

    # Definindo o Banco de Dados
    database_s = CyberSecurityData.objects.filter(prob_marginal=sector_company)
    database_s2 = CyberSecurityData.objects.filter(prob_marginal=sector_company.capitalize())
    database_r = CyberSecurityData.objects.filter(prob_marginal=region_company)
    database_r2 = CyberSecurityData.objects.filter(prob_marginal=region_company.lower())
    database = database_s | database_s2 | database_r | database_r2

    #print(database)

    if is_advanced:
        attack_history = AttackHistory.objects.filter(company=company).order_by('-attack_type')
        final_score1, text_score1, malware_region_value1, malware_sector_value1, malware_resilience_value1, malware_final_score1, phishing_region_value1, phishing_sector_value1, phishing_resilience_value1, phishing_final_score1, ddos_region_value1, ddos_sector_value1, ddos_resilience_value1, ddos_final_score1, insights_pos1, insights_neg1, malware_succ1, phishing_succ1, ddos_succ1 = profile_evaluator_advanced.risk_analysis_advanced(database, company, attack_history)
        
    else:
        final_score1, text_score1, malware_region_value1, malware_sector_value1, malware_resilience_value1, malware_final_score1, phishing_region_value1, phishing_sector_value1, phishing_resilience_value1, phishing_final_score1, ddos_region_value1, ddos_sector_value1, ddos_resilience_value1, ddos_final_score1, insights_pos1, insights_neg1, malware_succ1, phishing_succ1, ddos_succ1 = profile_evaluator_normal.risk_analysis_normal(database, company)

    print(f'\n\nFinalizando Análise de Risco:')
    print(final_score1, text_score1, malware_region_value1, malware_sector_value1, malware_resilience_value1, malware_final_score1, phishing_region_value1, phishing_sector_value1, phishing_resilience_value1, phishing_final_score1, ddos_region_value1, ddos_sector_value1, ddos_resilience_value1, ddos_final_score1, insights_pos1, insights_neg1, malware_succ1, phishing_succ1, ddos_succ1)
    # Getting in the database
    risk_and_economic_instance, created = RiskAndEconomic.objects.get_or_create(company=company)
    
    if is_advanced:
        risk_and_economic_instance.company_profile_type = True
    else:
        risk_and_economic_instance.company_profile_type = False
    risk_and_economic_instance.final_score = final_score1
    risk_and_economic_instance.text_score = text_score1
    risk_and_economic_instance.malware_region_value = malware_region_value1
    risk_and_economic_instance.malware_sector_value = malware_sector_value1
    risk_and_economic_instance.malware_resilience_value = malware_resilience_value1
    risk_and_economic_instance.malware_final_score = malware_final_score1
    risk_and_economic_instance.phishing_region_value = phishing_region_value1
    risk_and_economic_instance.phishing_sector_value = phishing_sector_value1
    risk_and_economic_instance.phishing_resilience_value = phishing_resilience_value1
    risk_and_economic_instance.phishing_final_score = phishing_final_score1
    risk_and_economic_instance.ddos_region_value = ddos_region_value1
    risk_and_economic_instance.ddos_sector_value = ddos_sector_value1
    risk_and_economic_instance.ddos_resilience_value = ddos_resilience_value1
    risk_and_economic_instance.ddos_final_score = ddos_final_score1
    risk_and_economic_instance.insights_pos = insights_pos1
    risk_and_economic_instance.insights_neg = insights_neg1
    risk_and_economic_instance.malware_succ = malware_succ1
    risk_and_economic_instance.phishing_succ = phishing_succ1
    risk_and_economic_instance.ddos_succ = ddos_succ1
    risk_and_economic_instance.save()

    template = current_dir + 'company_profile_advanced_detail.html' if is_advanced else current_dir + 'company_profile_detail.html'
    
    context = {
        'company': company,
        'is_advanced': is_advanced,
        'is_copy': is_copy,
        'is_user_copy': bool(user_copy),
        'is_instructor': user.is_instructor,
        'risk_and_economic': risk_and_economic_instance,
        'final_score': final_score1,
        'text_score': text_score1,
        'insights_pos': insights_pos1,
        'insights_neg': insights_neg1,
        'malware_succ': malware_succ1,
        'phishing_succ': phishing_succ1,
        'ddos_succ': ddos_succ1,
        'original_company_name': original_company_name,
        'original_company_pk': original_company_pk,
        'relevant_fields': relevant_fields
    }
    
    return render(request, template, context)

@login_required
def edit_company_profile(request, pk):
    user = request.user
    company_basic = get_object_or_404(CompanyProfile, pk=pk)
    
    # Verifica se a empresa é uma cópia e se pertence ao usuário atual
    company_profile_ct = ContentType.objects.get_for_model(CompanyProfile)
    advanced_company_profile_ct = ContentType.objects.get_for_model(AdvancedCompanyProfile)
    user_copy = UserCompanyCopy.objects.filter(
        user=user,
        object_id=company_basic.pk,
        content_type__in=[company_profile_ct, advanced_company_profile_ct]
    ).first()

    # Verifica se o usuário tem permissão para editar
    if not user.is_instructor and not user_copy:
        messages.error(request, _("Você não possui permissão para editar essa empresa. Tente criar uma cópia."))
        return redirect('dashboard:company_profile_detail', pk=company_basic.pk)

    pode_deletar = 1  
    
    # Verifica se a empresa tem um perfil avançado
    is_advanced = hasattr(company_basic, 'advancedcompanyprofile')
    
    if is_advanced:
        company = company_basic.advancedcompanyprofile
        template = current_dir + 'edit_advanced_company_profile.html'
        
        # Definição dos formsets para AdvancedCompanyProfile
        AttackHistoryFormSetFactory = inlineformset_factory(
            AdvancedCompanyProfile,
            AttackHistory,
            form=AttackHistoryForm,
            extra=1,
            can_delete=True
        )
        
        if request.method == 'POST':
            form = AdvancedCompanyProfileForm(request.POST, instance=company)
            annual_revenue_formset = AnnualRevenueFormSet(
                request.POST, 
                instance=company, 
                prefix='annual_revenue'
            )
            cybersecurity_spending_formset = CybersecuritySpendingFormSet(
                request.POST, 
                instance=company, 
                prefix='cybersecurity_spending'
            )
            company_assets_formset = CompanyAssetsFormSet(
                request.POST, 
                instance=company, 
                prefix='company_assets'
            )
            attack_history_formset = AttackHistoryFormSetFactory(
                request.POST,
                instance=company,
                prefix='attack_history'
            )
    
            if (form.is_valid() and annual_revenue_formset.is_valid() and
                cybersecurity_spending_formset.is_valid() and company_assets_formset.is_valid() and
                attack_history_formset.is_valid()):
    
                try:
                    with transaction.atomic():
                        form.save()
                        annual_revenue_formset.save()
                        cybersecurity_spending_formset.save()
                        company_assets_formset.save()
                        attack_history_formset.save()
    
                    messages.success(request, _('Advanced company profile updated successfully.'))
                    return redirect('dashboard:company_profile_detail', pk=company.pk)
                except Exception as e:
                    messages.error(request, _('An error occurred while saving: ') + str(e))
            else:
                messages.error(request, _('Please correct the errors below.'))
        else:
            form = AdvancedCompanyProfileForm(instance=company)
            annual_revenue_formset = AnnualRevenueFormSet(
                instance=company, 
                prefix='annual_revenue'
            )
            cybersecurity_spending_formset = CybersecuritySpendingFormSet(
                instance=company, 
                prefix='cybersecurity_spending'
            )
            company_assets_formset = CompanyAssetsFormSet(
                instance=company, 
                prefix='company_assets'
            )
            attack_history_formset = AttackHistoryFormSetFactory(
                instance=company, 
                prefix='attack_history'
            )
    
        context = {
            'company': company,
            'form': form,
            'annual_revenue_formset': annual_revenue_formset,
            'cybersecurity_spending_formset': cybersecurity_spending_formset,
            'company_assets_formset': company_assets_formset,
            'attack_history_formset': attack_history_formset,
            'is_advanced': is_advanced,
            'pode_deletar': pode_deletar,
        }
    
    else:
        company = company_basic
        template = current_dir + 'edit_company_profile.html'
        
        if request.method == 'POST':
            form = CompanyProfileForm(request.POST, instance=company)
            annual_revenue_formset = AnnualRevenueFormSet(
                request.POST, 
                instance=company, 
                prefix='annual_revenue'
            )
            cybersecurity_spending_formset = CybersecuritySpendingFormSet(
                request.POST, 
                instance=company, 
                prefix='cybersecurity_spending'
            )
            company_assets_formset = CompanyAssetsFormSet(
                request.POST, 
                instance=company, 
                prefix='company_assets'
            )
    
            if (form.is_valid() and annual_revenue_formset.is_valid() and
                cybersecurity_spending_formset.is_valid() and company_assets_formset.is_valid()):
    
                try:
                    with transaction.atomic():
                        form.save()
                        annual_revenue_formset.save()
                        cybersecurity_spending_formset.save()
                        company_assets_formset.save()
    
                    messages.success(request, _('Company profile updated successfully.'))
                    return redirect('dashboard:company_profile_detail', pk=company.pk)
                except Exception as e:
                    messages.error(request, _('An error occurred while saving: ') + str(e))
            else:
                messages.error(request, _('Please correct the errors below.'))
        else:
            form = CompanyProfileForm(instance=company)
            annual_revenue_formset = AnnualRevenueFormSet(
                instance=company, 
                prefix='annual_revenue'
            )
            cybersecurity_spending_formset = CybersecuritySpendingFormSet(
                instance=company, 
                prefix='cybersecurity_spending'
            )
            company_assets_formset = CompanyAssetsFormSet(
                instance=company, 
                prefix='company_assets'
            )
    
        context = {
            'company': company,
            'form': form,
            'annual_revenue_formset': annual_revenue_formset,
            'cybersecurity_spending_formset': cybersecurity_spending_formset,
            'company_assets_formset': company_assets_formset,
            'is_advanced': is_advanced,
            'pode_deletar': pode_deletar,
        }
    
    return render(request, template, context)

def copy_basic_company_profile(original_company):
    """
    Função auxiliar para copiar um CompanyProfile básico.
    """
    with transaction.atomic():
        copied_company = CompanyProfile.objects.create(
            name=original_company.name + " (Cópia)",
            headquarters_country=original_company.headquarters_country,
            industry_type=original_company.industry_type,
            employee_count=original_company.employee_count,
            updated_inventory=original_company.updated_inventory,
            backup_maintenance=original_company.backup_maintenance,
            risk_prioritization=original_company.risk_prioritization,
        )

        for revenue in original_company.annual_revenues.all():
            AnnualRevenue.objects.create(
                company=copied_company,
                year=revenue.year,
                amount=revenue.amount,
            )
        
        for spending in original_company.cybersecurity_spendings.all():
            CybersecuritySpending.objects.create(
                company=copied_company,
                year=spending.year,
                amount=spending.amount,
            )
        
        for asset in original_company.company_assets.all():
            CompanyAssets.objects.create(
                company=copied_company,
                item=asset.item,
                value=asset.value,
            )

    return copied_company

def copy_advanced_company_profile(original_advanced_company):
    """
    Função auxiliar para copiar um AdvancedCompanyProfile.
    """
    with transaction.atomic():
        copied_advanced = AdvancedCompanyProfile.objects.create(
            name=original_advanced_company.name + " (Cópia)",
            headquarters_country=original_advanced_company.headquarters_country,
            industry_type=original_advanced_company.industry_type,
            employee_count=original_advanced_company.employee_count,
            updated_inventory=original_advanced_company.updated_inventory,
            backup_maintenance=original_advanced_company.backup_maintenance,
            risk_prioritization=original_advanced_company.risk_prioritization,
            company_size=original_advanced_company.company_size,
            remote_work_rate=original_advanced_company.remote_work_rate,
            global_presence=original_advanced_company.global_presence,
            authentication_factors=original_advanced_company.authentication_factors,
            cloud_solution_type=original_advanced_company.cloud_solution_type,
            it_system_monitoring=original_advanced_company.it_system_monitoring,
            periodic_system_updates=original_advanced_company.periodic_system_updates,
            data_encryption_in_storage=original_advanced_company.data_encryption_in_storage,
            data_encryption_in_transit=original_advanced_company.data_encryption_in_transit,
            vpn_for_remote_access=original_advanced_company.vpn_for_remote_access,
            cybersecurity_awareness_and_training=original_advanced_company.cybersecurity_awareness_and_training,
            documented_response_plan=original_advanced_company.documented_response_plan,
            response_plan_update=original_advanced_company.response_plan_update,
            operational_recovery_capacity=original_advanced_company.operational_recovery_capacity,
            credentials_maintenance=original_advanced_company.credentials_maintenance,
            vulnerability_identification=original_advanced_company.vulnerability_identification,
            network_systems_traffic_monitoring=original_advanced_company.network_systems_traffic_monitoring,
            threat_identification_process=original_advanced_company.threat_identification_process,
            it_records_presence=original_advanced_company.it_records_presence,
            antivirus=original_advanced_company.antivirus,
            firewall=original_advanced_company.firewall,
            intrusion_detection_system=original_advanced_company.intrusion_detection_system,
            endpoint_detection_and_response=original_advanced_company.endpoint_detection_and_response,
            it_security_team=original_advanced_company.it_security_team,
        )

        for revenue in original_advanced_company.annual_revenues.all():
            AnnualRevenue.objects.create(
                company=copied_advanced,
                year=revenue.year,
                amount=revenue.amount,
            )
        
        for spending in original_advanced_company.cybersecurity_spendings.all():
            CybersecuritySpending.objects.create(
                company=copied_advanced,
                year=spending.year,
                amount=spending.amount,
            )
        
        for asset in original_advanced_company.company_assets.all():
            CompanyAssets.objects.create(
                company=copied_advanced,
                item=asset.item,
                value=asset.value,
            )
            
        '''
        copied_advanced.company_locations.set(original_advanced_company.company_locations.all())
        '''

        for attack_history in original_advanced_company.attack_histories.all():
            AttackHistory.objects.create(
                company=copied_advanced,
                attack_type=attack_history.attack_type,
                year=attack_history.year,
                count=attack_history.count,
            )

    return copied_advanced

@login_required
def copy_company_profile(request, pk):
    """
    View para copiar um perfil de empresa para o usuário.
    """
    original_company = get_object_or_404(CompanyProfile, pk=pk)
    user = request.user

    # Verificar se o original_company já é uma cópia
    is_copy = is_company_copy(original_company)
    if is_copy:
        messages.error(request, "Você não pode copiar uma cópia de um perfil de empresa.")
        return redirect('dashboard:company_profile_detail', pk=pk)

    # Verifica se já existe uma cópia para este usuário e esta empresa original
    existing_copy = UserCompanyCopy.objects.filter(user=user, original_company=original_company).first()
    if existing_copy:
        messages.info(request, "Você já possui uma cópia deste perfil de empresa.")
        return redirect('dashboard:company_profile_detail', pk=existing_copy.copied_company.pk)

    with transaction.atomic():
        if hasattr(original_company, 'advancedcompanyprofile'):
            # A empresa original é um AdvancedCompanyProfile
            original_advanced = original_company.advancedcompanyprofile
            copied_company = copy_advanced_company_profile(original_advanced)
            content_type_new = ContentType.objects.get_for_model(AdvancedCompanyProfile)
        else:
            # A empresa original é um CompanyProfile básico
            copied_company = copy_basic_company_profile(original_company)
            content_type_new = ContentType.objects.get_for_model(CompanyProfile)
        
        # Cria a cópia de UserCompanyCopy com todos os campos necessários
        UserCompanyCopy.objects.create(
            user=user,
            original_company=original_company,
            content_type=content_type_new,
            object_id=copied_company.id,
            copied_company=copied_company
        )
        messages.success(request, "Perfil da empresa copiado com sucesso!")

    return redirect('dashboard:company_profile_detail', pk=copied_company.pk)


@login_required
def company_profile_list(request, action = None):
    from django.utils.translation import get_language
    
    # Obter os ContentTypes para CompanyProfile e AdvancedCompanyProfile
    company_profile_ct = ContentType.objects.get_for_model(CompanyProfile)
    advanced_company_profile_ct = ContentType.objects.get_for_model(AdvancedCompanyProfile)

    # Subquery para verificar se a empresa é uma cópia
    is_copy_subquery = UserCompanyCopy.objects.filter(
        content_type__in=[company_profile_ct, advanced_company_profile_ct],
        object_id=OuterRef('pk')
    )

    # Buscar todas as empresas, incluindo as avançadas, e marcar se são cópias
    all_companies = CompanyProfile.objects.select_related('advancedcompanyprofile').annotate(
        is_copy=Exists(is_copy_subquery)
    ).order_by('name')

    # Filtrar apenas as empresas originais
    original_companies = [company for company in all_companies if not company.is_copy]
    
    # Função auxiliar para traduzir o país conforme o idioma
    def get_localized_country(company):
        current_language = get_language()
        
        # Se o idioma atual for português (pt-br), traduz de inglês para português
        if current_language == 'pt-br':
            return translate_country_to_portuguese(company.headquarters_country_en)
        else:
            # Se o idioma for inglês ou outro, usa o campo em inglês
            return company.headquarters_country_en
    
    # Adicionar o país localizado a cada empresa
    for company in original_companies:
        company.localized_country = get_localized_country(company)

    action_send = 'none'
    if action == 'analyse':
        action_send = 'analyse'
    elif action == 'economic':
        action_send = 'economic'
    
    return render(request, current_dir + 'company_profile_list.html', {'companies': original_companies, 'action': action_send})
    
@login_required
def user_company_copies(request):
    from django.utils.translation import get_language
    
    user = request.user
    
    # Buscar todas as cópias do usuário
    user_copies = UserCompanyCopy.objects.filter(user=user).select_related('content_type', 'original_company')
    
    copied_companies = []
    company_profile_ct = ContentType.objects.get_for_model(CompanyProfile)
    advanced_company_profile_ct = ContentType.objects.get_for_model(AdvancedCompanyProfile)

    # Função auxiliar para traduzir o país conforme o idioma
    def get_localized_country(company):
        current_language = get_language()
        
        # Se o idioma atual for português (pt-br), traduz de inglês para português
        if current_language == 'pt-br':
            return translate_country_to_portuguese(company.headquarters_country_en)
        else:
            # Se o idioma for inglês ou outro, usa o campo em inglês
            return company.headquarters_country_en

    for user_copy in user_copies:
        try:
            if user_copy.content_type == company_profile_ct:
                company = CompanyProfile.objects.get(id=user_copy.object_id)
                is_advanced = False
            elif user_copy.content_type == advanced_company_profile_ct:
                company = AdvancedCompanyProfile.objects.get(id=user_copy.object_id)
                is_advanced = True
            else:
                continue  # Pula se não for nem CompanyProfile nem AdvancedCompanyProfile

            # Adicionar o país localizado à empresa
            company.localized_country = get_localized_country(company)

            copied_companies.append({
                'company': company,
                'is_advanced': is_advanced,
                'original_company': user_copy.original_company,
                'created_at': user_copy.created_at
            })
        except (CompanyProfile.DoesNotExist, AdvancedCompanyProfile.DoesNotExist):
            # Se a empresa não existe mais, podemos opcionalmente registrar isso ou limpar a entrada
            # Aqui, optamos por simplesmente pular
            continue

    # Ordenar as cópias por data de criação (mais recente primeiro)
    copied_companies.sort(key=lambda x: x['created_at'], reverse=True)
    
    context = {
        'copied_companies': copied_companies
    }
    
    return render(request, current_dir + 'user_company_copies.html', context)

# the overview of risk analysis (the first tab)
@login_required
def company_analysis(request, pk):
    from django.utils.translation import get_language
    
    company = get_object_or_404(CompanyProfile, pk=pk)
    
    # Função auxiliar para traduzir o país conforme o idioma
    def get_localized_country(company):
        current_language = get_language()
        
        # Se o idioma atual for português (pt-br), traduz de inglês para português
        if current_language == 'pt-br':
            return translate_country_to_portuguese(company.headquarters_country_en)
        else:
            # Se o idioma for inglês ou outro, usa o campo em inglês
            return company.headquarters_country_en
    
    # Adicionar o país localizado à empresa
    company.localized_country = get_localized_country(company)
    
    bar_chart_data = {
        'labels': ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"],
        'values': [10, 15, 20, 25, 50, 20, 40, 45, 33, 55, 85, 65]
    }

    sector = company.industry_type.capitalize()
    database = CyberSecurityData.objects.filter(prob_marginal=sector)
    attack_types = ['Malware', 'Phishing', 'DDoS']
    risks = profile_evaluator_normal.region_percentage(database)

    prob_num_attacks_data = {
        'labels': ["0", "1 to 3", "4 to 10", "11 to 20", "21 to 30", "31+"],
        'probabilities': [0.05, 0.15, 0.30, 0.25, 0.15, 0.10]
    }
    
    # Determina a região usando o campo em inglês para consistência
    headquarters_country_en = company.headquarters_country_en
    region = next((region for region, countries in CONTINENTS.items() if headquarters_country_en in countries), 'Unknown')

    # Obtem dados dos setores e das regiões
    # Aqui é um ponto de possível otimização futura, pois está calculando as médias de todos setores e regiões
    # Daria para fazer uma função específica para filtrar os dados antes, ao invés de pegar todos
    all_sector_data = calcular_media_probabilidades_por_ataque_e_setor()
    all_region_data = calcular_media_probabilidades_por_ataque_e_continente()

    # Traduzir dados do setor
    translated_sector_data = {}
    for s, data in all_sector_data.items():
        translated_data = {
            'attack_types': [_(attack) for attack in data['attack_types']],
            'risks': [float(risk) if risk is not None else 0 for risk in data['risks']],
            'counts': data['counts']
        }
        translated_sector_data[_(s)] = translated_data

    # Traduzir dados da região
    translated_region_data = {}
    for r, data in all_region_data.items():
        translated_data = {
            'attack_types': [_(attack) for attack in data['attack_types']],
            'risks': [float(risk) if risk is not None else 0 for risk in data['risks']],
            'counts': data['counts']
        }
        translated_region_data[_(r)] = translated_data

    company_sector_data = translated_sector_data.get(_(sector), {})
    company_region_data = translated_region_data.get(_(region), {})

    # Preparando os dados para gráficos de barras do setor e região
    sector_bar_data = {
        'labels': company_sector_data.get('attack_types', []),
        'values': company_sector_data.get('risks', [])
    }
    region_bar_data = {
        'labels': company_region_data.get('attack_types', []),
        'values': company_region_data.get('risks', [])
    }

    context = {
        'company': company,
        'industry_type': _(sector),
        'headquarters_country': company.localized_country,  # Use the localized country
        'headquarters_country_en': headquarters_country_en,  # Keep English version for map
        'bar_chart_data': bar_chart_data,
        'attack_types': [_(attack) for attack in attack_types],
        'risks': risks,
        'prob_num_attacks_data': prob_num_attacks_data,
        'sector_bar_data': sector_bar_data,
        'region_bar_data': region_bar_data,
        'region': _(region)
    }
    return render(request, current_dir + 'company_analysis.html', context)

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_scale(value, min_val, max_val, field_name):
    """
    Valida se um valor está dentro da escala esperada
    """
    if value is None:
        raise ValueError(f"{field_name} não pode ser None")
    if not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} deve ser numérico")
    if not min_val <= value <= max_val:
        raise ValueError(f"{field_name} deve estar entre {min_val} e {max_val}")
    return True


def get_risk_level(score):
    """
    Retorna a cor de fundo e o texto correspondente ao nível de risco
    """
    try:
        validate_scale(score, 0, 100, "Score de risco")
        if score >= 80:
            return 0xFF0000, _("Critical")
        elif score >= 60:
            return 0xFFA500, _("Dangerous")
        elif score >= 40:
            return 0xffdc00, _("Caution")
        elif score >= 20:
            return 0x008000, _("Normal")
        else:
            return 0x00A8FF, _("Healthy")
    except Exception as e:
        logger.error(f"Erro ao determinar nível de risco: {str(e)}")
        raise

def prepare_risk_data(risk_data):
    """
    Processa e valida os dados de risco,
    garantindo valor mínimo de 1 para escalas de 1-5
    """
    processed_data = {}
    
    for threat, data in risk_data.items():
        logger.info(f"\n=== Processando dados para ameaça: {threat} ===")
        logger.info(f"Dados brutos recebidos: {data}")
        
        try:
            min_region_and_sector = 0.3
            max_region_and_sector = 2.0
            # Validação dos dados de entrada
            validate_scale(data['region'], min_region_and_sector, max_region_and_sector, f"{threat} - region")
            validate_scale(data['sector'], min_region_and_sector, max_region_and_sector, f"{threat} - sector")
            validate_scale(data['resilience'], 0.0, 5, f"{threat} - resilience")
            validate_scale(data['risk_score'], 0, 10, f"{threat} - risk_score")
            
            # Função auxiliar para garantir mínimo de 1 na escala 0-5
            def ensure_min_one(value):
                return max(1, value)
            
            processed_threat_data = {
                # Converte region e sector de 0.5-1.5 para 1-5
                'region_value': ensure_min_one(max(0, min(5, (data['region'] - 0.5) * 5))),
                'sector_value': ensure_min_one(max(0, min(5, (data['sector'] - 0.5) * 5))),

                # Resistência já deve estar em escala de 0 a 5, então to passando pra 1 a 5
                'resilience_value': ensure_min_one(data['resilience']),

                #  risk_score já está em escala de 0 a 10
                'risk_score_normalized': data['risk_score']
            }
            
            logger.info("\nDados processados:")
            logger.info(f"Risco da Região (1-5): {processed_threat_data['region_value']:.1f}")
            logger.info(f"Risco do Setor (1-5): {processed_threat_data['sector_value']:.1f}")
            logger.info(f"Resiliência (1-5): {processed_threat_data['resilience_value']:.1f}")
            logger.info(f"Score de Risco (0-10): {processed_threat_data['risk_score_normalized']:.1f}")
            
            processed_data[threat] = processed_threat_data
        except Exception as e:
            logger.error(f"Erro no processamento de {threat}: {str(e)}")
            raise
            
    return processed_data

def get_company_profile(pk):
    """
    Obtém o perfil da empresa com validação
    """
    logger.info(f"\n=== Obtendo perfil da empresa {pk} ===")
    try:
        company = AdvancedCompanyProfile.objects.get(id=pk)
        logger.info("Perfil avançado encontrado")
        return company, True
    except AdvancedCompanyProfile.DoesNotExist:
        try:
            company = CompanyProfile.objects.get(id=pk)
            logger.info("Perfil básico encontrado")
            return company, False
        except CompanyProfile.DoesNotExist:
            logger.error("Perfil da empresa não encontrado")
            return None, False

def get_company_risk_details(company):
    """
    Obtém detalhes de risco com validação
    """
    logger.info("\n=== Obtendo detalhes de risco ===")
    try:
        details = RiskAndEconomic.objects.get(company=company)
        if details:
            logger.info("Detalhes de risco encontrados")
            # Validação dos dados obtidos
            validate_scale(details.final_score, 0, 10, "Score final")
            return details
    except RiskAndEconomic.DoesNotExist:
        logger.error("Detalhes de risco não encontrados")
        return None
    except Exception as e:
        logger.error(f"Erro ao obter detalhes de risco: {str(e)}")
        raise

@login_required
def company_analysis_pro(request, pk):
    logger.info("\n====== INICIANDO ANÁLISE DE EMPRESA ======")


    # Obtém a empresa
    company, is_advanced = get_company_profile(pk)
    if not company:
        messages.error(request, _("Empresa não encontrada."))
        return redirect('dashboard:company_profile_list')

    # Obtém detalhes de risco
    company_details = get_company_risk_details(company)
    if not company_details:
        messages.error(request, _("Cálculo de risco não encontrado."))
        return redirect('dashboard:company_profile_detail', pk=company.pk)

    # Log dos dados brutos do banco
    logger.info("\n=== DADOS BRUTOS DO BANCO ===")
    logger.info(f"Score Final: {company_details.final_score}")
    logger.info("\nMalware:")
    logger.info(f"Region: {company_details.malware_region_value}")
    logger.info(f"Sector: {company_details.malware_sector_value}")
    logger.info(f"Resilience: {company_details.malware_resilience_value}")
    logger.info("\nPhishing:")
    logger.info(f"Region: {company_details.phishing_region_value}")
    logger.info(f"Sector: {company_details.phishing_sector_value}")
    logger.info(f"Resilience: {company_details.phishing_resilience_value}")
    logger.info("\nDDoS:")
    logger.info(f"Region: {company_details.ddos_region_value}")
    logger.info(f"Sector: {company_details.ddos_sector_value}")
    logger.info(f"Resilience: {company_details.ddos_resilience_value}")

    # Prepara dados de risco
    risk_data = {
        'malware': {
            'region': company_details.malware_region_value,  #0,5 a 1,5
            'sector': company_details.malware_sector_value,  #0,5 a 1,5
            'resilience': company_details.malware_resilience_value - profile_evaluator_advanced.MIN_RESILIENCE, #dado deve vir em escala de 0 a 5
            'risk_score': company_details.malware_final_score
        },
        'phishing': {
            'region': company_details.phishing_region_value,
            'sector': company_details.phishing_sector_value,
            'resilience': company_details.phishing_resilience_value - profile_evaluator_advanced.MIN_RESILIENCE,
            'risk_score': company_details.phishing_final_score
        },
        'ddos': {
            'region': company_details.ddos_region_value,
            'sector': company_details.ddos_sector_value,
            'resilience': company_details.ddos_resilience_value - profile_evaluator_advanced.MIN_RESILIENCE,
            'risk_score': company_details.ddos_final_score
        }
    }

    # Processa os dados de risco
    processed_risk_data = prepare_risk_data(risk_data)

    # Calcula cor de fundo baseado no score final
    final_score = company_details.final_score
    mapped_final_score = final_score * 10  # Converte para escala 0-100
    bg_color, text_score = get_risk_level(mapped_final_score)

    # Log final dos dados processados
    logger.info("\n=== RESUMO FINAL DOS DADOS PROCESSADOS ===")
    logger.info(f"Score Final da Empresa (0-10): {final_score:.1f}")
    logger.info(f"Nível de Risco: {text_score}")
    
    for threat, data in processed_risk_data.items():
        logger.info(f"\n{threat.upper()}:")
        logger.info(f"Risco da Região (0-5): {data['region_value']:.1f}")
        logger.info(f"Risco do Setor (0-5): {data['sector_value']:.1f}")
        logger.info(f"Resiliência (0-5): {data['resilience_value']:.1f}")
        logger.info(f"Score de Risco (0-10): {data['risk_score_normalized']:.1f}")

    tech_dimension_table = get_tech_dimension_table(company) if is_advanced else []


    # Prepara o contexto para o template
    context = {
        'company': company,
        'is_advanced': is_advanced,
        'background_color': bg_color,
        'final_score': final_score,
        'text_score': text_score,
        'risk_data': processed_risk_data,
        'insights_pos': company_details.insights_pos,
        'insights_neg': company_details.insights_neg,
        'triad_cia': [_("Confidentiality"), _("Integrity"), _("Availability")],
        'tech_dimension_table': tech_dimension_table
    }

    return render(request, current_dir + 'company_analysis_pro.html', context)


@login_required
def report_analysis_tests(request, pk = None):
    company = None
    if pk is not None:
        company = get_object_or_404(CompanyProfile, pk=pk)

    print("Iniciando report_analysis_tests")  # Debug print
    
    continent_attack_data = calcular_media_probabilidades_por_ataque_e_continente()
    sector_attack_data = calcular_media_probabilidades_por_ataque_e_setor()

    # Traduzir e converter dados de continentes
    translated_continent_data = {}
    for continent, data in continent_attack_data.items():
        translated_data = {
            'attack_types': [_(attack) for attack in data['attack_types']],
            'risks': [float(risk) if risk is not None else None for risk in data['risks']],
            'counts': data['counts']
        }
        translated_continent_data[_(continent)] = translated_data

    # Traduzir e converter dados de setores
    translated_sector_data = {}
    for sector, data in sector_attack_data.items():
        translated_data = {
            'attack_types': [_(attack) for attack in data['attack_types']],
            'risks': [float(risk) if risk is not None else None for risk in data['risks']],
            'counts': data['counts']
        }
        translated_sector_data[_(sector)] = translated_data

    context = {
        'continent_attack_data': json.dumps(translated_continent_data, cls=DjangoJSONEncoder),
        'sector_attack_data': json.dumps(translated_sector_data, cls=DjangoJSONEncoder),
        'company': company
    }

    print("Contexto final:", context)  # Debug print
    
    return render(request, current_dir + 'report_analysis_tests.html', context)

@login_required
def user_profile(request, pk = None):
    user = request.user
    company = None
    if pk is not None:
        company = get_object_or_404(CompanyProfile, pk=pk)
    context = {
        'user': user,
        'is_student': user.is_student,
        'is_instructor': user.is_instructor,
        'user_type': user.get_user_type_display(),
        'profile': user.student_profile if user.is_student else user.instructor_profile,
        'company': company
    }
    return render(request, current_dir + 'user_profile.html', context)

@login_required
@transaction.atomic
def edit_user_profile(request):
    user = request.user
    user_form = UserEditForm(instance=user)

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        if user_form.is_valid():
            user = user_form.save()
            # Handle user type change
            if user.is_student and not hasattr(user, 'student'):
                Student.objects.create(user=user)
            elif user.is_instructor and not hasattr(user, 'instructor'):
                Instructor.objects.create(user=user)
            return redirect('dashboard:user_profile')

    context = {
        'user_form': user_form,
        'user': user
    }
    return render(request, current_dir + 'edit_user_profile.html', context)

url_working_api = 'http://localhost:5000/'
url_enbis_function = 'http://localhost:5000/enbis'
url_gordon_loeb_optimal = 'http://localhost:5000/gordon_loeb_optimal/' #parametros: [probabilidade, valor asset, tipo (1 ou 2), flutuação, alpha] -> retorna EBIS, ENBIS e valor ótimo de investimento (z)
url_gordon_loeb = 'http://localhost:5000/gordon_loeb/' #parametros: [probabilidade, valor asset, valor investido, tipo (1 ou 2), flutuação, alpha] -> retorna EBIS, ENBIS e valor ótimo de investimento (z)
url_regiao_setor = 'http://localhost:5000/regiao_setor/' #parametros: [prob_região, prob_setor, peso_região] -> retorna união das probabilidades
url_media = 'http://localhost:5000/media/' #parametros: Lista [[dado, ano], [dado, ano], ...] -> retorna média dos dados
url_poisson = 'http://localhost:5000/poisson/' #parametros: probabilidade -> retorna média de ataques esperada no ano
url_impacto = 'http://localhost:5000/impact/'
url_impact_setting = 'http://localhost:5000/impact_setting/'

@login_required
def economic_planning(request, pk):
    user = request.user
    company = get_object_or_404(CompanyProfile, pk=pk)
    sand_profile, sand_created = SandboxCompany.objects.get_or_create(company = company, user = user)
    selected_attack = request.GET.get('selected_attack', None)
    asset_id = request.GET.get('asset_id', str(CompanyAssets.objects.filter(company = company).first().id)) ## para atualizar gráfico específico
    shown_asset = CompanyAssets.objects.get(id = asset_id)
    if selected_attack is not None:
        sand_asset = SandboxAsset.objects.get(asset = shown_asset, sandbox_company = sand_profile)
        sand_asset.grafico = selected_attack
        sand_asset.save()

    action = request.GET.get('action', None)

    DEFAULT_ALPHA = 0.001

    ## Testa RiskAndEconomic
    try:
        riskandeconomic = RiskAndEconomic.objects.get(company=company)
    except:
        return redirect('dashboard:company_profile_detail', pk=company.pk)
    ## RUN python3 api/api.py ##
    try:
        response = requests.get(url_working_api)
        # Tenta converter a resposta em JSON e verifica se o retorno é True
        if response.json() != True:
            return redirect("index")
    except (requests.exceptions.RequestException, ValueError) as e:
        # Captura erros de conexão ou problemas de decodificação de JSON
        return redirect("index")
    # Função auxiliar para converter Decimal para float
    def to_float(value):
        return float(value) if isinstance(value, Decimal) else value
    
    years = list(CybersecuritySpending.objects.filter(company=company).values_list('year', flat=True).distinct().order_by('-year'))
    cybersecurity_spendings = sum(float(spending.amount) for spending in CybersecuritySpending.objects.filter(company=company, year=years[0]).order_by('-year'))
    company_assets = CompanyAssets.objects.filter(company=company)
    probs = {
        'Malware': riskandeconomic.malware_succ / 100,
        'Phishing': riskandeconomic.phishing_succ / 100,
        'DDoS': riskandeconomic.ddos_succ / 100,
    }
    print(probs)
    no_attack_prob = 1
    for prob in probs.values():
        no_attack_prob *= (1 - prob)
    probs['Geral'] = 1 - no_attack_prob
    
    ##Sandbox 
    sandbox_on_request = request.GET.get('sandbox', None)
    
    if sandbox_on_request is not None:
        sand_profile.is_on = sandbox_on_request == 'true'

    #Atualizar impactos
    if action == 'impacto':
        sand_asset, sand_asset_created = SandboxAsset.objects.get_or_create(sandbox_company = sand_profile, asset = shown_asset)
        sand_attacks = SandboxAttack.objects.filter(asset = sand_asset)
        for attack in sand_attacks:
            impacto_dir = request.GET.get(f'config_direto_{attack.name}')
            impacto_ind = request.GET.get(f'config_indireto_{attack.name}')
            if impacto_dir != None:
                attack.impact_direct = impacto_dir
                attack.impact_indirect = impacto_ind
                attack.save()
    for asset in company_assets:
        sand_asset, sand_asset_created = SandboxAsset.objects.get_or_create(sandbox_company = sand_profile, asset = asset)
        geral_value = 0
        no_attack_prob = 1

        for attack, prob in probs.items():
            if prob != 0:
                sand_attack, sand_attack_created = SandboxAttack.objects.get_or_create(asset = sand_asset, name = attack)
                if sand_attack_created: ##Setando impactos do ativo
                    sand_attack.impact_direct, sand_attack.impact_indirect = requests.post(url_impact_setting,json = [asset.item, attack]).json()
                    
                if not sand_profile.is_on: ## DADOS REAIS
                    impacto = requests.post(url_impacto, json=[sand_attack.impact_direct, sand_attack.impact_indirect]).json()
                    sand_attack.name = attack
                    sand_attack.prob = prob
                    sand_attack.value = float(asset.value) * impacto 
                    sand_attack.invest = to_float(cybersecurity_spendings) if attack == "Geral" else 0

                if attack != 'Geral':
                    no_attack_prob *= 1 - prob 
                    geral_value += float(sand_attack.value) * prob
                if sand_attack_created:
                    sand_attack.save_invest = sand_attack.invest
                    sand_attack.save_prob = sand_attack.prob
                    sand_attack.save_value = sand_attack.value
                sand_attack.save() 
        sand_attack, created = SandboxAttack.objects.get_or_create(asset = sand_asset, name = 'Geral')
        sand_attack.prob = 1 - no_attack_prob
        sand_attack.value = geral_value / float(sand_attack.prob)
        sand_attack.save()
        sand_asset.save()
    if sand_profile.is_on:
        valor = 0
        probabilidade = 1
        if action == 'carregar':
            change_sand_asset, created = SandboxAsset.objects.get_or_create(asset = shown_asset, sandbox_company = sand_profile)
            change_sand_asset.alpha = change_sand_asset.saved_alpha
            change_sand_asset.save()
            change_sand_attacks = SandboxAttack.objects.filter(asset = change_sand_asset)
            for sand_attack in change_sand_attacks:
                sand_attack.invest = sand_attack.save_invest
                if sand_attack.name != 'Geral':
                    sand_attack.value = sand_attack.save_value
                    sand_attack.prob= sand_attack.save_prob
                    probabilidade *= (1 - to_float(sand_attack.prob))
                    valor += float(sand_attack.prob) * float(sand_attack.value)
                sand_attack.save()
            sand_attack = SandboxAttack.objects.get(asset = change_sand_asset, name = "Geral")
            sand_attack.prob = float(1 - probabilidade)
            sand_attack.value = valor / float(1 - probabilidade)
            sand_attack.save()

        if action in ['calcular', 'salvar']:
            change_sand_asset = SandboxAsset.objects.get(asset = shown_asset, sandbox_company = sand_profile)
            change_sand_asset.alpha = float(request.GET.get('alpha', None).replace(",", ".")) if 'alpha' in request.GET else change_sand_asset.alpha
            if change_sand_asset.alpha > 0.01:
                change_sand_asset.alpha = 0.01
            elif change_sand_asset.alpha < 0.00001:
                change_sand_asset.alpha = 0.00001

            for attack in probs.keys():
                try: ## DADOS FICTÌCIOS
                    change_sand_attack = SandboxAttack.objects.get(asset = change_sand_asset, name = attack)
                    invest = float(request.GET.get(f'investido_value_{attack}').replace(",", "."))
                    change_sand_attack.invest = invest if invest >= 0 else 0

                    if attack != "Geral":
                        probability = float(request.GET.get(f'prob_value_{attack}').replace(",", "."))/100
                        if probability >= 1:
                            probability = 0.99
                        elif probability <= 0:
                            probability = 0.01 
                        change_sand_attack.prob = probability
                        value = float(request.GET.get(f'attack_valor_{attack}').replace(",", "."))
                        change_sand_attack.value = value if value > 1000 else 1000
                        probabilidade *= (1 - float(change_sand_attack.prob))
                        valor += float(change_sand_attack.prob) * float(change_sand_attack.value)

                    if action == 'salvar':
                        change_sand_asset.saved_alpha = change_sand_asset.alpha
                        change_sand_attack.save_invest = change_sand_attack.invest
                        change_sand_attack.save_prob = change_sand_attack.prob
                        change_sand_attack.save_value = change_sand_attack.value
                    change_sand_attack.save()
                
                except:
                    pass
            change_sand_asset.save()
            change_sand_attack = SandboxAttack.objects.get(asset = change_sand_asset, name = "Geral")
            change_sand_attack.invest = float(request.GET.get(f'investido_value_Geral').replace(",", "."))
            change_sand_attack.prob = float(1 - probabilidade)
            change_sand_attack.value = valor / float(change_sand_attack.prob)
            for attack in probs.keys():
                try:
                    if action == 'salvar':
                        change_sand_attack.save_invest = float(request.GET.get(f'investido_value_{attack}').replace(",", "."))
                        change_sand_attack.save_prob = float(request.GET.get(f'prob_value_{attack}').replace(",", "."))/100
                        change_sand_attack.save_value = float(request.GET.get(f'attack_valor_{attack}').replace(",", "."))
                except:
                    pass

            change_sand_attack.save()

    ##Checa se modo avançado está desligado e faz DEFAULT_ALPHA se estiver 
    for asset in company_assets:
        sandbox_asset = SandboxAsset.objects.get(asset = asset, sandbox_company = sand_profile)
        sandbox_asset.alpha = sandbox_asset.alpha if sand_profile.is_on else DEFAULT_ALPHA
        sandbox_asset.save()

    sandbox_on_request = request.GET.get('sandbox', None)
    if sandbox_on_request is not None:
        sand_profile.is_on = sandbox_on_request == 'true'
    sand_profile.save()
    ##Finalizar envio para html
    assets_gordon_loeb = []
    flutuation = 0.025
    
    for asset in company_assets:
        block = {}
        asset.item = asset.item.capitalize()
        block['asset'] = asset
        block['investido'] = to_float(cybersecurity_spendings)
        block['ataques'] = []
        sand_asset = SandboxAsset.objects.get(asset = asset, sandbox_company = sand_profile)
        block['alpha'] = to_float(sand_asset.alpha) if sand_profile.is_on else DEFAULT_ALPHA #########
        block['grafico'] = sand_asset.grafico

        for attack in probs.keys():
            if(probs[attack] != 0):
                sand_attack = SandboxAttack.objects.get(asset=sand_asset, name=attack)
                
                otimo = requests.post(url_gordon_loeb_optimal, 
                                    json=[to_float(sand_attack.prob), 
                                        to_float(sand_attack.value), 
                                        2, 
                                        flutuation, 
                                        to_float(sand_asset.alpha)]).json()

                atual = requests.post(url_gordon_loeb, 
                                    json=[to_float(sand_attack.prob), 
                                        to_float(sand_attack.value), 
                                        to_float(sand_attack.invest), 
                                        2, 
                                        to_float(sand_asset.alpha)]).json()

                data_attack = {
                    'impacto_d': to_float(sand_attack.impact_direct),
                    'impacto_i': to_float(sand_attack.impact_indirect),
                    'investido': to_float(sand_attack.invest),
                    'valor': to_float(sand_attack.value),
                    'type': attack,
                    'prob': to_float(sand_attack.prob * 100),
                    'exp_damage': to_float(sand_attack.value) * to_float(sand_attack.prob),
                    'atual': atual,
                    'otimo': otimo,
                    'falta': otimo['z'] - to_float(sand_attack.invest),
                    'retorno': otimo['enbis'] - atual['enbis'],
                    'func': requests.post(url_enbis_function, 
                                    json=[to_float(sand_attack.prob), 
                                            to_float(sand_attack.value), 
                                            to_float(sand_asset.alpha)]).json(),
                    'min': otimo['z'] * 0.05,
                    'max': otimo['z'] * 3 if otimo['z'] * 3 > atual['z'] else atual['z'] * 1.05,
                    'efet': otimo['seg_enbis'] < atual['enbis'],
                    
                    'porc_efici': atual['enbis'] * 100 / otimo['enbis'],
                    'porc_efet_atual': atual['ebis'] * 100 / (to_float(sand_attack.value) * to_float(sand_attack.prob)),
                    'porc_efet_otimo': otimo['ebis'] * 100 / (to_float(sand_attack.value) * to_float(sand_attack.prob)),
                }
                block['ataques'].append(deepcopy(data_attack))
        assets_gordon_loeb.append(deepcopy(block))

    context = {
        'sandboxprof': sand_profile,
        'company': company,
        'assets': assets_gordon_loeb,
        'eficiencia_aceitavel': (1 - flutuation)*100,
        'year': years[0],
        'asset_id': int(asset_id)
    }
    return render(request, current_dir + 'company_economic_planning.html', context)

    
#guia/documentação abaixo

class PlatformGuideView(TemplateView):
    template_name = current_dir + 'platform_guide.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Platform Guide")
        if 'pk' in kwargs:
            context['company'] = get_object_or_404(CompanyProfile, pk=kwargs['pk'])
        return context

def error_404(request, exception):
    return render(request, 'dashboard/Templates/404.html', status=404)

def error_403(request, exception):
    return render(request, 'dashboard/Templates/403.html', status=403)