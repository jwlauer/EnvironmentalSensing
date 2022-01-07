import time
import machine
from machine import Pin
machine.freq(40000000)  #save power/battery by reducing processor speed

interval = 2  #minutes
led = Pin(13, Pin.OUT)
power = Pin(18, Pin.OUT)
led.off()
power.off()
time.sleep(1)
trigger = Pin(17, Pin.IN)


while True:
    print(trigger.value())
    if trigger.value() == True:
        led.on()
        power.on()
        time.sleep(15)
        led.off()
        power.off()
    time.sleep(1)