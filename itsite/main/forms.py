from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import *

class RegisterUserForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Имя', widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия', widget=forms.TextInput(attrs={'class': 'form-input'}))
    patronymic = forms.CharField(max_length=30, required=True, label='Отчество', widget=forms.TextInput(attrs={'class': 'form-input'}))
    position = forms.CharField(max_length=100, required=True, label='Должность', widget=forms.TextInput(attrs={'class': 'form-input'}))
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'patronymic', 'position', 'email', 'password1', 'password2')
class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['leave_type', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'leave_type': forms.Select(attrs={'class': 'form-control'})
        }
        labels = {
            'leave_type': 'Тип отпуска',  # Указание метки для поля leave_type
        }
class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
