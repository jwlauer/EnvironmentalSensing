#simple_set_clock.py
#Illustrates setting clock on DS3231.  If using Thonny, the microcontroller
#clock is set to the system clock, ensuring that the utime.localtime
#is roughly correct.  If that is not the case, hard-code the date and time.
#The module should be connected to the standard i2c pins on the ESP32

import machine
from machine import Pin
import utime
import urtc
i2c = machine.I2C(1,scl=Pin(9), sda=Pin(8)) 
rtc = urtc.DS3231(i2c)

#read values of time from local microcontrollers clock
(year, month, day, hour, minute, second, weekday, yearday) = utime.localtime()

#rtc is set using a different tuple format:
tuple_for_set = (year, month, day, weekday, hour, minute, second,0)
rtc.datetime(tuple_for_set)

print('DS3231 time set to: ')

#Read and format a timestamp:
timetuple = rtc.datetime()
print(timetuple)
timestamp = f'{timetuple[0]}/{timetuple[1]}/{timetuple[2]}'
timestamp += f' {timetuple[4]}:{timetuple[5]}:{timetuple[6]}'
print(f'timestamp = {timestamp}')

