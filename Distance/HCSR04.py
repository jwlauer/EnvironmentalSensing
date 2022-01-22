import machine
from machine import Pin
import os, time

#configure devices
triggerPin = Pin(12, Pin.OUT)
triggerPin.value(0)
echoPin = Pin(13, Pin.IN)

def distance():
  #trigger the pin
  triggerPin.value(1)
  time.sleep_us(10)
  triggerPin.value(0)
  #read time until the echo
  pulse_time = machine.time_pulse_us(echoPin, 1)

  #calculate speed of sound
  #[T1,P1,H1] = bme1.raw_values
  T1 = 293 #Assume Room Temperature--better to read from sensor
  c = 331.3 + 0.606*T1    # in m/s

  #calculate distance
  distance = (pulse_time / 2)/1000000 * c
  return distance
