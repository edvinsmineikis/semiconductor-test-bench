import pyvisa
import numpy as np

# pyVisa initialization and selection of oscilloscope, presuming it is the only one.
visa = pyvisa.ResourceManager()
osc = visa.open_resource(visa.list_resources()[0])

# By default we select channel 1 and ASCII encoding.
osc.write('DATA:SOURCE CH1')
osc.write('DATA:ENCDG ASCII')
osc.write('DATA:WIDTH 1')


# Returns a list of curve values in Volts, returns empty list upon failure.
def get_curve():
    try:
        yzero = float(osc.query('WFMO:YZE?'))
        ymult = float(osc.query('WFMO:YMU?'))
        yoff = float(osc.query('WFMO:YOF?'))
        values = np.array(osc.query_ascii_values('CURV?'))
        for a in range(len(values)):
            values[a] = yzero - yoff * ymult + ymult * float(values[a])
        return values
    except:
        return []

# Sets horizontal scale, input must be scientifically noted string, f.e.: '20e-9', which is 20ns/division. Returns 0 on success and -1 on failure.
def set_horizontal_scale(scale):
    try:
        osc.write('HORIZONTAL:SAMPLERATE ' + scale)
        return 0
    except:
        return -1

# Selects channel to write/read from, input is an int. Returns 0 on success and -1 on failure. Before changing any settings at all, a channel shall be defined.
def select_channel(channel):
    try:
        osc.write('DATA:SOURCE CH' + str(channel))
        return 0
    except:
        return -1

# Checks whether trigger is in auto or normal. Returns 0 for auto, 1 for normal, -1 for error.
def trigger_is_enabled():
    try:
        resp = osc.query('TRIGGER:A:MODE?')
        if 'AUTO' in resp:
            return 0
        elif 'NORMAL' in resp:
            return 1
    except:
        return -1

# Sets trigger to normal mode. Returns 0 on success, -1 on failure.
def trigger_set_normal():
    try:
        osc.write('TRIGGER:A:MODE NORMAL')
        return 0
    except:
        return -1

# Sets trigger to auto mode. Returns 0 on success, -1 on failure.
def trigger_set_auto():
    try:
        osc.write('TRIGGER:A:MODE AUTO')
        return 0
    except:
        return -1

# Sets channel used for edge trigger, takes int. Returns 0 on success and -1 on failure.
def trigger_channel_mode_edge(channel):
    try:
        osc.write('TRIGGER:A:EDGE:SOURCE CH' + str(channel))
        return 0
    except:
        return -1

# Sets channel used to set trigger level for particular channel, takes channel and level. Returns 0 on success and -1 on failure.
def trigger_set_level(channel, level):
    try:
        osc.write('TRIGGER:A:LEVEL CH' + str(channel) + ' ' + str(level))
        return 0
    except:
        return -1

# Sets edge trigger slope. 0 for Either, 1 for Rise, 2 for Fall. Returns 0 on success, -1 on failure.
def trigger_set_slope(slope):
    try:
        if slope < 0 or slope > 2:
            return -1
        elif slope == 0:
            osc.write('TRIGGER:A:EDGE:SLOPE EITHER')
        elif slope == 1:
            osc.write('TRIGGER:A:EDGE:SLOPE RISE')
        elif slope == 2:
            osc.write('TRIGGER:A:EDGE:SLOPE FALL')
        return 0
    except:
        return -1
        

# Returns -1 on failure, trigger status on success.
# ARMED indicates that the instrument is acquiring pretrigger information.
# AUTO indicates that the instrument is in the automatic mode and acquires data even in the absence of a trigger.
# READY indicates that all pretrigger information is acquired and that the instrument is ready to accept a trigger.
# SAVE indicates that the instrument is in save mode and is not acquiring data.
# TRIGGER indicates that the instrument triggered and is acquiring the post trigger information.
def trigger_status():
    try:
        resp = osc.query('TRIGGER:STATE?')
        return resp
    except:
        return -1






