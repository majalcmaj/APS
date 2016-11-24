import smtplib
import threading
from email.mime.text import MIMEText

from acquisition_presentation_server import settings

# TODO Artur - dokumentacja!

def send_message(mime_message):
    sending_thread = threading.Thread(target=_send_message,
                                      kwargs={"mime_message": mime_message})
    sending_thread.start()


def _send_message(mime_message):
    server = smtplib.SMTP(settings.EMAIL_SERVER_ADDRESS, settings.EMAIL_SERVER_PORT)
    server.starttls()
    server.login(settings.EMAIL_NOTIFICATION_LOGIN, settings.EMAIL_NOTIFICATION_PASSWORD)

    for email_address in settings.NOTIFIED_EMAILS:
        mime_message['To'] = email_address

    server.send_message(mime_message)

    server.quit()


def create_alert_simple_message(message):
    message_body = message
    message = MIMEText(message_body)
    message['Subject'] = "ALERT"
    message['From'] = settings.EMAIL_NOTIFICATION_LOGIN

    return message


def create_alert_custom_message(client, value_name, alert_value, threshold_value):
    client_properties = {property.name: property.type for property in client.monitored_properties.all()}

    message_body = "{} of ".format(" ".join(value_name.split("_")).capitalize())
    message_body += "host: {}(IP: {}) ".format(client.hostname, client.ip_address)
    message_body += "has reached: {}{}.\n".format(alert_value, client_properties[value_name])
    message_body += "Threshold value is: {}{}".format(threshold_value, client_properties[value_name])

    message = MIMEText(message_body)
    message['Subject'] = "ALERT"
    message['From'] = settings.EMAIL_NOTIFICATION_LOGIN

    return message