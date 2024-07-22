from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect

from .models import *
from django.contrib.auth import login, authenticate, logout
from .forms import *
from django.utils.timezone import now

# Create your views here.

menu = ["О сайте", "Добавить статью", "Обратная связь", "Войти"]

def main(request):
    return render(request, 'main/base.html', {'menu': menu, 'title': 'Главная страница'})

def about(request):
    return render(request, 'main/about.html', {'menu': menu, 'title': 'О сайте'})

def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не НАЙДЕНА</h1>')


def register(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Проверяем, существует ли уже профиль для пользователя
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'patronymic': form.cleaned_data.get('patronymic'),
                    'position': form.cleaned_data.get('position')
                }
            )
            if not created:
                # Если профиль уже существует, обновляем его поля
                profile.patronymic = form.cleaned_data.get('patronymic')
                profile.position = form.cleaned_data.get('position')
                profile.save()

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('apps')
    else:
        form = RegisterUserForm()
    return render(request, 'main/register.html', {'form': form})
def logout_view(request):
    logout(request)
    return redirect('home')  # Перенаправление на главную страницу после выхода

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import LoginForm

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if username == 'admin':
                    return redirect('admin_dashboard')  # Перенаправление на страницу admin
                else:
                    return redirect('apps')  # Перенаправление на домашнюю страницу после успешного входа
            else:
                form.add_error(None, 'Неверный логин или пароль')
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {'form': form})
def application_list_and_create(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            return redirect('apps')  # Перенаправление на ту же страницу после отправки формы
    else:
        form = ApplicationForm()

    applications = Application.objects.filter(user=request.user)
    return render(request, 'main/application.html', {'form': form, 'applications': applications})

@login_required
def gantt_chart(request):
    current_year = now().year
    leaves = Application.objects.select_related('user', 'leave_type').filter(
        start_date__year=current_year
    )
    context = {
        'leaves': leaves
    }
    return render(request, 'main/gantt_chart.html', context)

@login_required
def admin_dashboard_view(request):
    if request.user.username != 'admin':
        return redirect('apps')  # Перенаправление, если пользователь не администратор

    employees = UserProfile.objects.select_related('user').all()
    applications = Application.objects.select_related('user', 'leave_type').all()

    employee_data = []
    for employee in employees:
        user_applications = applications.filter(user=employee.user)
        for app in user_applications:
            employee_data.append({
                'username': employee.user.username,
                'last_name': employee.user.last_name,
                'first_name': employee.user.first_name,
                'position': employee.position,
                'start_date': app.start_date,
                'end_date': app.end_date,
                'leave_type': app.leave_type.name
            })

    return render(request, 'main/admin_dashboard.html', {'employee_data': employee_data})

# views.py
def auth_view(request):
    login_form = LoginForm(request=request, data=request.POST if request.method == 'POST' and 'login' in request.POST else None)
    register_form = RegisterUserForm(request.POST if request.method == 'POST' and 'register' in request.POST else None)

    if request.method == 'POST':
        if 'login' in request.POST and login_form.is_valid():
            user = login_form.get_user()
            if user:
                login(request, user)
                return redirect('apps')
        elif 'register' in request.POST and register_form.is_valid():
            user = register_form.save()
            profile = UserProfile(user=user, patronymic=register_form.cleaned_data.get('patronymic'), position=register_form.cleaned_data.get('position'))
            profile.save()
            login(request, user)
            return redirect('apps')

    context = {
        'login_form': login_form,
        'register_form': register_form
    }
    return render(request, 'main/auth.html', context)

def menu(request):
    # Логика вашего представления здесь
    return render(request, 'main/menu.html')