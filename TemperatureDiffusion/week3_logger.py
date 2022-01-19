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
#started = f'starting at {t[0]}-{t[1]}-{t[2]} {t[3]}:{t[4]}:{t[5]} \r\n'
started = f'starting at {t[0]}-{t[1]}-{t[2]} {t[3]}:{t[4]}:{t[5]}'

#format write string for header
text = started + ('\r\n')
text = text + 'time'
for i in range(len(roms)):
    text = text + f',temperature{i}'
print(text)
text_to_write = text + ('\r\n')

#Write the header line
#uncomment next line to erase the file each time you start
#f=open('datalog.txt','w')  #opening as write clears all data
f=open('datalog.txt','a')  #opening as append does not clear data
f.write(text_to_write)
f.close()

#set up timing
dt = 3
initial_time = time.time()
next_time = initial_time

while True:    
    if time.time()>=next_time:
        next_time = next_time + dt
        time_in_run = time.time() - initial_time
        
        ds.convert_temp()
        time.sleep_ms(750)   #wait long enough for sensors to respond
        
        #format the write string for data line
        text = (f'{time_in_run/60}')
        for rom in roms:
            temperature = ds.read_temp(rom)
            text = text + (f',{temperature:.1f}') 
        print(text)
        text_to_write = text+('\r\n')
        
        #write to file
        f=open('datalog.txt','a')
        f.write(text_to_write)
        f.close()
    else:
        time.sleep(0.1)
