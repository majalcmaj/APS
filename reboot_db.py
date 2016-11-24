#!/bin/python3
import os, shutil, django

try:
    os.remove('db.sqlite3')
    shutil.rmtree("acquisition_presentation_server/migrations")
except Exception:
    pass
os.system("python3 manage.py makemigrations acquisition_presentation_server")
os.system("python3 manage.py migrate")
os.environ["DJANGO_SETTINGS_MODULE"]="DjangoSites.settings"
django.setup()
from django.contrib.auth.models import User
user = User(username="admin")
user.set_password("admin")
user.save()