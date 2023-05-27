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
        self.write('DATA:ENCDG ASCII')
        self.write('DATA:WIDTH 1')

    def write(self, command):
        self.rm.write(command)

    def query(self, command):
        return self.rm.query(command)


class PowerSupply():
    def __init__(self):
        self.config = get_config()['PowerSupply']
        self.rm = pyvisa.ResourceManager().open_resource(get_pyvisa_resource(self.config['serial']))
        self.set_syst_lock_on()

    def write(self, command):
        self.rm.write(command)

    def query(self, command):
        return self.rm.query(command)


class ControlBoard():
    def __init__(self):
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
        return resp
    
    def query(self, cmd, value=0):
        msg = {
            'cmd': cmd,
            'value': value
        }
        return self.query_raw(msg)

