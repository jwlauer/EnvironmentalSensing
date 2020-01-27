#import all required libraries
import machine 
import time  
import onewire, ds18x20
import os
from machine import Pin

#define addresses of each sensor
dat = machine.Pin(12)  
ds = ds18x20.DS18X20(onewire.OneWire(dat))
roms = ds.scan()
print('found devices:', roms)

#format write string for header
text_to_write = 'time'
for i in range(len(roms)):
	text_to_write = text_to_write + (',temperature%s' % i)
text_to_write = text_to_write + ('\r\n')
print(text_to_write)

#Write the header line
#remove next line to erase the file each time you start
'f=open('datalog.txt','w')  #opening as write clears all data
f=open('datalog.txt','a')  #opening as append does not clear data
f.write(text_to_write)
f.close()

#loop through the program a set number of times
for i in range(120):     #program to repeat for an hour
	ds.convert_temp()
	time.sleep_ms(750)   #wait long enough for sensors to respond
	time_in_run = time.time()
	
	#format the write string for data line
	text_to_write = ('%s' % time_in_run)
	for rom in roms:
		temperature = ds.read_temp(rom)
		text_to_write = text_to_write + (',%s' % temperature) # the end=’ ‘ part provides separate readings 
	text_to_write = text_to_write+('\r\n') # this is necessary to start a new line next time around
	print(text_to_write)
	
	#write to file
	f=open('datalog.txt','a')
	f.write(text_to_write)
	f.close()
	
	#pause until next reading is made
	time.sleep(9.25)   #wait desired time
