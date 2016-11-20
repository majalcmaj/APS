from acquisition_presentation_server.models import Alert, Client

"""
File contains functions which handle alerts
"""

def delete_alert(alert_pk):
    """Delete alert with provided public key
    :param alert_pk: a public key of alert which should be deleted
    :return None if everything went ok
    :raises Alert.DoesNotExist when no alert object with correspondiong key was found.
    """
    Alert.objects.get(pk=alert_pk).delete()


def delete_all_for_client(client_pk):
    """Delete all alerts for client with given pk

    :param client_pk: a public key of client of which alerts should be deleted
    :return: None if everytging went OK
    :raises Client.DoesNotExists if client with given pk does not exist in database.
    """
    for alert in Client.objects.get(pk=client_pk).alerts.all():
        alert.delete()
