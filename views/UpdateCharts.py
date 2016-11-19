import json

from django.http.response import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from acquisition_presentation_server.common import RRDtoolManager
from acquisition_presentation_server.models import Client


class UpdateCharts(View):
    # TODO: Dodać csrf do ajaxa w index.html
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pk_last_update = json.loads(request.POST.get("pk_last_update"))
        monitoring_data = {}
        if pk_last_update is not None:
            for pk, previous_fetch in pk_last_update.items():
                data, update_time = RRDtoolManager.fetch_data(
                    Client.objects.get(pk=pk),
                    previous_fetch)
                if data is not None and update_time is not None:
                    monitoring_data[pk] = data
                    pk_last_update[pk] = update_time

        response = {
            "monitoring_data": monitoring_data,
            "pk_last_update": pk_last_update
        }
        return JsonResponse(response)
