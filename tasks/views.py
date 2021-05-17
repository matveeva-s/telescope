from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny

from tasks.models import Telescope, Task
from tasks.serializers import TelescopeSerializer, TelescopeBalanceSerializer


class TelescopeView(generics.ListAPIView):
    queryset = Telescope.objects.all()
    serializer_class = TelescopeSerializer


class TelescopeChoosingView(generics.ListAPIView):
    queryset = Telescope.objects.all()
    serializer_class = TelescopeBalanceSerializer
