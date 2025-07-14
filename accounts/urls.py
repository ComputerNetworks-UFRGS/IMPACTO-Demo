# coding=utf-8

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile', views.index, name='index'),
    path('request-role-change/', views.request_role_change, name='request_role_change'),
    path('manage-role-requests/', views.manage_role_requests, name='manage_role_requests'),
    path('approve-role-request/<int:request_id>/', views.approve_role_request, name='approve_role_request'),
    path('reject-role-request/<int:request_id>/', views.reject_role_request, name='reject_role_request'),
]
