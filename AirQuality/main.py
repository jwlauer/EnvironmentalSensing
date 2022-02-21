"""Example Code for Honeywell HPMA1115S0-XXX particulate sensor
Wes Lauer
January 8, 2022
Released under MIT license

This program uses a serial UART connect to read data from a
Honeywell HPMA1115S0 PM2.5/PM10 sensor.
"""
import machine
from machine import Pin
import time    #for pausing and looping

ser = machine.UART(1,baudrate=9600, rx=38, tx=39)  #RX & TX for Adafruit ESP32-S2 Feather-S2
BuiltinLED = Pin(13, Pin.OUT)
BuiltinLED.on()

#see if communication is working
ser.readline()
time.sleep(1)
result = ser.readline()  #this should show a line of response, which the device outputs every second
time.sleep(1)  #wait a second for a line to come in
ser.readline()  #this should show a single line of response, since the previous serial.readline cleared all the data

#stop auto send function--this makes learning UART less confusing because results don't keep stacking up in the queue
code = b'\x68\x01\x20\x77'
ser.readline()
ser.write(code)
time.sleep(1)
response = ser.readline()
print('command sent, acknowledgement is:')
print(response)

#turn reading off -- confirm that this stopped fan
stopcode= b'\x68\x01\x02\x95'
ser.readline()
ser.write(stopcode)
time.sleep(0.5)
response = ser.readline()
print('command sent, acknowledgement is:')
print(response)

#turn reading on -- confirm that this started fan
startcode = b'\x68\x01\x01\x96'
ser.readline()
ser.write(startcode)
time.sleep(0.5)
response = ser.readline()
print('acknowledgement is:')
print(response)

#read particle measuring results -- 68 01 04 93
readcode = b'\x68\x01\x04\x93'
ser.readline()
ser.write(readcode)
time.sleep(1)
response = ser.readline()
print('started, acknowledgement is:')
PM25 = response[3]*256+response[4]
print('PM2.5 = ');
print(PM25)
PM10 = response[5]*256+response[6]

#main loop
while True:
    written = ser.write(readcode) #assign the result to a variable so it won't print to screen
    time.sleep(6)  #data sheet says response time is under 6 seconds
    response = ser.readline()
    if response[0] == 64 and len(response)==8:
        PM25 = response[3]*256+response[4]
        PM10 = response[5]*256+response[6]
        print('PM2.5 = %s; PM10 = %s' % (PM25, PM10))
        if PM25>100:
            print('ALARM!!! ALARM!!! ALARM !!!')
            BuiltinLED.value(0)
        else:
            BuiltinLED.value(1)
    else:
        time.sleep(10)
        response = ser.readline()