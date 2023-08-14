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


def degradation_test(instruments, minutes, minutes_step):
    config = instruments.get_config()["Tests"]["degradation_test"]
    osc = instruments["Oscilloscope"]
    v_ch = str(config["voltage_channel"])
    i_ch = str(config["current_channel"])
    osc.query("DATA:SOURCE CH" + v_ch)
    osc.query("MEASUREMENT:MEAS1:TYPE RMS")
    osc.query("MEASUREMENT:MEAS2:TYPE PK2PK")
    osc.query("DATA:SOURCE CH" + i_ch)
    osc.query("MEASUREMENT:MEAS1:TYPE RMS")
    ps = instruments["PowerSupplySmall"]
    ps.query("OP1 0")
    ps.query("V1 10")
    ps.query("I1 " + str(config["input_current"]))
    ps.query("OP1 1")
    minutes_passed = 0
    R = config["shunt_resistance"]
    while minutes_passed <= minutes:
        v_in = float(ps.rm.query("V1O?").strip("V\r\n"))
        i_in = float(ps.rm.query("I1O?").strip("A\r\n"))
        osc.query("DATA:SOURCE CH" + v_ch)
        v_out = float(osc.rm.query("MEASUREMENT:MEAS1:MEAN?").strip("\r\n"))
        pk2pk = float(osc.rm.query("MEASUREMENT:MEAS2:MEAN?").strip("\r\n"))
        osc.query("DATA:SOURCE CH" + i_ch)
        i_out = float(osc.rm.query("MEASUREMENT:MEAS1:MEAN?").strip("\r\n")) / R
        measurements = [v_in, i_in, v_out, i_out, pk2pk]
        print(measurements)
        log_append("logs/degradation_test.tsv", measurements)
        minutes += minutes_step
        time.sleep(minutes_step * 60)


def thermal_cycling(instr_dict):
    osc = instr_dict["Oscilloscope"]
    ps = instr_dict["PowerSupply"]
    cb = instr_dict["ControlBoard"]

    config = instruments.get_config()
    test_config = config["Tests"]["thermal_cycling"]

    u_ds_ch = str(config["Oscilloscope"]["u_ds_ch"])
    u_gate_ch = str(config["Oscilloscope"]["u_gate_ch"])
    i_ch = str(config["Oscilloscope"]["i_ch"])
    osc.query("TRIGGER:A:MODE NORMAL")
    osc.query("TRIGGER:A:EDGE:SOURCE CH" + u_gate_ch)
    osc.query("TRIGGER:A:LEVEL CH 6")

    ps.query("SYST:LOCK ON")
    time.sleep(1)
    ps.query("VOLT " + str(test_config["voltage"]))
    ps.query("CURR " + str(test_config["current"]))
    ps.query("OUTP ON")
    cb.query("setPwm 255")
    cb.query("enableHiVds 0")
    time.sleep(2)

    for i in range(test_config["cycles"]):
        print(str(i) + "/" + str(test_config["cycles"]))

        osc.query("")
        cb.query("enablePwmRelay 0")
        time.sleep(1)
        osc.query("DATA:SOURCE CH" + u_ds_ch)
        values_u_ds = measurements.get_curve(instr_dict)["message"]
        osc.query("DATA:SOURCE CH" + i_ch)
        values_i = measurements.get_curve(instr_dict)["message"]
        cb.query("disablePwmRelay 0")

        gen_plot(values_u_ds, "plots/plot_ds.png")
        gen_plot(values_i, "plots/plot_i.png")

        exit()

        while True:
            temp = cb.query("getTemp 0")["temp"]
            print(temp)
            log_append("thermal.log", [temp])
            time.sleep(1.0)
            if temp > test_config["temp_max"]:
                cb.query("enableFan 0")
                cb.query("disablePwmRelay 0")
                while True:
                    temp = cb.query("getTemp 0")["temp"]
                    print(temp)
                    log_append("thermal.log", [temp])
                    time.sleep(1.0)
                    if temp < test_config["temp_min"]:
                        cb.query("disableFan 0")
                        break
                break

    cb.query("disablePwmRelay 0")
    cb.query("disableHiVds 0")
    ps.query("OUTP OFF")
