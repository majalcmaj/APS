# IMPORTANT: ADD THESE LINES TO THE END OF MAIN settings.py FOR THE WEBAPP TO WORK
# try:
#     from acquisition_presentation_server.settings import *
# except ImportError:
#     pass

import os
LOGGER_NAME = "django"
RRD_DATABASE_DIRECTORY = "/var/rrddb"

EMAIL_SERVER_ADDRESS = "smtp.gmail.com"
EMAIL_SERVER_PORT = 587
EMAIL_NOTIFICATION_LOGIN = "alert.server.monitor@gmail.com"
EMAIL_NOTIFICATION_PASSWORD = "Kupka1234"
NOTIFIED_EMAILS = [
    "majalcmaj@gmail.com"
]


# Logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
        },
    },
    'loggers': {
        "django": {
            'handlers': ['console'],
            'propagate': True,
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

LOGIN_REDIRECT_URL = "aps:index"
