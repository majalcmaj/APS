from acquisition_presentation_server.models import Alert, Client


def delete_alert(alert_pk):
    Alert.objects.get(pk=alert_pk).delete()


def delete_all_for_client(client_pk):
    for alert in Client.objects.get(pk=client_pk).alerts.all():
        alert.delete()
