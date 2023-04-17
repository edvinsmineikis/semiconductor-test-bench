from devices import CPX400SP
import time

#CPX400SP.output_off()
#exit()
CPX400SP.set_i_limit(5)

my_volts = 0.1

CPX400SP.set_v(my_volts)

CPX400SP.output_on()

while CPX400SP.get_i() < 4:
    time.sleep(1)
    print('V: '+str(CPX400SP.get_v()))
    print('I: '+str(CPX400SP.get_i())+'\n')
    my_volts += 0.01
    CPX400SP.set_v(my_volts)

CPX400SP.output_off()
#Helloworld
