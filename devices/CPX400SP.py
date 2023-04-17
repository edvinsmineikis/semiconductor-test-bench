import serial
import time

# Serial definition upon import. It is good to have a delay between definition and writing.
COM_PORT = 'COM12'
ser = serial.Serial(port=COM_PORT, write_timeout=5)
time.sleep(0.5)

# Set wait to nonzero value if you need a response. Otherwise function will return 0 on success or -1 on failure.
def send(cmd, wait):
    #try:
        if ser.isOpen() == False:
            ser.open()
        ser.write((cmd+'\n').encode())
        if wait == 0:
            return 0
        else:
            resp = ser.readline().decode()
            ser.close()
            return resp
    #except:
    #    return -1

def set_v(volts):
    return send('V1 '+str(volts), 0)

def set_i(amps):
    return send('I1 '+str(amps), 0)

def output_on():
    return send('OP1 1', 0)

def output_off():
    return send('OP1 0', 0)

def get_v():
    resp = send('V1O?', 1)
    if resp == -1:
        return -1
    else:
        return float(resp[:5])

def get_i():
    resp = send('I1O?', 1)
    if resp == -1:
        return -1
    else:
        return float(resp[:5])

def set_i_limit(amps):
    return send('I1 '+str(amps), 0)
