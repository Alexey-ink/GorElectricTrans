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


from django.shortcuts import render
from .models import CustomUser, Application

def admin_dashboard_view(request):
    # Получаем всех сотрудников из модели CustomUser
    employees = CustomUser.objects.select_related('position').all()

    # Получаем все заявки на отпуск
    applications = Application.objects.select_related('user', 'leave_type').all()

    employee_data = []
    for employee in employees:
        # Фильтруем заявки по текущему пользователю
        user_applications = applications.filter(user=employee)
        for app in user_applications:
            employee_data.append({
                'username': employee.username,
                'last_name': employee.last_name,
                'first_name': employee.first_name,
                'position': employee.position.get_name_display,
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

            # Обновляем поля пользователя (CustomUser)
            user.patronymic = register_form.cleaned_data.get('patronymic')
            user.position = register_form.cleaned_data.get('position')

            # Отладочный вывод перед сохранением
            print(f"Saving User: {user.patronymic}, {user.position}")

            # Сохраняем пользователя
            user.save()

            # Проверка, что данные сохранены
            saved_user = CustomUser.objects.get(username=user.username)
            print(f"User in DB: {saved_user.patronymic}, {saved_user.position}")

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


def settings_view(request):
    if not request.user.groups.filter(name='Administrator (not superuser)').exists():
        return redirect('menu')  # Ограничение доступа к странице настроек только для суперпользователей

    vacation_times = VacationTime.objects.select_related('position', 'leave_type').all()

    if request.method == 'POST':
        for vacation_time in vacation_times:
            field_name = f"days_{vacation_time.id}"
            if field_name in request.POST:
                new_days = request.POST[field_name]
                if new_days.isdigit():
                    vacation_time.number_of_days = int(new_days)
                    vacation_time.save()

                    # Найдите и обновите соответствующий UserLeaveBalance
                    user_leave_balances = UserLeaveBalance.objects.filter(leave_type=vacation_time.leave_type)
                    for balance in user_leave_balances:
                        balance.remaining_days = vacation_time.number_of_days
                        balance.save()

    context = {
        'vacation_times': vacation_times,
    }
    return render(request, 'main/settings.html', context)