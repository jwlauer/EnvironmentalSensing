#0 to 1.1V VWC= 10*V-1
#1.1V to 1.3V VWC= 25*V- 17.5
#1.3V to 1.82V VWC= 48.08*V- 47.5
#1.82V to 2.2V VWC= 26.32*V- 7.89

import machine
from machine import Pin
import utime
from machine import ADC
adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)  #Voltage range 0 (0) V to 3.6 V (4095)

while True:
    adc_count = adc.read()
    V = adc_count / 4095 * 3.6  
    if V < 1.1:
        VWC = 10*V-1
    elif V < 1.3:
        VWC = 25*V-17.5
    elif V < 1.82:
        VWC = 48.08*V-47.5
    elif V < 2.2:
        VWC = 26.32*V-7.89
    else:
        VWC = -999
    print('ADC = %s; V = %s; VWC = %s' %(adc_count, V, VWC))
    #print(adc_count)
    utime.sleep(1)
