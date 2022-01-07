import time
import machine
from machine import Pin
machine.freq(40000000)  #save power/battery by reducing processor speed

interval = 2  #minutes

power = Pin(13,Pin.OUT)
time.sleep(15)
while True:
    power.on()
    time.sleep(15)
    power.off()
    time.sleep(interval*60-15)