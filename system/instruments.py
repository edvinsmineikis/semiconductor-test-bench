import serial
import serial.tools.list_ports
import pyvisa
import numpy as np
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

# TEKTRONIX DPO 7054 Digital Phosphor Oscilloscope
class Oscilloscope():
    def __init__(self):
        self.config = get_config()['Oscilloscope']
        self.rm = pyvisa.ResourceManager().open_resource(get_pyvisa_resource(self.config['serial']))
        self.rm.write('DATA:ENCDG ASCII')
        self.rm.write('DATA:WIDTH 1')

    def get_curve(self):
        yzero = float(self.rm.query('WFMO:YZE?'))
        ymult = float(self.rm.query('WFMO:YMU?'))
        yoff = float(self.rm.query('WFMO:YOF?'))
        values = np.array(self.rm.query_ascii_values('CURV?'))
        for a in range(len(values)):
            values[a] = yzero - yoff * ymult + ymult * float(values[a])
        return values

    # Returns AUTO or NORMAL.
    def get_trigger_mode(self):
        return self.rm.query('TRIGGER:A:MODE?')
    
    def get_measurement_value(self, index):
        return self.rm.query('MEASUREMENT:MEAS' + str(index) + ':VALUE?')
    
    def get_measurement_mean(self, index):
        return self.rm.query('MEASUREMENT:MEAS' + str(index) + ':MEAN?')
    
    def set_autoset(self):
        self.rm.write('AUTOSET EXECUTE')

    def set_measurement_type(self, index, type):
        self.rm.write('MEASUREMENT:MEAS' + str(index) + ':TYPE '+type)

    # '1e-3' sets scale to 1ms per devision
    def set_horizontal_scale(self, scale):
        self.rm.write('HORIZONTAL:SCALE ' + scale)

    # '1e6' sets the sample rate to 1 million samples per second
    def set_horizontal_sample_rate(self, rate):
        self.rm.write('HORIZONTAL:MODE:SAMPLERATE ' + rate)

    def set_channel(self, channel):
        self.rm.write('DATA:SOURCE CH' + str(channel))

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
        self.config = get_config()['PowerSupply']
        self.rm = pyvisa.ResourceManager().open_resource(get_pyvisa_resource(self.config['serial']))
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
                    return
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


# Arduino Uno R3 + Control board
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

    def send(self, msg):
        self.ser.write(json.dumps(msg).encode())
        self.ser.write(b'\n')
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
    
    def set_gs_relay_on(self):
        msg = {
            'cmd': 'enableGsRelay',
        }
        return self.send(msg)
    
    def set_gs_relay_off(self):
        msg = {
            'cmd': 'disableGsRelay',
        }
        return self.send(msg)
    
    def set_pwm_duty(self, value):
        msg = {
            'cmd': 'setPwm',
            'value': value
        }
        return self.send(msg)
    
    def set_pwm_on(self):
        msg = {
            'cmd': 'setPwmOn',
        }
        return self.send(msg)
    
    def set_pwm_off(self):
        msg = {
            'cmd': 'setPwmOff',
        }
        return self.send(msg)



