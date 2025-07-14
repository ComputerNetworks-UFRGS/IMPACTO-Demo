# coding=utf-8

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import User, Student, RoleChangeRequest
from django.utils.translation import gettext as _
from django.contrib.auth.models import Group


class UserAdminCreationForm(UserCreationForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True,
                                   help_text="Select one Group")

    class Meta:
        model = User
        fields = ['username', 'email', 'group']

    def save(self, commit=True):
        instance = super(UserAdminCreationForm, self).save(commit=False)
        if commit:
            instance.save()
            group.user_set.add(instance)
        return instance


class Profile_Form(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class UserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label=_("Repeat the password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=_("Repeat the same password for verification.")
    )

    class Meta:
        model = User
        fields = ('username', 'name', 'email', 'institution', 'job')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'job': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'student'  # tipo de usuário padrão é o estudante
        if commit:
            user.save()
            Student.objects.get_or_create(user=user)  # cria o perfil de estudante
        return user

    # def save(self, commit=True):
    #     instance = super(UserCreationForm, self).save(commit=False)
    #     group = Group.objects.get(name=self.cleaned_data['group'])
    #     if group:
    #         if str(self.cleaned_data['group']) == 'Developer':
    #             instance.avatar = '/static/img/avatars/developer.png'
    #     if commit:
    #         instance.save()
    #         group.user_set.add(instance)
    #     return instance


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'name', 'is_active', 'is_staff']


class Autenticacao(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}))
    password = forms.CharField(label=_("Senha"),
                               widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm'}))


class RoleChangeRequestForm(forms.ModelForm):
    class Meta:
        model = RoleChangeRequest
        fields = ['requested_role', 'justification']
        labels = {
            'requested_role': _('Requested Role'),
            'justification': _('Justification'),
        }
        help_texts = {
            'justification': _('Please explain why you want to change your role.'),
        }
        widgets = {
            'requested_role': forms.Select(attrs={'class': 'form-control'}),
            'justification': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Remove current role from choices
            choices = [(k, v) for k, v in User.USER_TYPE_CHOICES if k != user.user_type]
            self.fields['requested_role'].choices = choices

