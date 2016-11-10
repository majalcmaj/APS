from django.conf.urls import url

from acquisition_presentation_server.view import LineChartJSONView, line_chart_json, line_chart
from acquisition_presentation_server.views.BlockedClientsView import BlockedClientsView
from acquisition_presentation_server.views.ClientConfigurationView import ClientConfigurationView
from acquisition_presentation_server.views.ClientDetailsView import ClientDetailsView
from acquisition_presentation_server.views.IndexView import IndexView
from acquisition_presentation_server.views.JsonRequestView import JsonRequestView
from acquisition_presentation_server.views.PendingClientsView import PendingClientsView
from acquisition_presentation_server.views.UpdateCharts import UpdateCharts

app_name = 'aps'
urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^JsonRequest$', JsonRequestView.as_view(), name='JsonRequest'),
    url(r'^ClientConfiguration/(?P<client_pk>[0-9]+)(/(?P<error_message>.*))?$',
        ClientConfigurationView.as_view(), name='ClientConfiguration'),
    url(r'^ClientDetails/(?P<client_pk>[0-9]+)$',
        ClientDetailsView.as_view(), name='ClientDetails'),
    url(r'^PendingClients/$', PendingClientsView.as_view(), name='PendingClients'),
    url(r'^BlockedClients/$', BlockedClientsView.as_view(), name='BlockedClients'),
    url(r'^line_chart_json/$', line_chart_json,
        name='line_chart_json'),
    url(r'^line_chart/$', line_chart,
        name='line_chart'),
    url(r'^UpdateCharts/$', UpdateCharts.as_view(),
        name='UpdateCharts'),
]
