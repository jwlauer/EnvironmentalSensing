import machine
from machine import Pin, ADC
import time
import math
import array as arr

#sampling parameters
n = 12 #number of samples per measurement
cycle_time = 1000
[on1,off1,on2,off2] = [cycle_time,cycle_time,cycle_time,cycle_time] #sleep time in microseconds
printflag = 1

#conductivity resistor value
con_resistance = 1000

#max ADC count
max_count = 8191 #for ESP32S21 in single read mode
attenuation_code = ADC.ATTN_11DB #ADC attenuation mode--specifies max readable voltage
max_voltage = 2.5 #max readable voltage according to espressif docs for 11DB atten

#define gpio pins--consistent with ESP32-S2 Feather S2
gpio1 = Pin(11, Pin.OUT)
adc1 = ADC(Pin(9))
adc2 = ADC(Pin(10))
gpio2 = Pin(12, Pin.OUT)
therm_power = Pin(13, Pin.OUT)
adc3_current = ADC(Pin(6))
adc_therm = ADC(Pin(5))

#set attenuation so that maximum voltage is about 2.1V
adc1.atten(ADC.ATTN_11DB)
adc2.atten(ADC.ATTN_11DB)
adc3_current.atten(ADC.ATTN_11DB)
adc_therm.atten(ADC.ATTN_11DB)

#pre-allocate arrays for counts to be read into
imeas1 = arr.array('l',[0]*n)
imeas2 = arr.array('l',[0]*n)
p3meas1 = arr.array('l',[0]*n)
p3meas2 = arr.array('l',[0]*n)
p4meas1 = arr.array('l',[0]*n)
p4meas2 = arr.array('l',[0]*n)


starttime = time.ticks_us()
for i in range(n):
    gpio1.value(1)
    time.sleep_us(on1)
    imeas1[i] = adc3_current.read()
    p3meas1[i] = adc1.read()
    p4meas1[i] = adc2.read()
    gpio1.value(0)
    time.sleep_us(off1)
    
    gpio2.value(1)
    time.sleep_us(on2)
    imeas2[i] = adc3_current.read()
    p3meas2[i] = adc1.read()
    p4meas2[i] = adc2.read()
    gpio2.value(0)
    time.sleep_us(off2)

endtime = time.ticks_us()
elapsed_time = endtime - starttime
meas_freq = n/(elapsed_time/1000000)
print('freq = ', meas_freq)

#pre-allocate arrays for current, voltage drop across poles, and resistance, for flow each direction
i1 = arr.array('f',[0]*n)
i2 = arr.array('f',[0]*n)
V1 = arr.array('f',[0]*n)
V2 = arr.array('f',[0]*n)
R1 = arr.array('f',[0]*n)
R2 = arr.array('f',[0]*n)

#compute current, voltage, and resistance for each sample (do outside sampling loop to maintain sampling timing)
for i in range(n):
    try:
        i1[i] = imeas1[i] / max_count * max_voltage / con_resistance 
        i2[i] = (max_voltage - imeas2[i] /max_count * max_voltage) / con_resistance
        V1[i] = (p3meas1[i] - p4meas1[i])/max_count * max_voltage
        V2[i] = (p4meas2[i] - p3meas2[i])/max_count * max_voltage
        R1[i] = V1[i]/i1[i]
        R2[i] = V2[i]/i2[i]
    except:
        R1[i] = -999999
        R2[i] = -999999
        print('Error in resistance computation')

#clean data by sampling middle two quartiles       
upper_index = math.ceil(3*n/4)
lower_index = math.floor(n/4)
sampled_length = (upper_index - lower_index)
resistance1 = sum(sorted(R1)[lower_index:upper_index])/sampled_length
resistance2 = sum(sorted(R2)[lower_index:upper_index])/sampled_length

icount1 = sum(sorted(imeas1)[lower_index:upper_index])/sampled_length
probe3count1 = sum(sorted(p3meas1)[lower_index:upper_index])/sampled_length
probe4count1 = sum(sorted(p4meas1)[lower_index:upper_index])/sampled_length
icount2 = sum(sorted(imeas2)[lower_index:upper_index])/sampled_length
probe3count2 = sum(sorted(p3meas2)[lower_index:upper_index])/sampled_length
probe4count2 = sum(sorted(p4meas2)[lower_index:upper_index])/sampled_length


#call thermistor reading, with 400 adc readings per measurement
#self.T = thermistor_ac.temperature(self.adc_therm, self.therm_power, self.therm_ground, self.therm_resistance, 400)        
#self.k = self.conductivity(self.resistance2,self.A,self.B,self.C)
#self.S = self.salinity(self.T, self.k)
#self.k25 = self.k25(self.k,self.T)
    
if printflag:
    for i in range (n):
        print('R1 = %s, R2 = %s, V1 = %s, V2 = %s, i1 = %s, i2 = %s, p3count1 = %s, p3count2 = %s, p4count1 = %s, p4count2 = %s' % (R1[i], R2[i], V1[i], V2[i], i1[i], i2[i], p3meas1[i], p3meas2[i], p4meas1[i], p4meas2[i]))
    print('elapsed time = %s micro seconds' % (elapsed_time))
    print('speed = %s Hz' % (n/elapsed_time*1000000))
    
