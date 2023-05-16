import serial
import serial.tools.list_ports
import time
import atexit
import pyvisa
import numpy as np
import json
# import RPi.GPIO as GPIO
import mock_gpio as GPIO


# TEKTRONIX DPO 7054 Digital Phosphor Oscilloscope
class Oscilloscope():
    def __init__(self):
        with open('config.json') as file:
            self.config = json.load(file)['Oscilloscope']
        visa = pyvisa.ResourceManager()
        try:
            self.rm = visa.open_resource(self.config['resource_name'])
        except Exception as err:
            err_msg = str(err)
            err_msg += "\n\n"
            err_msg += "No VISA device found with name: " + self.config['resource_name']
            raise Exception(err_msg)
        self.set_channel(1)
        self.rm.write('DATA:ENCDG ASCII')
        self.rm.write('DATA:WIDTH 1')

    def get_curve(self):
        yzero = float(self.rm.query('WFMO:YZE?'))
        ymult = float(self.rm.query('WFMO:YMU?'))
        yoff = float(self.rm.query('WFMO:YOF?'))
        values = np.array(self.rm.query_ascii_values('CURV?', converter='f'))
        for a in range(len(values)):
            values[a] = yzero - yoff * ymult + ymult * float(values[a])
        return values

    # '1e-3' sets scale to 1ms per devision
    def set_horizontal_scale(self, scale):
        self.rm.write('HORIZONTAL:SCALE ' + scale)

    # '1e6' sets the sample rate to 1 million samples per second
    def set_horizontal_sample_rate(self, rate):
        self.rm.write('HORIZONTAL:MODE:SAMPLERATE ' + rate)

    def set_channel(self, channel):
        self.rm.write('DATA:SOURCE CH' + str(channel))

    # Returns AUTO or NORMAL.
    def get_trigger_mode(self):
        return self.rm.query('TRIGGER:A:MODE?')

    def set_trigger_normal_mode(self):
        self.rm.write('TRIGGER:A:MODE NORMAL')

    def set_trigger_auto_mode(self):
        self.rm.write('TRIGGER:A:MODE AUTO')

    def set_trigger_channel_for_edge(self, channel):
        self.rm.write('TRIGGER:A:EDGE:SOURCE CH' + str(channel))

    # Level is a float in volts.
    def set_trigger_channel_level(self, channel, level):
        self.rm.write('TRIGGER:A:LEVEL CH' +
                            str(channel) + ' ' + str(level))

    def set_trigger_slope_either(self):
        self.rm.write('TRIGGER:A:EDGE:SLOPE EITHER')

    def set_trigger_slope_rise(self):
        self.rm.write('TRIGGER:A:EDGE:SLOPE RISE')

    def set_trigger_slope_fall(self):
        self.rm.write('TRIGGER:A:EDGE:SLOPE FALL')

    # ARMED indicates that the instrument is acquiring pretrigger information.
    # AUTO indicates that the instrument is in the automatic mode and acquires data even in the absence of a trigger.
    # READY indicates that all pretrigger information is acquired and that the instrument is ready to accept a trigger.
    # SAVE indicates that the instrument is in save mode and is not acquiring data.
    # TRIGGER indicates that the instrument triggered and is acquiring the post trigger information.
    def get_trigger_status(self):
        return self.rm.query('TRIGGER:STATE?')


# Elektro-Automatik PSI91500-30
class PowerSupply():
    def __init__(self):
        with open('config.json') as file:
            self.config = json.load(file)['PowerSupply']
        visa = pyvisa.ResourceManager()
        try:
            self.rm = visa.open_resource(self.config['resource_name'])
        except Exception as err:
            err_msg = str(err)
            err_msg += "\n\n"
            err_msg += "No VISA device found with name: " + self.config['resource_name']
            raise Exception(err_msg)
        self.set_syst_lock_on()

    def set_syst_lock_on(self):
        self.rm.write('SYST:LOCK ON')

    def set_syst_lock_off(self):
        self.rm.write('SYST:LOCK OFF')

    def set_output_on(self):
        self.rm.write('OUTP ON')

    def set_output_off(self):
        self.rm.write('OUTP OFF')
    
    def set_voltage(self, voltage):
        self.rm.write('VOLT ' + str(voltage))

    def set_current(self, current):
        self.rm.write('CURR: ' + str(current))


