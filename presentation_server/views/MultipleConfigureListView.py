from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView

from common.libs import ClientManager
from common.models import Client


class MultipleConfigureListView(LoginRequiredMixin, ListView):
    template_name = "presentation_server/MultipleConfigureListView.html"
    login_url = '/aps/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["chosen_pk"] = self._chosen_pk
        except:
            pass
        return context

    def get_queryset(self):
        if "pks_to_configure[]" in self.request.GET.keys():
            pks = [int(pk) for pk in self.request.GET.getlist("pks_to_configure[]")]
            if len(pks) == 0:
                return ClientManager.get_all_clients()
            else:
                pk = pks[0]
                self._chosen_pk = pk
                return ClientManager.get_clients_with_same_properties(pk)
        else:
            return ClientManager.get_all_clients()
