from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import *

urlpatterns = [
    path('menu/', menu, name='menu'),
    path('auth/', views.auth_view, name='auth'),
    path('', views.auth_view, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('apps/', application_list_and_create, name='apps'),
    path('administrator/', admin_dashboard_view, name='admin_dashboard'),
    path('approve/<int:application_id>/', views.approve_application, name='approve_application'),
    path('reject/<int:application_id>/', views.reject_application, name='reject_application'),
    path('change_dates/<int:application_id>/', views.change_application_dates, name='change_application_dates'),
    path('user_apps/', views.user_apps, name='user_apps'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)