import serial
import serial.tools.list_ports
import pyvisa
import json

def get_pyvisa_resource(serial_number):
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    for resource in resources:
        try:
            instr = rm.open_resource(resource)
            if serial_number in instr.query('*IDN?'):
                return resource
        except:
            pass
    raise Exception('Failed to find device with SN: '+str(serial_number))

def get_config():
    with open('config.json') as file:
        data = json.load(file)
        return data


class Oscilloscope():
    def __init__(self):
        self.config = get_config()['Oscilloscope']
        self.rm = pyvisa.ResourceManager().open_resource(get_pyvisa_resource(self.config['serial']))
        self.query('DATA:ENCDG ASCII')
        self.query('DATA:WIDTH 1')

    def query(self, command):
        if '?' in command:
            return {
                "message": self.rm.query(command)
            }
        else:
            self.rm.write(command)
            return {
                "message": None
            }


class PowerSupply():
    def __init__(self):
        self.config = get_config()['PowerSupply']
        self.rm = pyvisa.ResourceManager().open_resource(get_pyvisa_resource(self.config['serial']))

    def query(self, command):
        if '?' in command:
            return {
                "message": self.rm.query(command)
            }
        else:
            self.rm.write(command)
            return {
                "message": None
            }
        
class PowerSupplySmall():
    def __init__(self):
        self.config = get_config()['PowerSupplySmall']
        self.rm = pyvisa.ResourceManager().open_resource(get_pyvisa_resource(self.config['serial']))

    def query(self, command):
        if '?' in command:
            return {
                "message": self.rm.query(command)
            }
        else:
            self.rm.write(command)
            return {
                "message": None
            }

class FunctionGenerator():
    def __init__(self):
        self.config = get_config()['FunctionGenerator']
        self.rm = pyvisa.ResourceManager().open_resource(get_pyvisa_resource(self.config['serial']))

    def query(self, command):
        if '?' in command:
            return {
                "message": self.rm.query(command)
            }
        else:
            self.rm.write(command)
            return {
                "message": None
            }

class ControlBoard():
    def __init__(self):
        self.errors = {
            0: 'OK',
            1: 'Deserialization error',
            2: 'No command key',
            3: 'Invalid command'
        }
        self.config = get_config()['ControlBoard']
        ports = serial.tools.list_ports.comports()
        self.ser = None
        for port in ports:
            if port.vid == self.config['vid'] and port.pid == self.config['pid']:
                port = port.name
                self.ser = serial.Serial(port, baudrate=self.config['baudrate'], dsrdtr=True, timeout=5)
                return
        err_msg = "ControlBoard not found:\n"
        err_msg += "VID: " + str(self.config['vid']) + "\n"
        err_msg += "PID: " + str(self.config['pid']) + "\n"
        raise Exception(err_msg)

    def query_raw(self, msg):
        self.ser.write(json.dumps(msg).encode())
        self.ser.write(b'\n')
        resp = json.loads(self.ser.readline().decode())
        resp['status'] = self.errors[resp['status']]
        return resp
    
    def query(self, cmd):
        msg = {
            'cmd': cmd.split(' ')[0],
            'value': cmd.split(' ')[1]
        }
        return self.query_raw(msg)

