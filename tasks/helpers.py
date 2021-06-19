from _datetime import datetime, timedelta
import julian
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


def get_points_json(points):
    data = []
    for point in points:
        data.append({
            'id': point.satellite_id,
            'mag': point.mag,
            'jd': julian.to_jd(point.dt, fmt='jd'),
            'alpha': point.alpha,
            'beta': point.beta,
            'exp': point.exposure,
            'type': point.cs_type,
        })
    return data


def get_track_json(track_list):
    data = []
    for track in track_list:
        data.append({
            'jd': julian.to_jd(track.dt, fmt='jd'),
            'alpha': track.alpha,
            'beta': track.beta,
        })
    return data


def get_frames_json(frames):
    data = []
    for frame in frames:
        data.append({
            'jd': julian.to_jd(frame.dt, fmt='jd'),
            'exp': frame.exposure,
        })
    return data


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
