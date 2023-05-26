import time

def drain_source_resistance():
    pass

def gate_q():
    pass

def gate_v_threshold():
    pass

def converter_ripple_relative(instruments):
    osc = instruments['Oscilloscope']
    osc.set_channel(osc.config['converter_output_voltage_channel'])
    osc.set_measurement_type(1, 'RMS')
    osc.set_measurement_type(2, 'PK2PK')
    mean = float(osc.get_measurement_mean(1))
    pk2pk = float(osc.get_measurement_mean(2))
    return pk2pk/mean

def converter_efficiency(instruments):
    pass

def get_curve(instruments):
    osc = instruments['Oscilloscope']
    return osc.get_curve()