from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = 'Пользователи'

    def ready(self):
        from .signals import init_signals
        init_signals()
