import machine
from machine import Pin, ADC
import time
import math
import array as arr

#sampling parameters
n = 12 #number of samples per measurement
cycle_time = 100
[on1,off1,on2,off2] = [cycle_time,cycle_time,cycle_time,cycle_time] #sleep time in microseconds
printflag = 0  #flag for extra output

#resistor values 
con_resistance = 220 #resistor (ohms) on either end of conductivity cell
#therm_resistance = 9880 #resistor (ohms) in line with thermistor

#max ADC count
max_count = 4095 #for ESP32S3 in single read mode
attenuation_code = ADC.ATTN_11DB #ADC attenuation mode--specifies max readable voltage
max_voltage = 3.10 #max readable voltage--should be calibrated for 11DB atten

#define gpio pins
gpio1 = Pin(5, Pin.OUT)  #connects to electrode1 through con_resistance
adc3_current = ADC(Pin(17)) #connects directly to electrode2
adc1 = ADC(Pin(18))  #connects directly to electrode4
adc2 = ADC(Pin(14)) #connects directly to electrode3
adc4_current = ADC(Pin(12)) #connects directly to electrode1
gpio2 = Pin(6, Pin.OUT) #connects to electrode2 through con_resistance
#therm_power = Pin(13, Pin.OUT) #connects to either pole of NTC thermistor

#adc_therm = ADC(Pin(5)) #connects to either pole of NTC thermistor

#set attenuation so that maximum voltage is at highest possible level
adc1.atten(ADC.ATTN_11DB)
adc2.atten(ADC.ATTN_11DB)
adc3_current.atten(ADC.ATTN_11DB)
adc4_current.atten(ADC.ATTN_11DB)
#adc_therm.atten(ADC.ATTN_11DB)

#pre-allocate arrays that will store counts
imeas1 = arr.array('l',[0]*n)
imeas2 = arr.array('l',[0]*n)
p3meas1 = arr.array('l',[0]*n)
p3meas2 = arr.array('l',[0]*n)
p4meas1 = arr.array('l',[0]*n)
p4meas2 = arr.array('l',[0]*n)

def read():
    starttime = time.ticks_us()
    for i in range(n):
        #normal polarity
        gpio1.value(1)
        time.sleep_us(on1)
        imeas1[i] = adc4_current.read()
        #p3meas1[i] = adc1.read()
        #p4meas1[i] = adc2.read()
        p3meas1[i] = adc2.read()
        p4meas1[i] = adc1.read()
        gpio1.value(0)
        time.sleep_us(off1)
        
        #switched polarity
        gpio2.value(1)
        time.sleep_us(on2)
        imeas2[i] = adc3_current.read()
        #p3meas2[i] = adc1.read()
        #p4meas2[i] = adc2.read()
        p3meas2[i] = adc2.read()
        p4meas2[i] = adc1.read()

        gpio2.value(0)
        time.sleep_us(off2)
     
    endtime = time.ticks_us()
    elapsed_time = endtime - starttime
    meas_freq = n/(elapsed_time/1000000)

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
            i2[i] = imeas2[i] / max_count * max_voltage / con_resistance 
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
    resistance_average = (resistance1+resistance2)/2
    current1 = sum(sorted(i1)[lower_index:upper_index])/sampled_length
    current2 = sum(sorted(i2)[lower_index:upper_index])/sampled_length
    current_average = (current1+current2)/2

        
    #find maximum and minimum counts to see if out of range of ADC:
    arrays_of_counts = [imeas1, imeas2, p3meas1, p3meas2, p4meas1, p4meas2]
    oldmax = 0
    oldmin = max_count
    for array in arrays_of_counts:
        maximum = max(max(array),oldmax)
        minimum = min(min(array),oldmin)
        oldmax = maximum
        oldmin = minimum

    #Print output
    if printflag:
        for i in range (n):
            print(f"R1 = {R1[i]:.2f}, R2 = {R2[i]:.2f}, V1 = {V1[i]:.2f}, V2 = {V2[i]:.2f}, i1 = {i1[i]:.2f}, i2 = {i2[i]:.2f}")
            print(f"adc_count3 = {imeas2[i]}, adc_count4 = {imeas1[i]}, adc1_1 = {p3meas1[i]}, acd1_2 = {p4meas1[i]}, adc2_1 = {p4meas1[i]}, adc2_2 = {p4meas2[i]}")
    outputstring = f"R1 = {resistance1:.2f}, R2 = {resistance2:.2f}, R_av = {resistance_average:.2f}, "
    outputstring += f"i1 = {current1:.5f}, i2 = {current2:.5f}, i_av = {current_average:.5f}, "
    outputstring += f"freq = {meas_freq:.1f} hz, max_count = {maximum}, min_count = {minimum}"
    print(outputstring)
        

