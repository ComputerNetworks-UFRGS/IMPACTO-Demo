# coding=utf-8

import re

from django.db import models
from django.core.validators import MaxLengthValidator, RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.db import transaction


class User(AbstractBaseUser, PermissionsMixin):
    # Campos básicos do usuário
    username = models.CharField(
        _("Username"), 
        max_length=30, 
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message=_("Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters."),
                code='invalid'
            )
        ],
        help_text=_("A username that will be used for identification and login on the platform."),
    )
    name = models.CharField(_("Name"), max_length=100, blank=True)
    email = models.EmailField(_("E-mail"), unique=True)
    is_staff = models.BooleanField(_("Staff Status"), default=False)
    is_active = models.BooleanField(_("Active Status"), default=True)
    date_joined = models.DateTimeField(_("Date Joined"), auto_now_add=True)
    institution = models.CharField(_("Institution"), max_length=100, blank=True)
    job = models.CharField(_("Job"), max_length=100, blank=True)
    role = models.CharField(_("Role"), max_length=100, blank=True)

    # Campo para distinguir entre tipos de usuário
    USER_TYPE_CHOICES = [
        ('student', _('Student')),
        ('instructor', _('Instructor')),
    ]
    user_type = models.CharField(
        _("User Type"),
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='student',
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.name or self.username

    def get_short_name(self):
        return self.name.split(" ")[0] if self.name else self.username

    def user_has_role(self, role):
        return self.role == role

    # Propriedades para verificar o tipo de usuário
    @property
    def is_student(self):
        return self.user_type == 'student'

    @property
    def is_instructor(self):
        return self.user_type == 'instructor'

    # Propriedades para acessar perfis específicos
    @property
    def student_profile(self):
        if self.is_student:
            return self.student
        return None

    @property
    def instructor_profile(self):
        if self.is_instructor:
            return self.instructor
        return None

    def save(self, *args, **kwargs):
        creating = self._state.adding
        super().save(*args, **kwargs)
        if creating and self.user_type == 'student':
            Student.objects.get_or_create(user=self)

class Student(models.Model):
    # Modelo para armazenar informações específicas de estudantes
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # Outros campos e modelos aqui para o estudante

    def __str__(self):
        return f"Student: {self.user.username}"

class Instructor(models.Model):
    # Modelo para armazenar informações específicas de instrutores
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # Outros campos e modelos aqui para o instrutor

    def __str__(self):
        return f"Instructor: {self.user.username}"

class RoleChangeRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_requests')
    requested_role = models.CharField(_("Requested Role"), max_length=10, choices=User.USER_TYPE_CHOICES)
    current_role = models.CharField(_("Current Role"), max_length=10, choices=User.USER_TYPE_CHOICES)
    justification = models.TextField(_("Justification"), help_text=_("Please explain why you want to change your role"))
    status = models.CharField(_("Status"), max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')
    admin_notes = models.TextField(_("Admin Notes"), blank=True)

    class Meta:
        verbose_name = _("Role Change Request")
        verbose_name_plural = _("Role Change Requests")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.current_role} to {self.requested_role} ({self.status})"

    def approve(self, admin_user, notes=""):
        with transaction.atomic():
            self.status = 'approved'
            self.reviewed_by = admin_user
            self.admin_notes = notes
            self.save()
            
            # Change user role
            old_role = self.user.user_type
            self.user.user_type = self.requested_role
            self.user.save()
            
            # Create instructor profile if changing to instructor
            if self.requested_role == 'instructor':
                Instructor.objects.get_or_create(user=self.user)

    def reject(self, admin_user, notes=""):
        self.status = 'rejected'
        self.reviewed_by = admin_user
        self.admin_notes = notes
        self.save()