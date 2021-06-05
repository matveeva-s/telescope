# Chronos
Backend часть проекта **Chronos** - системы дистанцонного доступа и управления сетью телескопов.

### Требования
Установить **python** (Python 3.6.9 испольльзуется на данный момент) и **pip** (19.0.3 - текущая версия).
### Инструкция по запуску

1. Скачать/склонировать репозиторий
2. Из консоли в папке проекта создать виртуальное окружение *python3 -m venv env*
3. Активировать виртуальное окружение *source env/bin/activate*
4. Установить питоновские модули командой *pip install -r requirements.txt*
5. Получить файл с конфигурациями *settings.py* (извлечен из репо, так как в нем содержится необщедоступная инфа), 
положить его в папку telescope
5. Запустить сервер командой *python manage.py runserver* (запустится на http://127.0.0.1:8000)
6. Накатить миграции командой *python manage.py migrate*
7. Возможны проблемы с кодировкой utf8 для MySQL (ошибка типа django.db.utils.OperationalError: (1366,
 "Incorrect string value: '\\xD0\\x9F\\xD1\\x80\\xD0\\xBE...' for column 'name' at row 1")), это испрвляется командой 
*ALTER TABLE {TABLE_NAME} CONVERT TO CHARACTER SET utf8 COLLATE utf8_unicode_ci;*
