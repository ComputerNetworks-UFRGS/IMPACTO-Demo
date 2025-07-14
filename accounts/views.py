# coding=utf-8
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import (
    CreateView, TemplateView, UpdateView, FormView
)
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils.translation import gettext as _
from .models import User, RoleChangeRequest
from .forms import *


@login_required
def index(request):
    profile_form = Profile_Form(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)
    if request.method == 'POST':
        if request.POST.get('profile'):
            profile_form = Profile_Form(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, _('Profile has been updated!'))
            else:
                messages.error(request, _('Input Error'))
        if request.POST.get('password'):
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, _('Password has been changed!'))
            else:
                messages.error(request, _('Input Error'))
    context = {'profile_form': profile_form,
               'password_form': password_form}
    return render(request, 'accounts/Templates/index.html', context)


@login_required
def request_role_change(request):
    # Check if user already has a pending request
    existing_request = RoleChangeRequest.objects.filter(
        user=request.user, 
        status='pending'
    ).first()
    
    if existing_request:
        messages.warning(request, _('You already have a pending role change request.'))
        return redirect('dashboard:user_profile')
    
    if request.method == 'POST':
        form = RoleChangeRequestForm(request.POST, user=request.user)
        if form.is_valid():
            role_request = form.save(commit=False)
            role_request.user = request.user
            role_request.current_role = request.user.user_type
            role_request.save()
            messages.success(request, _('Your role change request has been submitted successfully!'))
            return redirect('dashboard:user_profile')
    else:
        form = RoleChangeRequestForm(user=request.user)
    
    context = {'form': form}
    return render(request, 'accounts/Templates/role_change_request.html', context)


@staff_member_required
def manage_role_requests(request):
    pending_requests = RoleChangeRequest.objects.filter(status='pending')
    all_requests = RoleChangeRequest.objects.all()[:50]  # Last 50 requests
    
    context = {
        'pending_requests': pending_requests,
        'all_requests': all_requests,
    }
    return render(request, 'accounts/Templates/manage_role_requests.html', context)


@staff_member_required
def approve_role_request(request, request_id):
    role_request = RoleChangeRequest.objects.get(id=request_id)
    notes = request.POST.get('admin_notes', '')
    
    role_request.approve(request.user, notes)
    messages.success(request, _('Role change request for %(username)s has been approved.') % {'username': role_request.user.username})
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('accounts:manage_role_requests')


@staff_member_required
def reject_role_request(request, request_id):
    role_request = RoleChangeRequest.objects.get(id=request_id)
    notes = request.POST.get('admin_notes', '')
    
    role_request.reject(request.user, notes)
    messages.success(request, _('Role change request for %(username)s has been rejected.') % {'username': role_request.user.username})
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('accounts:manage_role_requests')


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/Templates/index.html'
