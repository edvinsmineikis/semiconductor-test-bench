import serial
import time

# Serial definition upon import. It is good to have a delay between definition and writing.
COM_PORT = 'COM15'
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
    
def syst_lock_on():
    return send('SYST:LOCK ON', 0)

def output_on():
    return send('OUTP ON', 0)
