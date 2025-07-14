from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import login, logout
from django.contrib.auth.views import LogoutView, LoginView
from core import views
from core import settings
from .views import MyLoginView, UserCreate
from accounts.views import User
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls import handler404, handler403

#from django.conf.urls.i18n import i18n_patterns
current_dir = 'core/Templates/'
admin.autodiscover()

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.index, name='index'),
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path("dashboard/", include(("dashboard.urls"), namespace="dashboard")),
    path("accounts/", include(("accounts.urls"), namespace="accounts")),
    path('register/', UserCreate.as_view(template_name=current_dir +'login/register.html'),name='register'),
    path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
    path('login/', MyLoginView.as_view(template_name=current_dir +'login/login.html'),name='login'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'dashboard.views.error_404'
handler403 = 'dashboard.views.error_403'
