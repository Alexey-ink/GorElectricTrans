from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from datetime import datetime
import calendar
from datetime import timedelta
from .models import VacationSlot, Application
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
    if request.user.groups.filter(name='Admin (not superuser)').exists():
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


def vacation_slots(request):
    # Получаем выбранный год и месяц из GET параметров, если они есть
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))

    # Получаем все дни месяца
    days_in_month = calendar.monthrange(year, month)[1]

    # Получаем слоты отпуска для выбранного месяца
    slots = VacationSlot.objects.filter(date__year=year, date__month=month)

    # Создаем словарь с количеством свободных мест по дням
    slots_dict = {slot.date.day: slot.available_slots for slot in slots}

    # Список дней месяца с цветовой меткой
    days_with_colors = []
    for day in range(1, days_in_month + 1):
        available_slots = slots_dict.get(day, 3)  # По умолчанию считаем, что все слоты свободны (3 места)
        day_color = get_day_color(available_slots)
        days_with_colors.append({'day': day, 'color': day_color})

    # Генерируем список месяцев для выпадающего списка
    months = list(range(1, 13))

    # Рендеринг шаблона с данными
    return render(request, 'main/calendar.html', {
        'year': year,
        'month': month,
        'days_with_colors': days_with_colors,
        'months': months,
    })


def get_day_color(available_slots):
    # Логика для выбора цвета в зависимости от количества доступных мест
    if available_slots == 0:
        return 'no-spots'  # Красный - нет мест
    elif available_slots < 3:
        return 'few-spots'  # Желтый - меньше 3 мест
    else:
        return 'free'  # Зеленый - все места доступны


def reduce_available_slots(start_date, end_date):
    # Пробегаем по всем дням отпуска с start_date до end_date
    for single_date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
        # Ищем запись в модели VacationSlot для конкретного дня
        vacation_slot = VacationSlot.objects.filter(date=single_date).first()

        if vacation_slot and vacation_slot.available_slots > 0:
            # Уменьшаем количество доступных мест на 1
            vacation_slot.available_slots -= 1
            vacation_slot.save()
        else:
            # Если на этот день нет слота или слоты уже заняты
            print(f"Нет доступных слотов для {single_date}")


@login_required
def approve_application(request, application_id):
    # Получаем заявку по ID
    application = get_object_or_404(Application, id=application_id)

    if request.method == 'POST':
        # Утверждаем заявку
        application.status = 'approved'
        application.save()

        # Вызываем функцию для уменьшения доступных мест
        reduce_available_slots(application.start_date, application.end_date)

        # Сообщение об успешном утверждении
        messages.success(request, 'Заявка утверждена, свободные места обновлены.')

        # Перенаправляем на админскую панель после POST-запроса
        return redirect('admin_dashboard')

    # Если метод не POST, можно вернуть шаблон с деталями заявки
    return render(request, 'main/approve_application.html', {'application': application})


@login_required
def reject_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    if request.method == 'POST':
        application.status = 'rejected'
        application.save()
        messages.success(request, 'Заявка отклонена.')
    return redirect('admin_dashboard')  # Перенаправление на страницу списка заявок


from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.shortcuts import render


@login_required
def gantt_chart(request):
    current_year = now().year
    # Use 'select_related' to optimize database queries and fetch 'user.position'
    leaves = Application.objects.select_related('user', 'leave_type', 'user__position').filter(
        start_date__year=current_year
    )

    context = {
        'leaves': leaves,
        # We can access the position directly via 'leaves' as we fetched it with select_related
        'positions': {leave.user: leave.user.position for leave in leaves}
    }

    return render(request, 'main/gantt_chart.html', context)

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