import json

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt



@csrf_exempt
def json_request(request):
    if request.method == 'POST' and request.content_type == 'text/cpuinfo':
        try:
            json_data = json.loads(request.body.decode('utf-8'))
            print(json_data)
            message_db = JsonMessage(name=json_data['name'])
            message_db.save()
            values_dict = json_data['values']
            print(values_dict)
            for key in values_dict:
                print("Key: " + str(key))
                keyval_db = KeyVal(key=key, val=json.dumps(values_dict[key]).encode('utf-8'), json_message=message_db)
                keyval_db.save()
        except KeyError:
            pass

    return HttpResponse("")
