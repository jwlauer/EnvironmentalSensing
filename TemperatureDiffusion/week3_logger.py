#import all required libraries
import machine 
import time  
import onewire, ds18x20
import os
from machine import Pin

#define addresses of each sensor
dat = machine.Pin(3)  #SDA on Adafruit Feather ESP32-S2
ds = ds18x20.DS18X20(onewire.OneWire(dat))
roms = ds.scan()
print('found devices:', roms)

#format time
t = time.localtime()
started = f'starting at {t[0]}-{t[1]}-{t[2]} {t[3]}:{t[4]}:{t[5]} \r\n'

#format write string for header
text_to_write = started
text_to_write = text_to_write + 'time'
for i in range(len(roms)):
    text_to_write = text_to_write + f',temperature{i}'
text_to_write = text_to_write + ('\r\n')
print(text_to_write)

#Write the header line
#uncomment next line to erase the file each time you start
#f=open('datalog.txt','w')  #opening as write clears all data
f=open('datalog.txt','a')  #opening as append does not clear data
f.write(text_to_write)
f.close()

#set up timing
dt = 20
initial_time = time.time()
next_time = initial_time

while True:    
    if time.time()>=next_time:
        next_time = next_time + dt
        time_in_run = time.time() - initial_time
        
        ds.convert_temp()
        time.sleep_ms(750)   #wait long enough for sensors to respond
        
        #format the write string for data line
        text_to_write = (f'{time_in_run}')
        for rom in roms:
            temperature = ds.read_temp(rom)
            text_to_write = text_to_write + (f',{temperature}') 
        text_to_write = text_to_write+('\r\n') # this is necessary to start a new line next time around
        print(text_to_write)
        
        #write to file
        f=open('datalog.txt','a')
        f.write(text_to_write)
        f.close()
    else:
        time.sleep(0.1)