# Aim CPX400SP DC Power Supply 60V/20A
class PowerSupplySmall():
    def __init__(self, vid=None, pid=None, stop_discovery=False):
        if not stop_discovery:
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if port.vid == vid and port.pid == pid:
                    self.serial = serial.Serial(port=port.name, write_timeout=5)
                    time.sleep(0.1)
            else:
                err_msg = "PowerSupplySmall not found:\n"
                err_msg += "VID: " + str(vid) + "\n"
                err_msg += "PID: " + str(pid) + "\n"
                raise Exception(err_msg)
            

    def send(self, cmd, wait=True):
        if self.serial.isOpen() == False:
            self.serial.open()
        self.serial.write((cmd+'\n').encode())
        if wait == True:
            resp = self.serial.readline().decode()
            self.serial.close()
            return resp
        else:
            return None

    def set_voltage(self, volts):
        return self.send('V1 '+str(volts), 0)

    def set_current(self, amps):
        return self.send('I1 '+str(amps), 0)

    def set_output_on(self):
        return self.send('OP1 1', wait=False)

    def set_output_off(self):
        return self.send('OP1 0', wait=False)

    def get_voltage(self):
        resp = self.send('V1O?')
        if resp == -1:
            return -1
        else:
            return float(resp[:5])

    def get_current(self):
        resp = self.send('I1O?')
        if resp == -1:
            return -1
        else:
            return float(resp[:5])

    def set_current_limit(self, amps):
        return self.send('I1 '+str(amps), wait=False)


# Control board with Raspberry Pi
class ControlBoard():
    def __init__(self):
        atexit.register(GPIO.cleanup)
        GPIO.setmode(GPIO.BCM)
        self.pins_in = {
            "HiVDS_ready": 27,
            "HiVG_ready": 24
        }
        self.pins_out = {
            "HiVDS_start": 17,
            "HiVG_start": 23
        }

        for pin in self.pins_in.values():
            GPIO.setup(pin, GPIO.IN)
        for pin in self.pins_out.values():
            GPIO.setup(pin, GPIO.OUT)

    def set_HiVDS_on(self):
        GPIO.output(self.pins_out["HiVDS_start"], GPIO.HIGH)

    def set_HiVDS_off(self):
        GPIO.output(self.pins_out["HiVDS_start"], GPIO.LOW)

    def get_HiVDS_is_enabled(self):
        return GPIO.input(self.pins_in["HiVDS_ready"])
    
    def set_HiVG_on(self):
        GPIO.output(self.pins_out["HiVG_start"], GPIO.HIGH)

    def set_HiVG_off(self):
        GPIO.output(self.pins_out["HiVG_start"], GPIO.LOW)

    def get_HiVG_is_enabled(self):
        return GPIO.input(self.pins_in["HiVG_ready"])


# Arduino Uno R3
class MicroController():
    def __init__(self):
        with open('config.json') as file:
            self.config = json.load(file)['MicroController']
        ports = serial.tools.list_ports.comports()
        arduino_port = None
        for port in ports:
            if port.vid == self.config['vid'] and port.pid == self.config['pid']:
                arduino_port = port.name
        self.ser = serial.Serial(arduino_port, baudrate=9600, dsrdtr=True, timeout=5)

    def send(self, msg):
        self.ser.write(json.dumps(msg).encode())
        resp = json.loads(self.ser.readline().decode())
        return resp

    def get_temperature(self):
        msg = {
            'cmd': 'getTemp'
        }
        return self.send(msg)
    
    def get_temperature_controller_target(self):
        msg = {
            'cmd': 'getTempTarget'
        }
        return self.send(msg)
    
    def get_temperature_controller_P(self):
        msg = {
            'cmd': 'getCoefP'
        }
        return self.send(msg)
    
    def get_temperature_controller_I(self):
        msg = {
            'cmd': 'getCoefI'
        }
        return self.send(msg)
    
    def set_temperature_controller_on(self):
        msg = {
            'cmd': 'enableTempController'
        }
        return self.send(msg)
    
    def set_temperature_controller_off(self):
        msg = {
            'cmd': 'disableTempController'
        }
        return self.send(msg)
    
    def set_temperature_controller_target(self, target):
        msg = {
            'cmd': 'setTempTarget',
            'tempTarget': target
        }
        return self.send(msg)
    
    def set_temperature_controller_P(self, coef):
        msg = {
            'cmd': 'setCoefP',
            'tempTarget': coef
        }
        return self.send(msg)
    
    def set_temperature_controller_I(self, coef):
        msg = {
            'cmd': 'setCoefI',
            'tempTarget': coef
        }
        return self.send(msg)
    
    def set_high_voltage_gate_on(self):
        msg = {
            'cmd': 'enableHiVG',
        }
        return self.send(msg)
    
    def set_high_voltage_gate_off(self):
        msg = {
            'cmd': 'disableHiVG',
        }
        return self.send(msg)
    
    def set_high_voltage_drain_source_on(self):
        msg = {
            'cmd': 'enableHiVDS',
        }
        return self.send(msg)
    
    def set_high_voltage_drain_source_off(self):
        msg = {
            'cmd': 'disableHiVDS',
        }
        return self.send(msg)


