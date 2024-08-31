from django.db import models
from django.contrib.auth.models import User

class LeaveType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Тип отпуска")

    def __str__(self):
        return self.name


class Application(models.Model):
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('under_consideration', 'Under Consideration'),
        ('proposed_change', 'Proposed Change'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
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

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    patronymic = models.CharField(max_length=100, verbose_name="Отчество", null=True, blank=True)
    position = models.CharField(max_length=100, verbose_name="Должность", null=True, blank=True)

    def __str__(self):
        return self.user.username