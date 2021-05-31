from django.urls import re_path, include

import tasks.views as views

urlpatterns = [
    re_path(r'^telescopes/$', views.TelescopeView.as_view(), name='telescope_list'),
    re_path(r'^telescopes_with_balances/$', views.TelescopeChoosingView.as_view(), name='telescope_with_balances'),
    re_path(r'^point_task/$', views.PointTaskView.as_view(), name='point_task'),
    re_path(r'^tracking_task/$', views.TrackingTaskView.as_view(), name='tracking_task'),
]
