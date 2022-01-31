#setup_device.py
#designed to simplify setting time on DS3231 RTC modules
#The module should be connected to the standard i2c pins on the ESP32

import machine
import utime
import usocket
import network
import urtc

ssid = input('Please enter the SSID for your network: ')
password = input('Please enter the password for your network: ')

#connect to wlan
sta_if = network.WLAN(network.STA_IF) 
sta_if.active(True) #make station mode active
sta_if.connect(ssid, password)
utime.sleep(2)

try:
    from ntptime import settime
    settime()
    utime.sleep(0.3)
    #can also set time manually 
    #use rtc.datetime(year, month, day, weekday, hour, minute, second, millisecond)
except:
    print("could not set time from NTP server, reverting to RTC for time")

import urtc
i2c = machine.I2C(scl=machine.Pin(14), sda=machine.Pin(27)) 
rtc = urtc.DS3231(i2c)
(year, month, day, hour, minute, second, weekday, yearday) = utime.localtime()
#rtc is set using a different tuple format:
tuple_for_set = (year, month, day, weekday, hour, minute, second,0)
rtc.datetime(tuple_for_set)

print('DS3231 time set to: ')
print(rtc.datetime())

