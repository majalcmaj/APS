import json
import os, shutil, django
import signal
from multiprocessing import Pool

import requests
import time

WORKERS_COUNT = 3
WAIT_BETWEEN_TIME = 4
threads_alive = 0
errors = 0

class MockClient:
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 13000
    HOSTNAME = "WORKER{}"

    def __init__(self, *args, **kwargs):
        from common.libs import RRDtoolManager
        from common.models import Client
        from common.libs import ClientsStateManager
        self._counter = 0
        self._key = ClientsStateManager.register_new_pending_client(
            "CLIENT",
            "127.0.0.1",
            {"lumel_time": "T"}, WAIT_BETWEEN_TIME)

        ClientsStateManager.accept_pending_client(self._key)
        db_cl = Client.objects.get(pk=self._key)
        db_cl.hostname += str(self._key)
        db_cl.is_configured = True
        db_cl.property_on_dashboard = db_cl.monitored_properties.get(name="lumel_time")
        db_cl.monitoring_timespan = 60
        db_cl.save()
        RRDtoolManager.create_rrd(db_cl)
        #shutil.chown("/var/rrddb/{}.rrd".format(self._key), "apache", "apache")

    def form_request(self, agregator):
        url = "http://{}:{}/aps_client/JsonRequest".format(self.SERVER_IP, self.SERVER_PORT)
        headers = {"content-type": "aps/json"}
        payload = {"message": "monitoring_data",
                   "timestamp": int(time.time()),
                   "hostname": self.HOSTNAME.format(self._key),
                   "monitored_properties": agregator,
                   "key": self._key
                   }
        return url, headers, payload

    def send_data(self):
        aggregator = {"lumel_time": self._counter}
        self._counter = self._counter + 1 if self._counter < 100 else 0
        url, headers, payload = self.form_request(aggregator)
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            if response.status_code != 200:
                print("Bad code: {}".format(response.status_code))
        except requests.ConnectionError as e:
            print("Error: {}".format(e))

    def run(self):
        while True:
            self.send_data()
            time.sleep(WAIT_BETWEEN_TIME)


def proc(client):
    client.run()


class InterruptHandler:
    def __init__(self, pool):
        self._pool = pool

    def register_interrupt_handler(self):
        signal.signal(signal.SIGINT, self._exit_method)

    def _exit_method(self, signal, frame):
        pool.terminate()


if __name__ == "__main__":
    # try:
    #     os.remove('db.sqlite3')
    #     shutil.rmtree("common/migrations")
    # except Exception:
    #     pass
    # os.system("python3 manage.py makemigrations common")
    # os.system("python3 manage.py migrate")
    os.environ["DJANGO_SETTINGS_MODULE"] = "APS.settings"
    django.setup()
    from django.contrib.auth.models import User

    # u = User(username="admin")
    # u.set_password("admin")
    # u.save()

    pool = Pool(WORKERS_COUNT)
    interrupt_handler = InterruptHandler(Pool)
    pool.map(proc, [MockClient(key) for key in range(0, WORKERS_COUNT)])
    pool.join()
