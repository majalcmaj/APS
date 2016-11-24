#!/bin/python3
import os, shutil, django

try:
    os.remove('db.sqlite3')
    shutil.rmtree("common/migrations")
except Exception:
    pass
os.system("python3 manage.py makemigrations common")
os.system("python3 manage.py migrate")
os.environ["DJANGO_SETTINGS_MODULE"]="APS.settings"
django.setup()
from django.contrib.auth.models import User
user = User(username="admin")
user.set_password("admin")
user.save()