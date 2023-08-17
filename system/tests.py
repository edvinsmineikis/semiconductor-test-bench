import measurements
import instruments
from datetime import datetime
import time
import matplotlib.pyplot as plt


def gen_plot(data, path):
    plt.figure()
    plt.plot(data)
    plt.savefig(path)
    plt.close()


def log_append(filename, row):
    with open(filename, "a") as file:
        file.write(str(datetime.now()) + "\t")
        for column in row:
            file.write(str(column) + "\t")
        file.write("\n")


def thermal_cycling(instr_dict):
    def stop_everything():
        ps.query("OUTP OFF")
        cb.query("disablePwmRelay 0")
        cb.query("setPwm 0")
        cb.query("disableHiVds 0")

    def print_params(save=False):
        temp = cb.query("getTemp 0")["temp"]
        u_in = float(ps.query("MEAS:VOLT?")["message"].split(" ")[0])
        i_in = float(ps.query("MEAS:CURR?")["message"].split(" ")[0])
        u_ds = float(osc.query("MEASUREMENT:MEAS1:VALUE?")["message"])
        u_gate = float(osc.query("MEASUREMENT:MEAS2:VALUE?")["message"])
        i_drain = float(osc.query("MEASUREMENT:MEAS4:VALUE?")["message"])
        if save is True:
            log_append("thermal.log", [u_in, i_in, u_ds, u_gate, i_drain, temp])
        print([u_in, i_in, u_ds, i_drain, u_gate, temp])
        
        error_condition = (
            ("No error" not in ps.query("SYST:ERR?")["message"])
        )
        if error_condition is True:
            stop_everything()
            exit("SOMETHING WENT WRONG")

    osc = instr_dict["Oscilloscope"]
    ps = instr_dict["PowerSupply"]
    cb = instr_dict["ControlBoard"]

    config = instruments.get_config()
    test_config = config["Tests"]["thermal_cycling"]

    temp_target = test_config["temp_min"]
    cb.query("setTempTarget " + str(temp_target))
    cb.query("enableHiVds 0")
    cb.query("setPwm 128")

    u_ds_ch = str(config["Oscilloscope"]["u_ds_ch"])
    u_gate_ch = str(config["Oscilloscope"]["u_gate_ch"])
    i_ch = str(config["Oscilloscope"]["i_ch"])

    osc.query("CH" + str(u_ds_ch) + ":SCALE " + str(test_config["u_ds_scale"]))
    osc.query("CH" + str(u_gate_ch) + ":SCALE " + str(test_config["u_gate_scale"]))
    osc.query("CH" + str(i_ch) + ":SCALE " + str(test_config["i_scale"]))

    # osc.query("TRIGGER:A:MODE NORMAL")
    # osc.query("TRIGGER:A:EDGE:SOURCE CH" + u_gate_ch)
    # osc.query("TRIGGER:A:LEVEL 6")

    ps.query("SYST:LOCK ON")
    ps.query("SYST:ERR:ALL?")
    ps.query("VOLT " + str(test_config["voltage"]))
    ps.query("CURR " + str(test_config["current"]))
    ps.query("CURR:PROT " + str(test_config["current"]))
    ps.query("OUTP ON")

    time.sleep(1)

    for i in range(test_config["cycles"]):
        print(str(i) + "/" + str(test_config["cycles"]))

        cb.query("enablePwmRelay 0")
        cb.query("setPwm 128")
        ps.query("OUTP ON")
        time.sleep(1)

        # osc.query("DATA:SOURCE CH" + u_ds_ch)
        # values_u_ds = measurements.get_curve(instr_dict)["message"]
        # osc.query("DATA:SOURCE CH" + i_ch)
        # values_i = measurements.get_curve(instr_dict)["message"]
        # gen_plot(values_u_ds, "plots/plot_ds.png")
        # gen_plot(values_i, "plots/plot_i.png")

        while True:
            temp = cb.query("getTemp 0")["temp"]
            print_params()
            time.sleep(1.0)
            if temp > test_config["temp_max"]:
                cb.query("enableFan 0")
                cb.query("disablePwmRelay 0")
                cb.query("setPwm 0")
                ps.query("OUTP OFF")
                while True:
                    temp = cb.query("getTemp 0")["temp"]
                    print_params()
                    time.sleep(1.0)
                    if temp < test_config["temp_min"]:
                        cb.query("enableTempController 0")
                        break
                while True:
                    temp = cb.query("getTemp 0")["temp"]
                    print_params()
                    time.sleep(1.0)
                    if abs(temp_target - temp) < 0.5:
                        cb.query("disableTempController 0")
                        print_params(save=True)
                        break
                break

    stop_everything()
