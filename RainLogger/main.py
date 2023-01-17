"""Logs count and time to a Google Sheet
Wes Lauer
February 23, 2022
Released under MIT license

This program uses an ESP32 to to post a timestamp and count to a
Google Sheet. It is intended to run on a Feather ESP32-S2 board
(which has a built-in connection between battery and the on-board
LC709203F batter y  monitor). It was written as a way
of logging the time when the bucket in a tipping bucket rain gage
empties itself. To conserve power, the program
spends most of its time in a deep sleep state and only wakes
when an event occurs, resetting the board. The rst pin should be
connected to ground when a tip occurs.
To make it easy to break out of the program, it waits a little
longer at the end of the program when a tip/reset occurs.  

Be sure to set the correct SSID, password and keys to the Google
App Script and Google Sheet.

"""

import machine, utime, esp, esp32, prequests, usocket, network
from machine import Pin

gKey = "AKfycbx8Che9DZwgA8SUrGgFiBCUkFB9zn9jZnlXEY2B4H5Hif5ND2DUdMYQpc-DJqqC8LOF"
gSheetKey = "1UmmLPVldYR80taqco8byFmBWe1NnQoFUOR9lttbJS7s"
ssid = "Sensors"
password = "ENSC_2400"

startticks = utime.ticks_ms()

#turn on the internal LED to let the user know the device is on.
led = Pin(13, Pin.OUT)
led.value(1)

#define a function to flash the internal LED. This is useful for user interface
def flash_led(n,lagtime):
    for i in range(n):
        led.value(1)
        utime.sleep_ms(lagtime)
        led.value(0)
        utime.sleep_ms(lagtime)

#turn on power pins for RTC
power = Pin(18, Pin.OUT) #Pin A0 on Feather ESP32-S2
power.value(1)

#read the value of the count
try:
    f = open("count.txt")
    total = int(f.read())
#the except clause creates the file if it doesn't exist
except:
    f = open("count.txt", "w")
    total = 0
f.close()

#determine how the machine woke up, and increment count if needed
wake_reason = machine.wake_reason() #not used, but here for illustration
reset_cause = machine.reset_cause()
if reset_cause == 1: #machine.PWRON_RESET:
    print("Woke due to reset, incrementing total")
    total = total + 1
    #then write new count back to the count file
    print("New Total = %s\r\n" % total)
    f = open("count.txt", "w") #this erases the old file
    f.write(str(total)) #only first line of file is used
    f.close()
    print(f"Saved new total after {(utime.ticks_ms()-startticks)/1000:.2f} seconds")
    flash_led(10,50)
elif reset_cause == 2:
    print("Woke from hard reset or machine.reset, so not incrementing total")
elif reset_cause == 5:
    print("Woke from soft reset (as in Thonny Stop), so not incrementing total")
elif reset_cause == 4: #machine.DEEPSLEEP_RESET
    print("Woke from deepsleep, so not incrementing total")
    
#read value of voltage
from machine import I2C, Pin
from LC709203F import BatteryMonitor
i2c = I2C(1,scl=Pin(4), sda=Pin(3), freq=100000)
FuelGauge = BatteryMonitor(bus=i2c)
battery = FuelGauge.getBatteryVoltage()
print(battery)

try:
    import bme280
    bme = bme280.BME280(i2c=i2c, address = 119)
    utime.sleep(.1)
    tempC = bme.raw_values[0]
    tempC = bme.raw_values[0]
except:
    byte_tmsb = i2c.readfrom_mem(0x68,0x11,1)
    byte_tlsb = i2c.readfrom_mem(0x68,0x12,1)
    tempC = list(byte_tmsb)[0]+list(byte_tlsb)[0]/256
print(f"temp = {tempC}")
    
#connect to wlan
sta_if = network.WLAN(network.STA_IF)
if not sta_if.isconnected():
    try:
        sta_if.active(True) #make station mode active
        sta_if.connect(ssid, password)
        utime.sleep(1)
        print("connected")
        flash_led(2,100)
    except:
        print("not connected")
        flash_led(4,200)
        pass
else:
    print("Already connected")
    flash_led(2,50)

#get datetime
try:
    import urtc #needs to be on the board
    #from machine import I2C, Pin
    i2c = I2C(1,scl=Pin(4), sda=Pin(3), freq=100000)
    rtc = urtc.DS3231(i2c)
    datetime = rtc.datetime()
    print("Time set from DS3231")
except:
    try:
        from ntptime import settime
        print("Time set from NTP time to: ", end = "")
        settime()
        utime.sleep_ms(300)
        rtc = machine.RTC()
        #can also set time manually using rtc.datetime(year, month, day, weekday, hour, minute, second, millisecond)
    except:
        print("could not set time from NTP server, reverting to machine RTC for time")
        rtc = machine.RTC()
    datetime = rtc.datetime()

#save string to log file
write_string = "%s/%s/%s," % (datetime[0], datetime[1], datetime[2])
write_string += "%s:%s:%s," % (datetime[4], datetime[5], datetime[6])
write_string += "%s,%s,%s,%s\r\n" % (total, battery, reset_cause, tempC)
f = open("rainlog.txt", "a")
f.write(write_string)
f.close()

flash_led(5,150)

#format data for posting online
data = {}
data["Field1"] = total
data["Field2"] = battery
data["Field3"] = reset_cause
data["Field4"] = tempC
data["Sheet_id"] = gSheetKey
url = "https://script.google.com/macros/s/"+gKey+"/exec"

for n in range(4):
    try:
        flash_led(3,75)
        request = prequests.post(url, json = data)
        utime.sleep(1)
        flash_led(5,75)
        outcome = 'Posted OK'
        request.close()
        break
    except Exception as e:
        print('error message')
        flash_led(2,75)
        utime.sleep(1)
        if isinstance(e, OSError):
            try:
                request.close()
            except:
                print("request did not exist when closing")
        outcome = "Post failed"
print(outcome)

#turn off wifi to lower power when in sleep mode
sta_if.active(0)
power.value(0)

#Flash/wait to let user break out of loop
if reset_cause == 1:
    flash_led(40,50)
else:
    flash_led(4,50)
    
timeon = (utime.ticks_ms() - startticks)/1000
print("Going to sleep after being awake for " + str(timeon) + " s")
utime.sleep(0.25)
machine.deepsleep(1000*5*60) 