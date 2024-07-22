from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import *

urlpatterns = [
    path('menu/', menu, name='menu'),
    path('auth/', views.auth_view, name='auth'),
    path('', views.main, name = 'home'),
    path('about', views.about),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('apps/', application_list_and_create, name='apps'),
    path('gantt/', views.gantt_chart, name='gantt_chart'),
    path('administrator/', admin_dashboard_view, name='admin_dashboard'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)