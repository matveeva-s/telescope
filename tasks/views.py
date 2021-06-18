from datetime import datetime, timedelta
import locale
import pytz

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny


from tasks.models import Telescope, Task, BalanceRequest, Balance, Point
from tasks.serializers import (
    TelescopeSerializer, TelescopeBalanceSerializer, PointTaskSerializer,
    TrackingTaskSerializer, TleTaskSerializer, BalanceRequestSerializer, BalanceRequestCreateSerializer
)
from tasks.helpers import telescope_collision_task_message


DT_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class TelescopeView(generics.ListAPIView):
    queryset = Telescope.objects.all()
    serializer_class = TelescopeSerializer


class TelescopeChoosingView(generics.ListAPIView):
    queryset = Telescope.objects.all()
    serializer_class = TelescopeBalanceSerializer


class PointTaskView(generics.CreateAPIView):
    queryset = Task.objects.filter(task_type=Task.POINTS_MODE)
    serializer_class = PointTaskSerializer

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=self.request.data, context=self.get_serializer_context())
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        telescope_id = self.request.data.get('telescope')
        start_dt = datetime.strptime(self.request.data.get('min_dt'), DT_FORMAT).replace(tzinfo=pytz.UTC)
        end_dt = datetime.strptime(self.request.data.get('max_dt'), DT_FORMAT).replace(tzinfo=pytz.UTC)
        collisions_message = telescope_collision_task_message(telescope_id, start_dt, end_dt)
        if collisions_message:
            return Response(data={'msg': collisions_message}, status=400)
        point_task = serializer.save()
        duration = int(self.request.data.get('duration'))
        try:
            balance = Balance.objects.get(user=self.request.user, telescope_id=telescope_id)
            balance.minutes = balance.minutes - duration
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
        start_dt = datetime.strptime(self.request.data.get('min_dt'), DT_FORMAT).replace(tzinfo=pytz.UTC)
        end_dt = datetime.strptime(self.request.data.get('max_dt'), DT_FORMAT).replace(tzinfo=pytz.UTC)
        collisions_message = telescope_collision_task_message(telescope_id, start_dt, end_dt)
        if collisions_message:
            return Response(data={'msg': collisions_message}, status=400)
        duration = int(self.request.data.get('duration'))
        try:
            balance = Balance.objects.get(user=self.request.user, telescope_id=telescope_id)
            balance.minutes = balance.minutes - duration
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
        start_dt = datetime.strptime(self.request.data.get('min_dt'), DT_FORMAT)
        end_dt = datetime.strptime(self.request.data.get('max_dt'), DT_FORMAT)
        collisions_message = telescope_collision_task_message(telescope_id, start_dt, end_dt)
        if collisions_message:
            return Response(data={'msg': collisions_message}, status=400)
        duration = int(self.request.data.get('duration'))
        try:
            balance = Balance.objects.get(user=self.request.user, telescope_id=telescope_id)
            balance.minutes = balance.minutes - duration
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


def get_telescope_schedule(request, telescope_id):
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    actual_tasks = Task.objects.filter(status__in=[Task.CREATED, Task.RECEIVED], telescope_id=telescope_id)
    slots = []
    for task in actual_tasks:
        slot = f'{task.start_dt.strftime("%d %b %Y, %H:%M:%S")} - {task.end_dt.strftime("%d %b %Y, %H:%M:%S")}'
        slots.append(slot)
    return JsonResponse({'schedule': slots})


def get_telescope_plan(request, telescope_id):
    telescope = get_object_or_404(Telescope, id=telescope_id)
