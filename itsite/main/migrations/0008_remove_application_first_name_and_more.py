# Generated by Django 5.0.3 on 2024-05-21 23:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_application_remove_responsibility_position_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='application',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='application',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='application',
            name='position',
        ),
        migrations.AddField(
            model_name='application',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='applications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='application',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='profiles', to='main.application'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='position',
            field=models.CharField(default='Не указано', max_length=100, verbose_name='Должность'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='patronymic',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Отчество'),
        ),
    ]