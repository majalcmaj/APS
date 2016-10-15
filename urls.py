from django.conf.urls import url

from acquisition_presentation_server.views.ApplyClientConfiguration import ApplyClientConfiguration
from acquisition_presentation_server.views.BlockedClientModify import BlockedClientModify
from acquisition_presentation_server.views.BlockedClientsView import BlockedClientsView
from acquisition_presentation_server.views.ClientConfigurationView import ClientConfigurationView
from acquisition_presentation_server.views.ClientsView import ClientsView
from acquisition_presentation_server.views.IndexView import IndexView
from acquisition_presentation_server.views.JsonRequestView import JsonRequestView
from acquisition_presentation_server.views.PendingClientsView import PendingClientsView
from acquisition_presentation_server.views.PendingClientModify import PendingClientModify

app_name='aps'
urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^JsonRequest$', JsonRequestView.as_view(), name = 'JsonRequest'),
    url(r'^Clients/$', ClientsView.as_view(), name = 'Clients'),
    url(r'^ClientConfiguration/(?P<client_pk>[0-9]+)$',
        ClientConfigurationView.as_view(), name = 'ClientConfiguration'),
    url(r'^ApplyClientConfiguration$',
        ApplyClientConfiguration.as_view(), name = 'ApplyClientConfiguration'),
    url(r'^PendingClients/$', PendingClientsView.as_view(), name = 'PendingClients'),
    url(r'^BlockedClients/$', BlockedClientsView.as_view(), name = 'BlockedClients'),
    url(r'^PendingClientModify/$', PendingClientModify.as_view(),
        name = 'PendingClientModify'),
    url(r'^BlockedClientModify/$', BlockedClientModify.as_view(),
        name = 'BlockedClientModify'),

]