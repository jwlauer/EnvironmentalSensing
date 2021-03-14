#Example Code for controlling Pololu DRV8838 motor driver
#power for motor should be wired to VIN and GND pins--this should not
#be taken from the microcontroller (e.g., it should not be 3V3).  It
#is better to connect battery directly.

import pyb, time
en = pyb.Pin('Y3', pyb.Pin.OUT_PP) #this pin enables the motor and controls speed if set to Pulse Width Modulation mode (PWM)
ph = pyb.Pin('Y2', pyb.Pin.OUT_PP)  #this pin controls direction of motor
sl = pyb.Pin('Y1', pyb.Pin.OUT_PP)   #this pin, if low, can put the motor driver to sleep to save power

sl.value(0)  #turns off power
sl.value(1)  #turns on power to Pololu DRV8838

en.value(1)  #turns motor on
time.sleep(1)
en.value(0)  #turns motor off
time.sleep(1)

ph.value(1)  #switches direction
en.value(1)  #turns motor on
time.sleep(1)
en.value(0)  #turns motor off


#to control speed, set enable pin to pwm mode and then change pulse_width_percentage
from pyb import Timer
tim = Timer(4, freq=10000)
ch = tim.channel(3, Timer.PWM, pin=en)
ch.pulse_width_percent(50)
time.sleep(1)
ch.pulse_width_percent(25)
time.sleep(1)
ch.pulse_width_percent(0)

#ramp speed up slowly
for speed in range(80):
    ch.pulse_width_percent(speed)
    time.sleep(0.1)
#slow down slowly
for speed in range(80):
    ch.pulse_width_percent(80-speed)
    time.sleep(0.1)
#deinitialize timer
tim.deinit()

#redefine pin to set back to on/off mode
en = pyb.Pin('Y3', pyb.Pin.OUT_PP)  #this pin enables the motor and controls speed if set to Pulse Width Modulation mode (PWM)
en.value(1)  #turns motor on
time.sleep(1)
en.value(0)  #turns motor off

