import machine
switch=machine.Pin(5,machine.Pin.OUT)
switch.value(1)
int_led=machine.Pin(2,machine.Pin.OUT)
int_led.value(0)

import machine
import time
    data1 = (1, 2, 3)

    data2 = (4, 5, 6)

    
    time.sleep(20.0)
    
    switch.value(0)
    