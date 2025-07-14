from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from django.utils.decorators import method_decorator
from . import views
from .views import add_company_profile, change_language
from django.conf.urls.i18n import i18n_patterns
from .views import PlatformGuideView

app_name = 'dashboard'

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:pk>", views.index, name="index_company"),

    path('change_language/<str:language_code>/', views.change_language, name='change_language'),

    path('company-profile/add/', views.add_company_profile, name='add_company_profile'),
    path('company-profile-advanced/add/', views.add_advanced_company_profile, name='add_advanced_company_profile'),
    path('company-profile/<int:pk>/', views.company_profile_detail, name='company_profile_detail'),
    path('company-profile/', views.company_profile_list, name='company_profile_list'),
    path('company-profile/<str:action>/', views.company_profile_list, name='company_profile_list_redirect'),
    path('company-profile/<int:pk>/edit/', views.edit_company_profile, name='edit_company_profile'),
    path('company-profile/<int:pk>/analysis/', views.company_analysis, name='company_analysis'),
    path('company-profile/<int:pk>/analysis_pro/', views.company_analysis_pro, name='company_analysis_pro'),

    path('company/<int:pk>/copy/', views.copy_company_profile, name='copy_company_profile'),


    path('company-profile/<int:pk>/economic-planning/', views.economic_planning, name='economic_planning'),

    path('my-company-copies/', views.user_company_copies, name='user_company_copies'),

    path('report-database-analysis/', views.report_analysis_tests, name='report_analysis_tests'),
    path('report-database-analysis/<int:pk>', views.report_analysis_tests, name='report_analysis_tests_company'),
    
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/<int:pk>', views.user_profile, name='user_profile_company'),
    path('profile/edit/', views.edit_user_profile, name='edit_user_profile'),

    path('platform-guide/', PlatformGuideView.as_view(), name='platform_guide'),
    path('platform-guide/<int:pk>', PlatformGuideView.as_view(), name='platform_guide_company'),

]#+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
