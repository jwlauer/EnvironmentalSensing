"""Logs EC data 
Wes Lauer
March 7, 2022
Released under MIT license

This program logs electrical conductivity, temperature, and
pressure to a file.

"""

import machine, time
from machine import Pin, I2C
import ec_function
import ms_pressure
import urtc

#turn on the internal LED to let the user know the device is on.
led = Pin(13, Pin.OUT)
led.value(1)

#Write header
write_string = "datetime,MS_pres,MS_temp,R_av,i_av,Therm_temp\r\n"
f = open("eclog.txt", "a")
f.write(write_string)
f.close()

#define a function to flash the internal LED. This is useful for user interface
def flash_led(n,lagtime):
    for i in range(n):
        led.value(1)
        time.sleep_ms(lagtime)
        led.value(0)
        time.sleep_ms(lagtime)

#turn on power pins for RTC
#power = Pin(18, Pin.OUT) #Pin A0 on Feather ESP32-S2
#power.value(1)
    
def log(logtime):
    #setup i2c bus
    i2c = I2C(1,scl=Pin(4), sda=Pin(3))
    
    while True:
       
        try:
            rtc = urtc.DS3231(i2c)
            datetime = rtc.datetime()
            print("Time set from DS3231")
        except:
            print("could not set time from NTP server, reverting to machine RTC for time")
            rtc = machine.RTC()
            datetime = rtc.datetime()

        #format timestamp
        timestamp = "%s/%s/%s " % (datetime[0], datetime[1], datetime[2])
        timestamp += "%s:%s:%s" % (datetime[4], datetime[5], datetime[6])
    
        #find next log time
        next_time = time.time() + logtime

        #read pressure and temperature
        try:
            [pres, ctemp] = ms_pressure.ms5839_02(i2c)
        except:
            [pres, ctemp] = [-999,-999]
            flash_led(2,500)


        #read pressure and temperature
        try:
            [R_av,i_av,T] = ec_function.read_ec()
        except:
            [R_av,i_av,T] = [-999,-999,-999]
            flash_led(3,500)
        
        #format string to save
        write_string = timestamp
        write_string += ",%.2f,%.2f,%.3f,%.4f,%.2f\r\n" % (pres,ctemp,R_av,i_av,T)
        
        f = open("eclog.txt", "a")
        f.write(write_string)
        f.close()
        flash_led(20,150)

        #turn frequency down to save power, then just wait, flashing LED periodically
        machine.freq(40000000)    
        while time.time() < next_time:
            flash_led(2,150)
            time.sleep(5)
        #turn frequency back up
        machine.freq(240000000)    
