from django.urls import re_path, include

import tasks.views as views

urlpatterns = [
    re_path(r'^telescopes/$', views.TelescopeView.as_view(), name='telescope_list'),
    re_path(r'^telescopes_with_balances/$', views.TelescopeChoosingView.as_view(), name='telescope_with_balances'),
]
