# coding=utf-8

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Student, Instructor
from .forms import UserAdminCreationForm, UserAdminForm

class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = 'Student Profile'

class InstructorInline(admin.StackedInline):
    model = Instructor
    can_delete = False
    verbose_name_plural = 'Instructor Profile'

class UserAdmin(BaseUserAdmin):
    add_form = UserAdminCreationForm
    add_fieldsets = (
        (None, {
            'fields': ('username', 'email', 'user_type', 'password1', 'password2')
        }),
    )
    form = UserAdminForm
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
        (_('Personal info'), {
            'fields': ('name', 'institution', 'job', 'role')
        }),
        (_('User type'), {
            'fields': ('user_type',)
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {
            'fields': ('last_login',)
        }),
    )
    readonly_fields = ('last_login', 'date_joined')
    list_display = ['username', 'name', 'email', 'user_type', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['user_type', 'is_staff', 'is_superuser', 'is_active', 'groups']
    search_fields = ['username', 'name', 'email']

    def get_inlines(self, request, obj=None):
        if obj:
            if obj.user_type == 'student':
                return [StudentInline]
            elif obj.user_type == 'instructor':
                return [InstructorInline]
        return []

admin.site.register(User, UserAdmin)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_email', 'get_name']
    search_fields = ['user__username', 'user__email', 'user__name']

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def get_name(self, obj):
        return obj.user.name
    get_name.short_description = 'Name'

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_email', 'get_name']
    search_fields = ['user__username', 'user__email', 'user__name']

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def get_name(self, obj):
        return obj.user.name
    get_name.short_description = 'Name'