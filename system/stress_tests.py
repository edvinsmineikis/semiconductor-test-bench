import measurements
from instruments import *
from datetime import datetime
import time
import atexit

def log_append(filename, columns):
    with open(filename, 'a') as file:
        for column in columns:
            file.write(str(column) + '\t')
        file.write('\n')

def fluctuating_temperature():
    pass

def high_voltage_to_gate():
    pass

def high_temperature_switching():
    pass

def degradation_test(instruments, minutes, minutes_step):
    config = get_config()['Tests']['degradation_test']
    osc = instruments['Oscilloscope']
    v_ch = str(config['voltage_channel'])
    i_ch = str(config['current_channel'])
    osc.query('DATA:SOURCE CH' + v_ch)
    osc.query('MEASUREMENT:MEAS1:TYPE RMS')
    osc.query('MEASUREMENT:MEAS2:TYPE PK2PK')
    osc.query('DATA:SOURCE CH' + i_ch)
    osc.query('MEASUREMENT:MEAS1:TYPE RMS')
    ps = instruments['PowerSupplySmall']
    ps.query('OP1 0')
    ps.query('V1 10')
    ps.query('I1 '+str(config['input_current']))
    ps.query('OP1 1')
    minutes_passed = 0
    R = config['shunt_resistance']
    while minutes_passed <= minutes:
        v_in = float(ps.rm.query('V1O?').strip('V\r\n'))
        i_in = float(ps.rm.query('I1O?').strip('A\r\n'))
        osc.query('DATA:SOURCE CH' + v_ch)
        v_out = float(osc.rm.query('MEASUREMENT:MEAS1:MEAN?').strip('\r\n'))
        pk2pk = float(osc.rm.query('MEASUREMENT:MEAS2:MEAN?').strip('\r\n'))
        osc.query('DATA:SOURCE CH' + i_ch)
        i_out = float(osc.rm.query('MEASUREMENT:MEAS1:MEAN?').strip('\r\n'))/R
        measurements = [v_in, i_in, v_out, i_out, pk2pk, datetime.now()]
        print(measurements)
        log_append('logs/degradation_test.tsv', measurements)
        minutes += minutes_step
        time.sleep(minutes_step * 60)

def atexit_outputs_off():
    instruments['PowerSupplySmall'].query('OP1 0')

if __name__ == '__main__':
    atexit.register(atexit_outputs_off)
    
    instruments = {
        'Oscilloscope': Oscilloscope(),
        'PowerSupplySmall': PowerSupplySmall()
    }
    
    degradation_test(instruments, 60*8, 1)

