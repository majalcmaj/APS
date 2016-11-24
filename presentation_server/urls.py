from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from presentation_server.views.AlertsCleaner import AlertsCleaner
from presentation_server.views.BlockedClientsView import BlockedClientsView
from presentation_server.views.ClientConfigurationView import ClientConfigurationView
from presentation_server.views.ClientDetailsView import ClientDetailsView
from presentation_server.views.IndexView import IndexView
from presentation_server.views.PendingClientsView import PendingClientsView
from presentation_server.views.ThresholdConfigurationView import ThresholdConfigurationView
from presentation_server.views.UpdateCharts import UpdateCharts

app_name = 'aps'
urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^ClientConfiguration/(?P<client_pk>[0-9]+)/(?P<error_message>.*)?$',
        ClientConfigurationView.as_view(), name='ClientConfiguration'),
    url(r'^ClientDetails/(?P<client_pk>[0-9]+)$',
        ClientDetailsView.as_view(), name='ClientDetails'),
    url(r'^PendingClients/$', PendingClientsView.as_view(), name='PendingClients'),
    url(r'^BlockedClients/$', BlockedClientsView.as_view(), name='BlockedClients'),
    url(r'^UpdateCharts/$', UpdateCharts.as_view(),
        name='UpdateCharts'),
    url(r'^login/', auth_views.login,
        {
            'template_name': "presentation_server/auth/login.html",
        },
        name="login",
        ),
    url(r'^logout/', auth_views.logout,
        {
            'next_page': "/aps/",
        },
        name="logout",
        ),
    url(r'^ThresholdConfiguration$',
        ThresholdConfigurationView.as_view(), name='ThresholdConfiguration'),
    url(r'^AlertsCleaner/(?P<client_pk>[0-9]+)$',
        AlertsCleaner.as_view(), name='AlertsCleaner'),

]
