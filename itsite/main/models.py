from django.db import models
from django.contrib.auth.models import User

class LeaveType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Тип отпуска")

    def __str__(self):
        return self.name

class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='applications')
    start_date = models.DateField(verbose_name="Дата начала отпуска")
    end_date = models.DateField(verbose_name="Дата окончания отпуска")

    def __str__(self):
        return f"{self.user.username} - {self.leave_type.name} - {self.start_date} to {self.end_date}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    patronymic = models.CharField(max_length=100, verbose_name="Отчество", null=True, blank=True)
    position = models.CharField(max_length=100, verbose_name="Должность", null=True, blank=True)

    def __str__(self):
        return self.user.username