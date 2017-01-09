from django.test import TestCase

#  TEST FOR RRD TOOL - to implement!
# def run():
#     for c in Client.objects.all():
#         c.delete()
#     cl = Client(hostname="test", ip_address="127.0.0.1", port=13000, probing_interval=1)
#     cl.save()
#     for mp in "ram_usage", "cpu_usage":
#         cl.monitored_properties.create(name=mp, type='int')
#     cl.save()
#
#     rrdm = RRDtoolManager(cl)
#
#     rrdm.create_rrd()
#     import random
#     time.sleep(1)
#     for i in range(0, 5):
#         rrdm.update_rrd({"cpu_usage":str(i),
#                         "ram_usage":str(i * 100)})
#         time.sleep(1)
#     print(rrdm.fetch_data(20))
