from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser  # Импортируйте вашу кастомную модель пользователя

class CustomUserAdmin(UserAdmin):
    # Настройте отображение вашей модели в админке, если это необходимо
    model = CustomUser
    list_display = ['username', 'email', 'is_staff', 'is_active', 'position']
    list_filter = ['is_staff', 'is_active', 'groups']

admin.site.register(CustomUser, CustomUserAdmin)