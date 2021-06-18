from datetime import datetime, timedelta
import pytz

from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny


from tasks.models import Telescope, Task, BalanceRequest, Balance, Point
from tasks.serializers import (
    TelescopeSerializer, TelescopeBalanceSerializer, PointTaskSerializer,
    TrackingTaskSerializer, TleTaskSerializer, BalanceRequestSerializer, BalanceRequestCreateSerializer
)


class TelescopeView(generics.ListAPIView):
    queryset = Telescope.objects.all()
    serializer_class = TelescopeSerializer


class TelescopeChoosingView(generics.ListAPIView):
    queryset = Telescope.objects.all()
    serializer_class = TelescopeBalanceSerializer


class PointTaskView(generics.CreateAPIView):
    queryset = Task.objects.filter(task_type=Task.POINTS_MODE)
    serializer_class = PointTaskSerializer

    def is_collisions_with_existed_points(self, telescope_id, points):
        actual_tasks_ids = Task.objects.filter(
            telescope_id=telescope_id, task_type=Task.POINTS_MODE, status__in=[Task.CREATED, Task.RECEIVED]
        ).values_list('id', flat=True)
        existed_points = Point.objects.filter(task_id__in=actual_tasks_ids)
        for existed_point in existed_points:
            for point in points:
                start_dt = datetime.strptime(point.get('dt'), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.UTC)
                end_dt = start_dt + timedelta(seconds=point.get('exposure'))
                existed_start_dt = existed_point.dt
                existed_end_dt = existed_point.dt + timedelta(seconds=existed_point.exposure)
                if start_dt > existed_start_dt and start_dt < existed_end_dt or \
                        end_dt > existed_start_dt and end_dt < existed_end_dt:
                    local_start_dt = existed_start_dt + timedelta(hours=3)
                    local_end_dt = existed_end_dt + timedelta(hours=3)
                    return f'Задание не может быть сохранено, так как есть другая точка для съемки в ' \
                        f'{local_start_dt.strftime("%H:%M:%S")}, продлящаяся до {local_end_dt.strftime("%H:%M:%S")}'
        return ''

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=self.request.data, context=self.get_serializer_context())
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        telescope_id = self.request.data.get('telescope')
        collisions = self.is_collisions_with_existed_points(telescope_id, self.request.data.get('points'))
        if collisions:
            return Response(data={'msg': collisions, 'status': 'error'}, status=400)
        point_task = serializer.save()
        timing = self.request.data.get('timing')
        try:
            balance = Balance.objects.get(user=self.request.user, telescope_id=telescope_id)
            balance.minutes = balance.minutes - timing
            balance.save()
            return Response(data={'msg': f'Задание №{point_task.id} успешно создано, на этом телескопе осталось {balance.minutes} минут для наблюдений', 'status': 'ok'})
        except Balance.DoesNotExist:
            return Response(data={'msg': f'Ошибка создания задания, нет доступа к данному телескопу', 'status': 'error'}, status=400)


class TrackingTaskView(generics.CreateAPIView):
    queryset = Task.objects.filter(task_type=Task.TRACKING_MODE)
    serializer_class = TrackingTaskSerializer

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=self.request.data, context=self.get_serializer_context())
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        tracking_task = serializer.save()
        telescope_id = self.request.data.get('telescope')
        timing = self.request.data.get('timing')
        try:
            balance = Balance.objects.get(user=self.request.user, telescope_id=telescope_id)
            balance.minutes = balance.minutes - timing
            balance.save()
            return Response(data={
                'msg': f'Задание №{tracking_task.id} успешно создано, на этом телескопе осталось {balance.minutes} минут для наблюдений',
                'status': 'ok'})
        except Balance.DoesNotExist:
            return Response(data={'msg': f'Ошибка создания задания, нет доступа к данному телескопу', 'status': 'error'}, status=400)


class TleTaskView(generics.CreateAPIView):
    queryset = Task.objects.filter(task_type=Task.TLE_MODE)
    serializer_class = TleTaskSerializer

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=self.request.data, context=self.get_serializer_context())
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        tle_task = serializer.save()
        telescope_id = self.request.data.get('telescope')
        timing = self.request.data.get('timing')
        try:
            balance = Balance.objects.get(user=self.request.user, telescope_id=telescope_id)
            balance.minutes = balance.minutes - timing
            balance.save()
            return Response(data={
                'msg': f'Задание №{tle_task.id} успешно создано, на этом телескопе осталось {balance.minutes} минут для наблюдений',
                'status': 'ok'})
        except Balance.DoesNotExist:
            return Response(
                data={'msg': f'Ошибка создания задания, нет доступа к данному телескопу', 'status': 'error'},
                status=400)


class BalanceRequestView(generics.ListAPIView):
    serializer_class = BalanceRequestSerializer

    def get_queryset(self):
        return BalanceRequest.objects.filter(user=self.request.user)


class BalanceRequestCreateView(generics.CreateAPIView):
    serializer_class = BalanceRequestCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=self.request.data, context=self.get_serializer_context())
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        request = serializer.save()
        return Response(data=f'Заявка №{request.id} успешна создана')
