"""Logs pressure/temperature/depth to a Google Sheet.
Wes Lauer
October 29, 2021
Released under MIT license

This program uses an ESP32 (Lolin D32 Pro) to read data from the 
built-in capacitative touch sensor and the build-in 
internal temperature sensor. Provisions are also made for reading
timestamps from a DS3231 RTC or an NTP server.  Data is posted
to an online google sheet if the device is online. The device
is then placed in deep sleep. This script is intended to
be called directly from main.py.

Be sure to set the correct SSID, password, and apikey in credentials.py.
"""

import machine, utime, esp, esp32, urequests, usocket, network, uos
#import post_to_google_sheet
from machine import TouchPad, Pin
#from credentials import credentials

#pad_gpios = [0,2,12,13,14,27,33]
pad_gpios = [0,2,12]

t = TouchPad(Pin(32))
touch_pads = []
for gpio in pad_gpios:
    touch_pads.append(TouchPad(Pin(gpio)))

def normal_reading(touch_pads,t):
    readings = []
    for pad in touch_pads:
        readings.append(pad.read())
    average = sum(readings) / len(readings)
    raw_reading = t.read()
    normal_reading = raw_reading/average
    return (normal_reading, raw_reading)

def log(sleeptime, wifi=False, sd=False):
    import machine, utime #esp, esp32, #urequests, usocket, network, uos
    from machine import Pin

    next_time = utime.time() + sleeptime

    #Read touch data before turning on wifi

    #   t = TouchPad(Pin(32))
    touches = []
    raws = []
    lower_index = 3
    upper_index = 9
    utime.sleep(3)
    for i in range(12):    
        (normal,raw) = normal_reading(touch_pads, t)
        touches.append(normal)
        raws.append(raw)
    touch = sum(touches[3:9])/6
    raw_touch = sum(raws[3:9])/6
    print('touch = ', touch, ' raw_touch = ', raw_touch)
        
    led = Pin(5, Pin.OUT)
    led.value(0)

    def flash(n,t):
        for i in range(n):
            led.value(1)
            utime.sleep(t)
            led.value(0)
            utime.sleep(t)

    esp.osdebug(None)
    startticks = utime.ticks_ms()

    wake_reason = machine.wake_reason()
    reset_cause = machine.reset_cause()
    print('wake reason = '+ str(wake_reason))
    print('reset cause = '+ str(reset_cause))

    #mount SD card on Lolin D32 Pro.  If it doesn't work, sleep 20 seconds so user can break out.
    try:
        if sd:
            uos.mount(machine.SDCard(slot=2,width=1, sck=18, mosi=23, miso=19, cs=4), "/sd")
        else:
            pass
    except:
        pass

    #write header file if did not wake from deep sleep
    if machine.reset_cause() != machine.DEEPSLEEP_RESET:
        outputtxt = 'date,time,touch,raw_touch,temperature,battery(V)\r\n'
        try:
            uos.chdir('sd')
            f = open('datalog.txt','a')
            f.write(outputtxt)
            f.close()
            uos.chdir('/')
        except:
            #flash LED if fails to write and write to flash memory
            f = open('datalog.txt','a')
            f.write(outputtxt)
            f.close()
            flash(10,0.1)
        print('Wrote header line')

    #turn on power pins for RTC
    #power = Pin(2, Pin.OUT)
    #power.value(1)

    #read value of time from DS3231 RTC if it is connected. If not, set time from
    #web (NTP time) and if that doesn't work, just revert to system real time clock.
    try:
        import urtc #needs to be on the board
        #from machine import I2C, Pin
        rtc = urtc.DS3231(i2c)
        datetime = rtc.datetime()
        print('Time set from DS3231')
    except:
        try:
            from ntptime import settime
            print('Time set from NTP time to: ', end = '')
            settime()
            utime.sleep_ms(500)
            rtc = machine.RTC()
            #can also set time manually using rtc.datetime(year, month, day, weekday, hour, minute, second, millisecond)
        except:
            print("Reverting to machine RTC for time")
            rtc = machine.RTC()
        datetime = rtc.datetime()
    print('Datetime in machine.rtc format = ', end = '')
    print(datetime)

    #read value of voltage using built-in 100k 100k voltage divider on pin 35 for Lolin D32 Pro
    from machine import ADC
    adc = ADC(Pin(35))
    adc.atten(ADC.ATTN_11DB)  #Voltage range 0 (0) V to 3.6 V (4095)
    adc_count = adc.read()
    battery = adc_count / 4095 * 3.6 * 2  #factor of two because of voltage divider
    print('battery = ',battery)

    #read internal temperature
    temperature = esp32.raw_temperature()
    print('temperature = ', temperature) 
    
    #format output string
    outputtxt = ('%s/%s/%s,%s:%s:%s,' % (datetime[0], datetime[1], datetime[2], datetime[4], datetime[5], datetime[6]))
    outputtxt += ('%s,%s,%s,%s\r\n' % (touch,raw_touch,temperature,battery))
    print(outputtxt)

    #then write final data to the SD
    try:
        uos.chdir('sd')
        f = open('datalog.txt', 'a') 
        f.write(outputtxt) 
        f.close()
        uos.chdir('/')
    except:
        #flash LED if fails to write and write to flash memory
        f = open('datalog.txt','a')
        f.write(outputtxt)
        f.close()
        flash(10,0.05)

    flash(5,0.25)

    p1 = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
    #esp32.wake_on_ext0(p1, level = 0)
    #set machine to wake if p1 (so pin 15) is pulled low
    #the internal pull-up resistor may not work, so may require
    #an external pull-up resistor of perhaps 100K.
    esp32.wake_on_ext1([p1], level = 0)

    timeon = (utime.ticks_ms() - startticks)/1000
    print('Going to sleep after being awake for ' + str(timeon) + ' s')
    while (utime.time() < next_time):
        led.value(0)
        utime.sleep(0.05)
        led.value(1)
        #machine.lightsleep(1000*sleeptime)
        machine.lightsleep(1000)
    #machine.deepsleep(1000*sleeptime) #sleeps sleeptime minutes
    machine.deepsleep(1000*sleeptime) #sleeps sleeptime minutes




