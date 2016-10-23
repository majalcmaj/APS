import time
import calendar


def get_client_data():
    time_s = calendar.timegm(time.gmtime())
    return {
        "unix_time" : [time_s - tm for tm in range (19*100, 0, -100)],
        "data":{
            "cpu_usage":[1,2,3,4,5,6,7,8,9,10,9,8,7,6,5,4,3,2,1],
            "ram_usage":[11,22,13,24,15,26,17,28,19,10,29,18,27,16,25,14,23,12,21],
            "free_disk_space":[11,22,33,44,55,66,77,88,99,100,91,82,73,64,55,46,37,28,19],
        }
    }
