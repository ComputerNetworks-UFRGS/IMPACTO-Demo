# coding=utf-8

from django.contrib.auth.backends import ModelBackend as BaseModelBackend

from .models import User

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import RemoteUserBackend
from django.conf import settings

class ModelBackend(BaseModelBackend):
    def authenticate(self, username=None, password=None):
        if not username is None:
            try:
                user = User.objects.get(email=username)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                pass
