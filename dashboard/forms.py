from django import forms
from accounts.models import User
from .models import (
    CompanyProfile, 
    AnnualRevenue, 
    CybersecuritySpending, 
    CompanyAssets, 
    AdvancedCompanyProfile, 
    AttackHistory, 
    Region, 
    AttackType
)
from django.utils.translation import gettext_lazy as _
from .utils import validate_and_translate_country
from django.core.exceptions import ValidationError
from django.forms.models import inlineformset_factory

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'institution', 'job', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': _('Enter username'), 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'placeholder': _('Full name'), 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': _('Enter email address'), 'class': 'form-control'}),
            'institution': forms.TextInput(attrs={'placeholder': _('Enter institution'), 'class': 'form-control'}),
            'job': forms.TextInput(attrs={'placeholder': _('Enter job title'), 'class': 'form-control'}),
            'role': forms.TextInput(attrs={'placeholder': _('Enter role'), 'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_('A user with that email already exists.'))
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_('A user with that username already exists.'))
        return username

# Placeholder forms se precisar adicionar campos específicos para Student e Instructor	
class StudentEditForm(forms.ModelForm):
    class Meta:
        model = User  # mudar se adicionar campos
        fields = []

class InstructorEditForm(forms.ModelForm):
    class Meta:
        model = User   # mudar se adicionar campos
        fields = []  
class CompanyProfileBaseEditForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = [
            'name', 'headquarters_country', 'industry_type', 'employee_count', 
            'updated_inventory', 'backup_maintenance', 'risk_prioritization'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'headquarters_country': forms.Select(attrs={'class': 'form-control'}),
            'industry_type': forms.Select(attrs={'class': 'form-control'}),
            'employee_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'updated_inventory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'backup_maintenance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'risk_prioritization': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = [
            'name', 'headquarters_country', 'industry_type', 'employee_count',
            'updated_inventory', 'backup_maintenance', 'risk_prioritization'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'headquarters_country': forms.TextInput(attrs={'class': 'form-control'}),
            'industry_type': forms.Select(attrs={'class': 'form-control'}),
            'employee_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'updated_inventory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'backup_maintenance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'risk_prioritization': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_headquarters_country(self):
        country = self.cleaned_data['headquarters_country']
        try:
            return validate_and_translate_country(country)
        except ValueError as e:
            raise forms.ValidationError(str(e))

class BaseForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        if self.cleaned_data.get('DELETE'):
            # Se o formulário está marcado para exclusão, não precisamos validar
            return cleaned_data
        
        if not self.instance.pk and not self.cleaned_data.get('DELETE', False):
            # Se é um novo registro e não está marcado para deletar, 'id' não é obrigatório
            self.errors.pop('id', None)
        return cleaned_data

class AnnualRevenueForm(BaseForm):
    class Meta:
        model = AnnualRevenue
        fields = ['year', 'amount']

    def clean(self):
        cleaned_data = super().clean()
        if self.cleaned_data.get('DELETE'):
            # Não validar se o formulário está marcado para exclusão
            return cleaned_data
        year = cleaned_data.get('year')
        company = self.instance.company if self.instance.pk else self.data.get('company')

        if year and company:
            existing = AnnualRevenue.objects.filter(company=company, year=year)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                self.add_error('year', _('An entry for this year already exists.'))
        return cleaned_data

class CybersecuritySpendingForm(BaseForm):
    class Meta:
        model = CybersecuritySpending
        fields = ['year', 'amount']

    def clean(self):
        cleaned_data = super().clean()
        if self.cleaned_data.get('DELETE'):
            # Não validar se o formulário está marcado para exclusão
            return cleaned_data
        year = cleaned_data.get('year')
        company = self.instance.company if self.instance.pk else self.data.get('company')

        if year and company:
            existing = CybersecuritySpending.objects.filter(company=company, year=year)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                self.add_error('year', _('An entry for this year already exists.'))
        return cleaned_data

class CompanyAssetsForm(BaseForm):
    class Meta:
        model = CompanyAssets
        fields = ['item', 'value']

    def clean(self):
        cleaned_data = super().clean()
        if self.cleaned_data.get('DELETE'):
            # Não validar se o formulário está marcado para exclusão
            return cleaned_data
        item = cleaned_data.get('item')
        company = self.instance.company if self.instance.pk else self.data.get('company')

        if item and company:
            existing = CompanyAssets.objects.filter(company=company, item=item)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                self.add_error('item', _('An entry for this item already exists.'))
        return cleaned_data

AnnualRevenueFormSet = inlineformset_factory(
    CompanyProfile,
    AnnualRevenue,
    form=AnnualRevenueForm,
    extra=1,
    can_delete=True
)

CybersecuritySpendingFormSet = inlineformset_factory(
    CompanyProfile,
    CybersecuritySpending,
    form=CybersecuritySpendingForm,
    extra=1,
    can_delete=True
)

CompanyAssetsFormSet = inlineformset_factory(
    CompanyProfile,
    CompanyAssets,
    form=CompanyAssetsForm,
    extra=1,
    can_delete=True
)

class AdvancedCompanyProfileForm(CompanyProfileForm):
    class Meta(CompanyProfileForm.Meta):
        model = AdvancedCompanyProfile
        fields = CompanyProfileForm.Meta.fields + [
            'company_size', 'remote_work_rate', 'global_presence',
            'authentication_factors', 'cloud_solution_type', 'it_system_monitoring',
            'periodic_system_updates', 'data_encryption_in_storage',
            'data_encryption_in_transit', 'vpn_for_remote_access',
            'cybersecurity_awareness_and_training', 'documented_response_plan',
            'response_plan_update', 'operational_recovery_capacity',
            'credentials_maintenance', 'vulnerability_identification',
            'network_systems_traffic_monitoring', 'threat_identification_process',
            'it_records_presence', 'antivirus', 'firewall',
            'intrusion_detection_system', 'endpoint_detection_and_response',
            'it_security_team'
        ]
        widgets = CompanyProfileForm.Meta.widgets.copy()
        # Adicione widgets adicionais para AdvancedCompanyProfile
        widgets.update({
            'company_size': forms.Select(attrs={'class': 'form-control'}),
            'remote_work_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'global_presence': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'authentication_factors': forms.NumberInput(attrs={'class': 'form-control'}),
            'cloud_solution_type': forms.Select(attrs={'class': 'form-control'}),
            'it_system_monitoring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'periodic_system_updates': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'data_encryption_in_storage': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'data_encryption_in_transit': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'vpn_for_remote_access': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cybersecurity_awareness_and_training': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'documented_response_plan': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'response_plan_update': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'operational_recovery_capacity': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'credentials_maintenance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'vulnerability_identification': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'network_systems_traffic_monitoring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'threat_identification_process': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'it_records_presence': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'antivirus': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'firewall': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'intrusion_detection_system': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'endpoint_detection_and_response': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'it_security_team': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        })

    # se tiver mais validações personalizadas adicionais, fica aqui

class AttackHistoryForm(forms.ModelForm):
    class Meta:
        model = AttackHistory
        fields = ['attack_type', 'year', 'count']
        widgets = {
            'attack_type': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1900, 'max': '2100' }),
            'count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def clean(self):
        cleaned_data = super().clean()
        attack_type = cleaned_data.get('attack_type')
        year = cleaned_data.get('year')

        # Não tentamos acessar self.instance.company aqui
        # A validação de unicidade será feita no nível do formset ou view

        return cleaned_data

AttackHistoryFormSet = inlineformset_factory(
    AdvancedCompanyProfile,
    AttackHistory,
    form=AttackHistoryForm,
    extra=1,
    can_delete=True
)