"""Logs count and time to a Google Sheet using IFTTT.
Wes Lauer
February 21, 2022
Released under MIT license

This program uses an ESP32 to to post a timestamp and count to 
a Google Sheet. It is intended to run on
a Feather ESP32-S2 board (which has a built-in connection between
battery and the on-board LC709203F battery  monitor). It was written as a way
of logging the time when the bucket in a tipping bucket rain gage
empties itself. To conserve power, the program
spends most of its time in a deep sleep state and only wakes
when an event occurs (by grounding pin 12).  To make it easy to 
break out of the program, it does not run when the reset button 
is pressed.  Instead, to run the program, do a soft reset:  

>>> import machine
>>> machine.reset()

To end, do a hard reset by pressing reset button.
Alternatively, the program can be started by holding the tipping
bucket in the position that it makes a connection (and or by connectin 12 to ground),
then pressing the reset button.  If all is well, the program will 
run through the procedure and flash the blue
LED twice when going into deep sleep. The LED will not flash if the 
program does not work.

Be sure to set the correct SSID, password, and apikey.

"""

import machine, utime, esp, esp32, prequests, usocket, network
from machine import Pin
import post_to_google_sheet

#esp.osdebug(None)
startticks = utime.ticks_ms()

#turn on the internal LED to let the user know the device is on.
from machine import Pin
led = Pin(13, Pin.OUT)
led.value(1)
utime.sleep(1)
led.value(0)
utime.sleep(1)
led.value(1)

gKey = "AKfycbwMbVHSL_YUBlRPC7mi6XRPhxW6PtKac1S-39dt5xH3UQk5PZ-zcYtnejPC-uz0wzwB"
gSheetKey = "1UmmLPVldYR80taqco8byFmBWe1NnQoFUOR9lttbJS7s"

ssid = "Anduin"
password = "Johnny_1002"

wake_reason = machine.wake_reason()
reset_cause = machine.reset_cause()
print('wake reason = '+ str(wake_reason))
print('reset cause = '+ str(reset_cause))

#End program if reset was pressed and if bucket is not in a "tripped" state
p1 = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
print('Bucket pin value = ' + str(p1.value()))
if (reset_cause == machine.PWRON_RESET) and (p1.value() == 1):
    print('It was reset after power disconnect and bucket is not engaged.  Breaking out of program.')
    import sys
    sys.exit()

#****************************************************************************
#set an interrupt to increment the count if bucket tips while program running
interruptcounter = 0
ticksOfLastInterrupt = utime.ticks_ms()

#define an interrupt handler to count the number of times that the bucket tips while
#the program is running.  The handler does not count a tip if it occurs within
#less than 0.5 seconds of the previous tip--such a reading would likley be due
#to error in the reed switch, which could connect/break the circuit multiple times
#if tipped slowly.
def handleInterrupt(p1):
    global interruptcounter
    global ticksOfLastInterrupt
    timeElapsed = utime.ticks_diff(utime.ticks_ms(), ticksOfLastInterrupt)
    if timeElapsed > 500:
        interruptcounter = interruptcounter + 1
        ticksOfLastInterrupt = utime.ticks_ms()
        print('Interrupt Triggered')

#set pin 12 to look for tips    
p1.irq(trigger=Pin.IRQ_FALLING, handler=handleInterrupt)
#****************************************************************************   

#Sleep to let user break out of loop
time.sleep(15)

#turn on power pins for RTC
power = Pin(18, Pin.OUT) #Pin A0 on Feather ESP32-S2
power.value(1)

#define a function to flash the internal LED. This is useful for user interface
def flash_led(n):
    for i in range(n):
        led.value(1)
        utime.sleep_ms(50)
        led.value(0)
        utime.sleep_ms(50)

#read the value of the count from SD
try:
    f = open('count.txt')
    total = int(f.read())
#the except clause creates the file if it doesn't exist
except:
    f = open('count.txt', 'w')
    total = 0
f.close()

#connect to wlan
try:
    sta_if = network.WLAN(network.STA_IF) #define object to access station mode functions
    sta_if.active(True) #make station mode active
    sta_if.connect(ssid, password)
    print('connected')
except:
    print('not connected')
    pass
    
utime.sleep(3)
#read value of time from DS3231 RTC if it is connected. If not, set time from
#web (NTP time) and if that doesn't work, just revert to system real time clock.
#os.chdir('/')

#read value of voltage using built-in 100k 100k voltage divider on pin 35 for Lolin D32 Pro
from machine import I2C, Pin
from LC709203F import BatteryMonitor
i2c = I2C(1,scl=Pin(4), sda=Pin(3), freq=100000)
FuelGauge = BatteryMonitor(bus=i2c)
battery = FuelGauge.getBatteryVoltage()

try:
    import urtc #needs to be on the board
    from machine import I2C, Pin
    i2c = I2C(1,scl=Pin(4), sda=Pin(3), freq=100000)
    rtc = urtc.DS3231(i2c)
    datetime = rtc.datetime()
    print('Time set from DS3231')
except:
    try:
        from ntptime import settime
        print('Time set from NTP time to: ', end = '')
        settime()
        utime.sleep_ms(300)
        rtc = machine.RTC()
        #can also set time manually using rtc.datetime(year, month, day, weekday, hour, minute, second, millisecond)
    except:
        print("could not set time from NTP server, reverting to machine RTC for time")
        rtc = machine.RTC()
    datetime = rtc.datetime()
print('Datetime in machine.rtc format = ', end = '')
print(datetime)

#format the data to send


if reset_cause == machine.PWRON_RESET:
    print('Woke due to reset with bucket engaged, so not incrementing total')
elif reset_cause == 5:
    print('Woke from soft reset, so not incrementing total')
elif wake_reason == 4:
    print('Woke due to timer so not incrementing total')
else:
    print('Woke due to tip, so incrementing total')
    total = total + 1

data = {}
data['field2'] = total
data['field3'] = battery
result = post_to_google_sheet.send_to_sheet(ssid, password, gKey, gSheetKey, data)
print(result)

#turn off wifi to lower power when in sleep mode
sta_if.active(0)
power.value(0)

total = total + interruptcounter
if reset_cause == machine.PWRON_RESET:
    print('Woke due to reset with bucket engaged, so not saving')
elif reset_cause == 5:
    print('Woke from soft reset, so not saving')
elif wake_reason == 4:
    print('Woke due to timer so not saving')
else:
    print('Woke due to tip, so saving data')        
    #write date, time, and count to the log file
    f = open('rainlog.txt', 'a')
    f.write('%s/%s/%s,%s:%s:%s,%s,%s\r\n' % (datetime[0], datetime[1], datetime[2], datetime[4], datetime[5], datetime[6], str(total), battery))
    f.close()
 
#then write final count back to the count file
print('New Total = %s\r\n' % total)
f = open('count.txt', 'w') #this erases the old file
f.write(str(total)) #only first line of file is used
f.close()

flash_led(5)

p1 = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
#esp32.wake_on_ext0(p1, level = 0)
esp32.wake_on_ext1([p1], level = 0)

timeon = (utime.ticks_ms() - startticks)/1000
print('Going to sleep after being awake for ' + str(timeon) + ' s')
machine.deepsleep(1000*15) #sleeps 60 minutes





