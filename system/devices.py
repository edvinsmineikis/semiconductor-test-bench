import serial
import time
import pyvisa
import numpy as np

# TEKTRONIX TDS7104 Digital Phosphor Oscilloscope
class Oscilloscope():
    def __init__(self):
        # pyVisa initialization and selection of self.resourceillself.resourceope, presuming it is the only one.
        visa = pyvisa.ResourceManager()
        self.resource = visa.open_resource(visa.list_resources()[0])

        # By default we select channel 1 and ASCII encoding.
        self.resource.write('DATA:SOURCE CH1')
        self.resource.write('DATA:ENCDG ASCII')
        self.resource.write('DATA:WIDTH 1')

    # Returns a list of curve values in Volts, returns empty list upon failure.
    def get_curve(self):
        try:
            yzero = float(self.resource.query('WFMO:YZE?'))
            ymult = float(self.resource.query('WFMO:YMU?'))
            yoff = float(self.resource.query('WFMO:YOF?'))
            values = np.array(self.resource.query_ascii_values('CURV?'))
            for a in range(len(values)):
                values[a] = yzero - yoff * ymult + ymult * float(values[a])
            return values
        except:
            return []

    # Sets horizontal scale, input must be scientifically noted string, f.e.: '20e-9', which is 20ns/division. Returns 0 on success and -1 on failure.
    def set_horizontal_scale(self, scale):
        try:
            self.resource.write('HORIZONTAL:SAMPLERATE ' + scale)
            return 0
        except:
            return -1

    # Selects channel to write/read from, input is an int. Returns 0 on success and -1 on failure. Before changing any settings at all, a channel shall be defined.
    def select_channel(self, channel):
        try:
            self.resource.write('DATA:SOURCE CH' + str(channel))
            return 0
        except:
            return -1

    # Checks whether trigger is in auto or normal. Returns 0 for auto, 1 for normal, -1 for error.
    def trigger_is_enabled(self):
        try:
            resp = self.resource.query('TRIGGER:A:MODE?')
            if 'AUTO' in resp:
                return 0
            elif 'NORMAL' in resp:
                return 1
        except:
            return -1

    # Sets trigger to normal mode. Returns 0 on success, -1 on failure.
    def trigger_set_normal(self):
        try:
            self.resource.write('TRIGGER:A:MODE NORMAL')
            return 0
        except:
            return -1
    
    # Sets trigger to auto mode. Returns 0 on success, -1 on failure.
    def trigger_set_auto(self):
        try:
            self.resource.write('TRIGGER:A:MODE AUTO')
            return 0
        except:
            return -1
    
    # Sets channel used for edge trigger, takes int. Returns 0 on success and -1 on failure.
    def trigger_channel_mode_edge(self, channel):
        try:
            self.resource.write('TRIGGER:A:EDGE:SOURCE CH' + str(channel))
            return 0
        except:
            return -1

    # Sets channel used to set trigger level for particular channel, takes channel and level. Returns 0 on success and -1 on failure.
    def trigger_set_level(self, channel, level):
        try:
            self.resource.write('TRIGGER:A:LEVEL CH' + str(channel) + ' ' + str(level))
            return 0
        except:
            return -1

    # Sets edge trigger slope. 0 for Either, 1 for Rise, 2 for Fall. Returns 0 on success, -1 on failure.
    def trigger_set_slope(self, slope):
        try:
            if slope < 0 or slope > 2:
                return -1
            elif slope == 0:
                self.resource.write('TRIGGER:A:EDGE:SLOPE EITHER')
            elif slope == 1:
                self.resource.write('TRIGGER:A:EDGE:SLOPE RISE')
            elif slope == 2:
                self.resource.write('TRIGGER:A:EDGE:SLOPE FALL')
            return 0
        except:
            return -1


    # Returns -1 on failure, trigger status on success.
    # ARMED indicates that the instrument is acquiring pretrigger information.
    # AUTO indicates that the instrument is in the automatic mode and acquires data even in the absence of a trigger.
    # READY indicates that all pretrigger information is acquired and that the instrument is ready to accept a trigger.
    # SAVE indicates that the instrument is in save mode and is not acquiring data.
    # TRIGGER indicates that the instrument triggered and is acquiring the post trigger information.
    def trigger_status(self):
        try:
            resp = self.resource.query('TRIGGER:STATE?')
            return resp
        except:
            return -1

# Elektro-Automatik PSI9500
class PowerSupply():
    def __init__(self):
        COM_PORT = 'COM15'
        self.serial = serial.serial(port=COM_PORT, write_timeout=5)
        time.sleep(0.5)

    def send(self, cmd, wait):
        if serial.isOpen() == False:
            serial.open()
        serial.write((cmd+'\n').encode())
        if wait == 0:
            return 0
        else:
            resp = serial.readline().decode()
            serial.close()
            return resp
        
    def syst_lock_on(self):
        return self.send('SYST:LOCK ON', 0)

    def output_on(self):
        return self.send('OUTP ON', 0)

    def output_off(self):
        return self.send('OUTP OFF', 0)

# Aim CPX400SP DC Power Supply 60V/20A
class PowerSupplySmall():
    def __init__(self):
        COM_PORT = 'COM12'
        self.serial = serial.Serial(port=COM_PORT, write_timeout=5)
        time.sleep(0.5)

    # Set wait to nonzero value if you need a response. Otherwise function will return 0 on success or -1 on failure.
    def send(self, cmd, wait):
        #try:
            if self.serial.isOpen() == False:
                self.serial.open()
            self.serial.write((cmd+'\n').encode())
            if wait == 0:
                return 0
            else:
                resp = self.serial.readline().decode()
                self.serial.close()
                return resp
        #except:
        #    return -1

    def set_v(self, volts):
        return self.send('V1 '+str(volts), 0)

    def set_i(self, amps):
        return self.send('I1 '+str(amps), 0)

    def output_on(self):
        return self.send('OP1 1', 0)

    def output_off(self):
        return self.send('OP1 0', 0)

    def get_v(self):
        resp = self.send('V1O?', 1)
        if resp == -1:
            return -1
        else:
            return float(resp[:5])

    def get_i(self):
        resp = self.send('I1O?', 1)
        if resp == -1:
            return -1
        else:
            return float(resp[:5])

    def set_i_limit(self, amps):
        return self.send('I1 '+str(amps), 0)
