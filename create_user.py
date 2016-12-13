import os, django, getpass
if __name__=="__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "APS.settings"
    django.setup()
    from django.contrib.auth.models import User

    username = input("Admin login: ")
    try:
        User.objects.get(username=username)
        print("User with given username already exists in database.")
        exit(1)
    except User.DoesNotExist:
        pass
    u = User(username=username)
    password = getpass.getpass()
    if getpass.getpass("Repeat password:") != password:
        print("Provided passwords are not the same.")
        exit(1)
    u.set_password(password)
    u.save()
    exit(0)