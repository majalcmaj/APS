from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from acquisition_server.views.JsonRequestView import JsonRequestView
from acquisition_server.views import ClientRestAPI
app_name = 'aps_client'
urlpatterns = [
    url(r"monitoring_data$", ClientRestAPI.monitoring_data),
    url(r"client_configuration$", ClientRestAPI.client_configuration),
    url(r"client_identity$", ClientRestAPI.client_identity),
    url(r'^JsonRequest$', JsonRequestView.as_view(), name='JsonRequest'),
]
