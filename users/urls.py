from django.urls import re_path, include

import users.views as views

urlpatterns = [
    re_path(r'^profile/$', views.ProfileView.as_view(), name='telescope_list'),
]

