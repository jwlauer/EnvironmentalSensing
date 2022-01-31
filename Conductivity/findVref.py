#import libraries
import machine
from machine import Pin, ADC
import time

#specify parameters
n = 20 #number of samples to average
R1 = 10000
R2 = 10000
v33 = 3.30
#compute v_data
v_data = 3.3*R2/(R1+R2)

#initialize ADC
try:
    #works for ESP8266
    adc = ADC(0)
    maxcount = 1023
except:
    #works for ESP32
    adc = ADC(Pin(5))
    adc.atten(ADC.ATTN_11DB)
    maxcount = 8191  #4095 if ESP32

#Collect n measurements, average, and print results
total = 0
for i in range(20):
    total = total + adc.read()
    time.sleep(0.2) #necessary to give ADC time to reset
c_adc_av = total / n 
v_ref = v_data * maxcount / c_adc_av
print(f"n = {n}, average ADC count = {c_adc_av}, average Vref = {v_ref}")