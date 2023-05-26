import measurements
from datetime import datetime
import time

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

def degradation_test(minutes, minutes_step):
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
        log_append('logs/degradation_test.tsv', measurements)
        minutes += minutes_step
        time.sleep(minutes_step * 60)
