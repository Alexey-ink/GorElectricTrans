from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save, post_migrate  # Импортируем необходимые сигналы


class LeaveType(models.Model):
    ANNUAL_PAID = 'ежегодный оплачиваемый'
    UNPAID = 'без сохранения заработной платы'
    STUDY = 'учебный'
    MATERNITY = 'по родам, кормлению и уходу за ребенком'
    BUSINESS_TRIP = 'командировка'

    LEAVE_TYPE_CHOICES = [
        (ANNUAL_PAID, 'Ежегодный оплачиваемый'),
        (UNPAID, 'Без сохранения заработной платы'),
        (STUDY, 'Учебный'),
        (MATERNITY, 'По родам, кормлению и уходу за ребенком'),
        (BUSINESS_TRIP, 'Командировка'),
    ]

    name = models.CharField(max_length=100, choices=LEAVE_TYPE_CHOICES, verbose_name="Тип отпуска")

    def __str__(self):
        return self.name


class Application(models.Model):
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('under_consideration', 'Under Consideration'),
        ('proposed_change', 'Proposed Change'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    leave_type = models.ForeignKey('LeaveType', on_delete=models.CASCADE, related_name='applications')
    start_date = models.DateField(verbose_name="Дата начала отпуска")
    end_date = models.DateField(verbose_name="Дата окончания отпуска")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='under_consideration',
        verbose_name="Статус"
    )

    def __str__(self):
        return f"{self.user.username} - {self.leave_type.name} - {self.start_date} to {self.end_date} - {self.get_status_display()}"


class CustomUser(AbstractUser):
    patronymic = models.CharField(max_length=150, blank=True, null=True)
    position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True, related_name='users',
                                 verbose_name="Должность")

    def __str__(self):
        return self.username


# Класс Position для хранения должностей
class Position(models.Model):
    POSITION_CHOICES = [
        ('administrator', 'Администратор'),
        ('trolleybus_driver', 'Водитель троллейбуса'),
        ('tram_driver', 'Водитель трамвая'),
        ('controller', 'Контроллер'),
        ('accountant', 'Бухгалтер'),
        ('mechanic', 'Механик'),
        ('intern', 'Стажер'),
        ('director', 'Директор'),
        ('electrician', 'Электрик'),
        ('cleaner', 'Уборщик'),
    ]

    name = models.CharField(
        max_length=40,
        choices=POSITION_CHOICES,
        default='administrator',
        verbose_name="Должность"
    )

    def __str__(self):
        return self.get_name_display()


# Класс VacationTime для хранения времени отпуска в зависимости от должности
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class VacationTime(models.Model):
    number_of_days = models.IntegerField(verbose_name="Количество дней отпуска")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='vacation_times')
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='vacation_times')

    def __str__(self):
        return f"{self.position.name} - {self.leave_type.name}: {self.number_of_days} дней"

    @classmethod
    def initialize_default_vacation_days(cls):
        for position in Position.objects.all():
            for leave_type in LeaveType.objects.all():
                cls.objects.get_or_create(position=position, leave_type=leave_type, defaults={'number_of_days': 30})


# Сигнал для инициализации значений по умолчанию после выполнения миграций
# @receiver(post_migrate)
# def create_default_vacation_days(sender, **kwargs):
# sender.name == 'main':  # Замените 'your_app_name' на название вашего приложения
 #       VacationTime.initialize_default_vacation_days()


class UserLeaveBalance(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='user_leave_balances')
    remaining_days = models.IntegerField(default=30, verbose_name="Оставшиеся дни отпуска")

    def __str__(self):
        return f"{self.user.username} - {self.leave_type.name}: {self.remaining_days} дней"


@receiver(post_save, sender=CustomUser)
def create_leave_balances(sender, instance, created, **kwargs):
    if created:
        for leave_type in LeaveType.objects.all():
            UserLeaveBalance.objects.create(user=instance, leave_type=leave_type)


@receiver(post_save, sender=Application)
def update_leave_balance(sender, instance, **kwargs):
    if instance.status == 'approved':
        leave_balance = UserLeaveBalance.objects.get(user=instance.user, leave_type=instance.leave_type)
        # Считаем количество дней, которые пользователь берет в отпуск
        used_days = (instance.end_date - instance.start_date).days + 1
        leave_balance.remaining_days -= used_days
        leave_balance.save()


