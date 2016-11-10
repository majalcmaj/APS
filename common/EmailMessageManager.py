import smtplib
from email.mime.text import MIMEText
import threading
from acquisition_presentation_server import settings


#FOR TESTING PURPOSES
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "DjangoSites.settings"

import django
django.setup()

from acquisition_presentation_server.models import Client, MonitoredProperty
#END FOR TESTING PURPOSES

class EmailMessageManager:
    @staticmethod
    def send_message(mime_message):
        sending_thread = threading.Thread(target=EmailMessageManager._send_message,
                                          kwargs={"mime_message":mime_message})
        sending_thread.start()

    @staticmethod
    def _send_message(mime_message):
        server = smtplib.SMTP(settings.EMAIL_SERVER_ADDRESS, settings.EMAIL_SERVER_PORT)
        server.starttls()
        server.login(settings.EMAIL_NOTIFICATION_LOGIN, settings.EMAIL_NOTIFICATION_PASSWORD)

        for email_address in settings.NOTIFIED_EMAILS:
            mime_message['To'] = email_address
            server.send_message(mime_message)

        server.quit()

    @staticmethod
    def create_alert_message(client, value_name, alert_value, threshold_value):
        client_properties = {property.name: property.type for property in client.monitored_properties.all()}

        message_body = "{} of ".format(" ".join(value_name.split("_")).capitalize())
        message_body += "host: {}(IP: {}) ".format(client.hostname, client.ip_address)
        message_body += "has reached: {}{}.\n".format(alert_value, client_properties[value_name])
        message_body += "Threshold value is: {}{}".format(threshold_value, client_properties[value_name])

        message = MIMEText(message_body)
        message['Subject'] = "ALERT"
        message['From'] = settings.EMAIL_NOTIFICATION_LOGIN

        return message

#FOR TESTING PURPOSES
if __name__ == '__main__':
    client = Client.objects.get(pk=10)
    alert_message = EmailMessageManager.create_alert_message(client, "cpu_usage", 99, 90)
    EmailMessageManager.send_message(alert_message)
#END FOR TESTING PURPOSES