import machine
from machine import Pin, ADC
import time
import math
import array as arr

adc = ADC(Pin(10))
adc.atten(ADC.ATTN_11DB)

R1 = 8970
R2 = 9030
V33 = 3.3
V = 3.3*R2/(R1+R2)
readings = []
maxcount = 8191

n = 0
total = 0
while True:
    n = n+1
    total = total + adc.read()
    average = total / n 
       
    vmax = V * maxcount / average
    
    print(f"average = {average}, vmax = {vmax}")