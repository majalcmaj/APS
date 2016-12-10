import socket
import struct

from utils.crc_calculator import CRCCalculator


class LumelConnection():
    def __init__(self, lumel_ip, lumel_port):
        self._lumel_ip = lumel_ip
        self._lumel_port = lumel_port
        self._connection_socket = None

    def form_command(self, address, function, start_register, number_of_registers):
        command = [address, function]
        command.extend(list(start_register.to_bytes(2, byteorder='big')))
        command.extend(list(number_of_registers.to_bytes(2, byteorder='big')))
        command.extend(CRCCalculator.get_crc_bytes(command))
        return command

    def connect_with_lumel(self):
        try:
            self._connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._connection_socket.connect(("localhost", 8300))
            return True
        except Exception:
            print("Could not connect to lumel")
            self._connection_socket = None
        return False

    def close_connection(self):
        if self._connection_socket is not None:
            try:
                self._connection_socket.close()
            except Exception:
                print("Could not connect to lumel")

    def send_command(self, command):
        self._connection_socket.send(bytes(command))
        response = self._connection_socket.recv(1024)
        return response

    def extrac_register_data_from_response(self, response, number_of_registers, type):
        # lumel_device_address = response[0]
        # function = response[1]
        # print("device address:", lumel_device_address)
        # print("function:", function)
        # print("number of bytes to read:", number_of_bytes_per_register)

        number_of_bytes_per_register = int(response[2] / number_of_registers)
        start = 3
        result = []
        for register_index in range(0, number_of_registers):
            offset = register_index * number_of_bytes_per_register
            register_value = response[start + offset:start + offset + number_of_bytes_per_register]
            if type == 'int':
                register_value = int.from_bytes(register_value, byteorder='big')
            elif type == 'float':
                register_value = bytearray([register_value[i] for i in range(number_of_bytes_per_register - 1, -1, -1)])
                register_value = struct.unpack('f', register_value)[0]
            result.append(register_value)
        return result
