from django.db import migrations

def add_initial_data(apps, schema_editor):
    LeaveType = apps.get_model('main', 'LeaveType')
    Application = apps.get_model('main', 'Application')
    Position = apps.get_model('main', 'Position')

    # Добавляем типы отпусков
    leave_types = [
        ('ежегодный оплачиваемый', 'Ежегодный оплачиваемый'),
        ('без сохранения заработной платы', 'Без сохранения заработной платы'),
        ('учебный', 'Учебный'),
        ('по родам, кормлению и уходу за ребенком', 'По родам, кормлению и уходу за ребенком'),
        ('командировка', 'Командировка'),
    ]
    for code, name in leave_types:
        LeaveType.objects.create(name=code)

    # Добавляем должности
    positions = [
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
    for code, name in positions:
        Position.objects.create(name=code)

    # Статусы не добавляются в базу напрямую, они используются как choices в модели Application.

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),  # Обновите на соответствующую миграцию
    ]

    operations = [
        migrations.RunPython(add_initial_data),
    ]
