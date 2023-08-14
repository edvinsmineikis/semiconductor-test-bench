import instruments
import matplotlib.pyplot as plt
import tests

instr_dict = {
    "Oscilloscope": instruments.Oscilloscope(),
    "ControlBoard": instruments.ControlBoard(),
    "PowerSupply": instruments.PowerSupply()
}

tests.thermal_cycling(instr_dict)



