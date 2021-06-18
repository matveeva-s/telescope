from _datetime import datetime, timedelta
from tasks.models import Task


def telescope_collision_task_message(telescope_id, start_dt, end_dt):
    actual_tasks_ids = Task.objects.filter(
        telescope_id=telescope_id, task_type=Task.POINTS_MODE, status__in=[Task.CREATED, Task.RECEIVED]
    )
    for task in actual_tasks_ids:
        if start_dt > task.start_dt and start_dt < task.end_dt or end_dt > task.start_dt and end_dt < task.end_dt:
            local_start_dt = task.start_dt + timedelta(hours=3)
            local_end_dt = task.end_dt + timedelta(hours=3)
            return f'Задание не может быть сохранено, так как есть другое задание в ' \
                f'{local_start_dt.strftime("%H:%M:%S")}, продлящееся до {local_end_dt.strftime("%H:%M:%S")}'
    return ''


def converting_degrees(value):
    degrees = abs(int(value))
    minutes = abs(value - degrees) * 60
    seconds = int(abs(minutes - int(minutes)) * 60)
    minutes = int(minutes)
    return degrees, minutes, seconds


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False
