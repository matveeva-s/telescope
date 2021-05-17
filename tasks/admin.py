from django.contrib import admin
from .models import Telescope, Task, TrackingData, TLEData, Point, Frame, TrackPoint, Balance, BalanceRequest

admin.site.register(Telescope)
admin.site.register(Task)
admin.site.register(TrackingData)
admin.site.register(TLEData)
admin.site.register(Point)
admin.site.register(Frame)
admin.site.register(TrackPoint)
admin.site.register(Balance)
admin.site.register(BalanceRequest)
