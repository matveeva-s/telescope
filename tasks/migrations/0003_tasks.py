# Generated by Django 3.1.2 on 2021-05-09 13:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0002_frame_point_task_tledata_trackingdata_trackpoint'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.SmallIntegerField(choices=[(1, 'Создано'), (2, 'Получена телескопом'), (3, 'Выполнена'), (4, 'Не удалось выполнить')], default=1, verbose_name='Статус')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('task_type', models.SmallIntegerField(choices=[(1, 'Снимки по точкам'), (2, 'Трэкинг по точкам'), (3, 'Снимки по TLE')], verbose_name='Тип задания')),
                ('start_dt', models.DateTimeField(verbose_name='Дата и время начала наблюдения')),
                ('end_dt', models.DateTimeField(verbose_name='Дата и время конца наблюдения')),
                ('author', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор задания')),
                ('telescope', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='tasks.telescope', verbose_name='Телескоп')),
            ],
            options={
                'verbose_name': 'Задание',
                'verbose_name_plural': 'Задания',
            },
        ),
        migrations.CreateModel(
            name='TrackPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alpha', models.FloatField(verbose_name='Азимут')),
                ('beta', models.FloatField(verbose_name='Высота')),
                ('dt', models.DateTimeField(verbose_name='Время снимка')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='track_points', to='tasks.task', verbose_name='Задание')),
            ],
            options={
                'verbose_name': 'Точка для трекинга',
                'verbose_name_plural': 'Точки для трекинга',
            },
        ),
        migrations.CreateModel(
            name='TrackingData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('satellite_id', models.IntegerField(verbose_name='Номер спутника')),
                ('mag', models.FloatField(verbose_name='Звездная велечина')),
                ('step_sec', models.IntegerField(default=1, verbose_name='Временной шаг')),
                ('count', models.IntegerField(default=100, verbose_name='Количество снимков')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tracking_data', to='tasks.task', verbose_name='Задание')),
            ],
            options={
                'verbose_name': 'Данные для трекинга',
                'verbose_name_plural': 'Данные для трекинга',
            },
        ),
        migrations.CreateModel(
            name='TLEData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('satellite_name', models.CharField(max_length=255, verbose_name='Название спутника')),
                ('line1', models.CharField(max_length=255, verbose_name='Первая строка TLE спутника')),
                ('line2', models.CharField(max_length=255, verbose_name='Вторая строка TLE спутника')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='TLE_data', to='tasks.task', verbose_name='Задание')),
            ],
            options={
                'verbose_name': 'Данные для TLE',
                'verbose_name_plural': 'Данные для TLE',
            },
        ),
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('satellite_id', models.IntegerField(verbose_name='Номер спутника')),
                ('mag', models.FloatField(verbose_name='Звездная велечина')),
                ('dt', models.DateTimeField(verbose_name='Время снимка')),
                ('alpha', models.FloatField(verbose_name='Азимут')),
                ('beta', models.FloatField(verbose_name='Высота')),
                ('exposure', models.IntegerField(verbose_name='Требуемая выдержка снимка')),
                ('cs_type', models.SmallIntegerField(choices=[(0, 'Земная система координат'), (1, 'Звездная система координат')], default=0, verbose_name='Система координат')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='points', to='tasks.task', verbose_name='Задание')),
            ],
            options={
                'verbose_name': 'Точка для снимка',
                'verbose_name_plural': 'Точки для снимков',
            },
        ),
        migrations.CreateModel(
            name='Frame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exposure', models.IntegerField(verbose_name='Требуемая выдержка снимка')),
                ('dt', models.DateTimeField(verbose_name='Время снимка')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='frames', to='tasks.task', verbose_name='Задание')),
            ],
            options={
                'verbose_name': 'Фрейм',
                'verbose_name_plural': 'Фреймы (выдержка + время снимка)',
            },
        ),
    ]
