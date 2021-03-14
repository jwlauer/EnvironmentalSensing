#import libraries.  Uses upower library to ensure it only does regular sleep if USB connected.
import upower, pyb, time
#import turb, DRV8838_test
import machine
from machine import Pin
import os, utime

#Define builtin LED
green = pyb.LED(2)
blue = pyb.LED(4)
sensorpower = Pin('X6', Pin.OUT)
sensorpower.value(1)
sensorground = Pin('X7', Pin.OUT)
sensorground.value(0)
ledpower = Pin('X8', Pin.OUT)
ledground = Pin('X4', Pin.OUT)
ledground.value(0)
sensor = Pin('X5', Pin.IN) #D3

en = pyb.Pin('X1', pyb.Pin.OUT_PP)  #this pin enables the motor and controls speed if set to Pulse Width Modulation mode (PWM)
ph = pyb.Pin('X2', pyb.Pin.OUT_PP)  #this pin controls direction of motor
sl = pyb.Pin('X3', pyb.Pin.OUT_PP)  #this pin, of low, can put the motor driver to sleep to save power

sl.value(0)  #turns off power
sl.value(1)  #turns on power to Pololu DRV8838

en.value(1)  #turns motor on
en.value(0) #turns motor off 

def pulse():  #An error in ESP8266 means that we can only time when light is on otherwise board resets
        en.value(1)
        ledpower.value(1)
        utime.sleep(3)
        PulsePin = Pin('X5', Pin.IN) #Most GPIO pins work
        #time the remainder of the first high pulse
        pulse_time = machine.time_pulse_us(PulsePin, 1, 1000000)
        #now time the next high pulse.  This ensures the entire pulse is counted.
        pulse_time = machine.time_pulse_us(PulsePin, 1, 1000000)
        ledpower.value(0)
        return pulse_time

#Define logging function that can be called at arbitrary interval (seconds)
def log(t):
    """ A function for logging data to file at a regular interval.
    
    The function saves a line of text at each interval representing conductivity, temperature,
    pressure. The device then goes into standby mode for interval t.  After interval t, the
    device awakes as if from a hard reset.  The function is designed to be called from
    main.py.

    Args:
        t: logging interval (seconds)

    Returns:
        Nothing--puts device into standby mode upon completion.
    
    Example:
        To log data at 30 second intervals, save the following two lines as main.py
        
        import logger
        logger.log(30)

    """
    

    nexttime = time.time()+t
    #write header line
    header = 'datetime,sensor\r\n'
    f = open('finallog.txt','a') 
    f.write(header)
    f.close()

    while True:
        #Wait until it's time to sample by blinking briefly, then sleeping in low power the rest of the second 
        while time.time()<nexttime:
            green.on()
            upower.lpdelay(4)
            green.off()
            upower.lpdelay(996)
            en.value(0)
            print('Just waiting for the right time')
        print('It\'s time!')
        #print (pulse(1))

        #Find next time to take a reading
        nexttime += t

        #Read sensor values
        sensor = pulse() 
        
        #Get time
        [year, month, day, hour, minute, second, weekday, yesterday] = time.localtime()
        
        #Format sensor values to write
        writeline = ('%s/%s/%s %s:%s:%s,%s\r\n' %
                     (year,month,day,hour,minute,second,sensor))
        print(writeline)
        
        #Write sensor values
        f = open('finallog.txt','a')
        f.write(writeline)
        f.close()

        
        #Flash an LED here to show it worked
        blue.on()
        upower.lpdelay(20)
        blue.off()