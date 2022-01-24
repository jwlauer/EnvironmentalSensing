import machine
from machine import Pin, ADC
import time
import math

therm_resistance = 10000 #resistor in line with thermistor

#max ADC count
max_count = 8191 #for ESP32S21 in single read mode
attenuation_code = ADC.ATTN_11DB #ADC attenuation mode--specifies max readable voltage
max_voltage = 2.730 #max readable voltage according to espressif docs for 11DB atten

#define gpio pins--consistent with ESP32-S2 Feather S2
adc_therm = ADC(Pin(5))
therm_power = Pin(13, Pin.OUT)
therm_power.value(1)

#set attenuation so that maximum voltage is about 2.5V
adc_therm.atten(ADC.ATTN_11DB)

A = 0.001125308852122
B = 0.000234711863267
C = 0.000000085663516

while True:
    therm_count = adc_therm.read()
    therm_voltage = therm_count / max_count * max_voltage
    therm_i = therm_voltage / therm_resistance
    R_t = (3.3 - therm_voltage)/therm_i
    T = 1/((A+B*(math.log(R_t)))+C*((math.log(R_t))**3))-273.15
    print(f'T={T}')
