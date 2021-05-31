import json
from datetime import datetime, date, time
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny


from tasks.models import Telescope, Task, Point
from tasks.serializers import TelescopeSerializer, TelescopeBalanceSerializer, PointTaskSerializer, TrackingTaskSerializer


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
        point_task = serializer.save()
        return Response(data={'msg': f'Задание №{point_task.id} успешно создано', 'status': 201}, status=201)


class TrackingTaskView(generics.CreateAPIView):
    queryset = Task.objects.filter(task_type=Task.TRACKING_MODE)
    serializer_class = TrackingTaskSerializer

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=self.request.data, context=self.get_serializer_context())
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        tracking_task = serializer.save()
        return Response(data={'msg': f'Задание №{tracking_task.id} успешно создано', 'status': 201}, status=201)
