from django.db import models
from django.conf import settings


class Telescope(models.Model):
    ONLINE = 1
    OFFLINE = 2
    STATUS_CHOICES = (
        (ONLINE, 'Online'),
        (OFFLINE, 'Offline'),
    )
    name = models.CharField('Название', max_length=100)
    status = models.SmallIntegerField('Статус', choices=STATUS_CHOICES, default=OFFLINE)
    description = models.TextField('Описание', blank=True, null=True)
    location = models.CharField('Местоположение', max_length=300, blank=True, null=True)
    latitude = models.FloatField('Широта в градусах', blank=True, null=True)
    longitude = models.FloatField('Долгота в градусах', blank=True, null=True)
    avatar = models.ImageField('Аватар', null=True, blank=True, upload_to='images/telescopes')

    class Meta:
        verbose_name = 'Телескоп'
        verbose_name_plural = 'Телескопы'

    def __str__(self):
        if self.name:
            return self.name
        return f'Телескоп {self.id}'

    def get_user_balance(self, user):
        balance = self.balances.filter(user=user).first()
        return balance.minutes if balance else 0


class Task(models.Model):
    CREATED = 1
    RECEIVED = 2
    READY = 3
    FAILED = 4
    STATUS_CHOICES = (
        (CREATED, 'Создано'),
        (RECEIVED, 'Получена телескопом'),
        (READY, 'Выполнена'),
        (FAILED, 'Не удалось выполнить'),
    )
    POINTS_MODE = 1
    TRACKING_MODE = 2
    TLE_MODE = 3

    TYPE_CHOICES = (
        (POINTS_MODE, 'Снимки по точкам'),
        (TRACKING_MODE, 'Трэкинг по точкам'),
        (TLE_MODE, 'Снимки по TLE'),
    )
    status = models.SmallIntegerField('Статус', choices=STATUS_CHOICES, default=CREATED)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Автор задания', related_name='tasks', on_delete=models.CASCADE)
    telescope = models.ForeignKey(Telescope, verbose_name='Телескоп', related_name='tasks', on_delete=models.CASCADE)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    task_type = models.SmallIntegerField('Тип задания', choices=TYPE_CHOICES)
    start_dt = models.DateTimeField('Дата и время начала наблюдения', null=True, blank=True)
    end_dt = models.DateTimeField('Дата и время конца наблюдения', null=True, blank=True)

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'

    def __str__(self):
        return f'{self.get_task_type_display()} (id={self.id}) от {self.author.get_full_name()}'


class Frame(models.Model):
    task = models.ForeignKey(to=Task, verbose_name='Задание', related_name='frames', null=True, blank=True, on_delete=models.CASCADE)
    exposure = models.IntegerField('Требуемая выдержка снимка')
    dt = models.DateTimeField('Время снимка')

    class Meta:
        verbose_name = 'Фрейм'
        verbose_name_plural = 'Фреймы (выдержка + время снимка)'


class TrackPoint(models.Model):
    task = models.ForeignKey(to=Task, verbose_name='Задание', related_name='track_points', null=True, blank=True, on_delete=models.CASCADE)
    alpha = models.FloatField('Азимут')
    beta = models.FloatField('Высота')
    dt = models.DateTimeField('Время снимка')

    class Meta:
        verbose_name = 'Точка для трекинга'
        verbose_name_plural = 'Точки для трекинга'


class TrackingData(models.Model):
    task = models.ForeignKey(to=Task, verbose_name='Задание', related_name='tracking_data', null=True, blank=True, on_delete=models.CASCADE)
    satellite_id = models.IntegerField('Номер спутника')
    mag = models.FloatField('Звездная велечина')
    step_sec = models.IntegerField('Временной шаг', default=1)
    count = models.IntegerField('Количество снимков', default=100)

    class Meta:
        verbose_name = 'Данные для трекинга'
        verbose_name_plural = 'Данные для трекинга'


class TLEData(models.Model):
    task = models.ForeignKey(to=Task, verbose_name='Задание', related_name='TLE_data', null=True, blank=True, on_delete=models.CASCADE)
    satellite_name = models.CharField('Название спутника', max_length=255)
    line1 = models.CharField('Первая строка TLE спутника', max_length=255)
    line2 = models.CharField('Вторая строка TLE спутника', max_length=255)

    class Meta:
        verbose_name = 'Данные для TLE'
        verbose_name_plural = 'Данные для TLE'


class Point(models.Model):
    EARTH_SYSTEM = 0
    STARS_SYSTEM = 1
    SYSTEM_CHOICES = (
        (EARTH_SYSTEM, 'Земная система координат'),
        (STARS_SYSTEM, 'Звездная система координат'),
    )
    task = models.ForeignKey(to=Task, verbose_name='Задание', related_name='points', null=True, blank=True, on_delete=models.CASCADE)
    satellite_id = models.IntegerField('Номер спутника')
    mag = models.FloatField('Звездная велечина')
    dt = models.DateTimeField('Время снимка')
    alpha = models.FloatField('Азимут')
    beta = models.FloatField('Высота')
    exposure = models.IntegerField('Требуемая выдержка снимка')
    cs_type = models.SmallIntegerField('Система координат', choices=SYSTEM_CHOICES, default=EARTH_SYSTEM)

    class Meta:
        verbose_name = 'Точка для снимка'
        verbose_name_plural = 'Точки для снимков'


class Balance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь', related_name='balances',
                             on_delete=models.CASCADE)
    telescope = models.ForeignKey(to=Telescope, verbose_name='Телескоп', related_name='balances',
                                  on_delete=models.CASCADE)
    minutes = models.IntegerField('Наблюдательное время', default=0)

    class Meta:
        verbose_name = 'Баланс наблюдательного времени'
        verbose_name_plural = 'Балансы наблюдательного времени'

    def __str__(self):
        return f'{self.user} ({self.telescope})'


class BalanceRequest(models.Model):
    CREATED = 1
    APPROVED = 2
    REJECTED = 3
    STATUS_CHOICES = (
        (CREATED, 'Создана'),
        (APPROVED, 'Одобрена'),
        (REJECTED, 'Отклонена'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь', related_name='requests',
                             on_delete=models.CASCADE)
    telescope = models.ForeignKey(to=Telescope, verbose_name='Телескоп', related_name='balances_requests',
                                  on_delete=models.CASCADE)
    minutes = models.IntegerField('Требуемое время в минутах')
    status = models.SmallIntegerField('Статус', choices=STATUS_CHOICES, default=CREATED)

    class Meta:
        verbose_name = 'Заявка на получение наблюдательного времени'
        verbose_name_plural = 'Заявки на получение наблюдательного времени'

    def __str__(self):
        return f'Заявка {self.id} (от {self.user}, на {self.telescope})'
