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
    yzero = float(osc.rm.query('WFMO:YZE?'))
    ymult = float(osc.rm.query('WFMO:YMU?'))
    yoff = float(osc.rm.query('WFMO:YOF?'))
    values = osc.rm.query_ascii_values('CURV?')
    for i in range(len(values)):
        values[i] = yzero - yoff * ymult + ymult * values[i]
    return {
        'message': values
    }

function_map = {
    'drain_source_resistance': drain_source_resistance,
    'gate_q': gate_q,
    'gate_v_threshold': gate_v_threshold,
    'converter_ripple_relative': converter_ripple_relative,
    'converter_efficiency': converter_efficiency,
    'get_curve': get_curve
}