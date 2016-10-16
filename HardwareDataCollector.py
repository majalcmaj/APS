import random

class HardwareDataCollector:
    @staticmethod
    def map_names_onto_functions(names):
        functions=[]
        for name in names:
            if(name =="cpu_usage"):
                functions.append((name,HardwareDataCollector.get_cpu_usage))
            elif (name == "ram_usage"):
                functions.append((name, HardwareDataCollector.get_ram_usage))
            elif (name == "free_disk_space"):
                functions.append((name, HardwareDataCollector.get_free_disk_space))
        return functions

    @staticmethod
    def get_cpu_usage():
        return 5

    @staticmethod
    def get_ram_usage():
        return 10

    @staticmethod
    def get_free_disk_space():
        return 15


