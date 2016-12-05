from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from acquisition_server.views.JsonRequestView import JsonRequestView

app_name = 'aps_client'
urlpatterns = [
    url(r'^JsonRequest$', JsonRequestView.as_view(), name='JsonRequest'),
]
