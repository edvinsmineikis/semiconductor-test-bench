from devices import *
import measurements
from datetime import datetime
import time

def fluctuating_temperature():
    ps = PowerSupply()
    osc = Oscilloscope()
    board = ControlBoard()

def high_voltage_to_gate():
    pass

def high_temperature_switching():
    pass

def degradation_test(minutes, minutes_step):
    def print_to_file(measurements):
        file = open('degradation_log.tsv', 'a')
        for meas in measurements:
            file.write(str(meas) + '\t')
        file.write('\n')
        file.close()

    osc = Oscilloscope()
    osc.set_channel(3)
    osc.set_measurement_type(1, 'MEAN')
    osc.set_measurement_type(2, 'PK2PK')

    minutes_passed = 0
    while minutes_passed <= minutes:
        mean = float(osc.get_measurement(1))
        pk2pk = float(osc.get_measurement(2))
        measurements = [mean, pk2pk, datetime.now()]
        print(measurements)
        print_to_file(measurements)
        minutes += minutes_step
        time.sleep(minutes_step * 60)