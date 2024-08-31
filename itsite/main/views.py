from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404

from .models import *
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import login as auth_login
from .forms import *
from django.utils.timezone import now

# Create your views here.

def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не НАЙДЕНА</h1>')

def logout_view(request):
    logout(request)
    return redirect('home')  # Перенаправление на главную страницу после выхода

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


def admin_dashboard_view(request):

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
                'leave_type': app.leave_type.name,
                'application_id': app.id,
                'app_status': app.status,
                'patronymic': employee.patronymic
            })

    return render(request, 'main/admin_dashboard.html', {'employee_data': employee_data})

@login_required(login_url='auth')
def menu(request):
    # Проверяем, состоит ли пользователь в группе "Администраторы без суперпользовательских прав"
    if request.user.groups.filter(name='Administrator (not superuser)').exists():
        return render(request, 'main/admin_menu.html')
    else:
        # Если пользователь не администратор, показываем обычное меню
        return render(request, 'main/menu.html')


def auth_view(request):
    if request.user.is_authenticated:
        return redirect('menu')  # Перенаправление на страницу меню, если пользователь уже авторизован

    login_form = AuthenticationForm(request,
                                    data=request.POST if request.method == 'POST' and 'login' in request.POST else None)
    register_form = RegisterUserForm(request.POST if request.method == 'POST' and 'register' in request.POST else None)

    if request.method == 'POST':
        if 'login' in request.POST and login_form.is_valid():
            user = login_form.get_user()
            auth_login(request, user)
            return redirect('menu')

        elif 'register' in request.POST and register_form.is_valid():
            user = register_form.save()

            # Создаем профиль пользователя или получаем существующий
            profile, created = UserProfile.objects.get_or_create(user=user)

            # Обновляем поля профиля
            profile.patronymic = register_form.cleaned_data.get('patronymic')
            profile.position = register_form.cleaned_data.get('position')

            # Отладочный вывод перед сохранением
            print(f"Saving Profile: {profile.patronymic}, {profile.position}")

            # Сохраняем профиль
            profile.save()

            # Проверка, что данные сохранены
            saved_profile = UserProfile.objects.get(user=user)
            print(f"Profile in DB: {saved_profile.patronymic}, {saved_profile.position}")

            auth_login(request, user)
            return redirect('menu')

    context = {
        'login_form': login_form,
        'register_form': register_form
    }
    return render(request, 'main/auth.html', context)


@login_required
def approve_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    if request.method == 'POST':
        application.status = 'approved'
        application.save()
        messages.success(request, 'Заявка утверждена.')
    return redirect('admin_dashboard')  # Перенаправление на страницу списка заявок


@login_required
def reject_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    if request.method == 'POST':
        application.status = 'rejected'
        application.save()
        messages.success(request, 'Заявка отклонена.')
    return redirect('admin_dashboard')  # Перенаправление на страницу списка заявок


@login_required
def change_application_dates(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    if request.method == 'POST':
        # Получение данных из формы
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        comment = request.POST.get('comment')

        # Обновление полей заявки
        application.start_date = start_date
        application.end_date = end_date
        application.status = 'proposed_change'
        application.save()

        messages.success(request, 'Заявка обновлена.')
        return redirect('admin_dashboard')  # Перенаправление на страницу списка заявок

    return render(request, 'main/change_dates.html', {'application': application})


@login_required
def user_apps(request):
    # Получаем заявки для текущего пользователя
    applications = Application.objects.filter(user=request.user)

    context = {
        'applications': applications
    }
    return render(request, 'main/user_apps.html', context)
