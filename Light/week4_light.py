import machine, time, os
from machine import I2C, Pin

#setup temperature probe
import onewire, ds18x20
dat = machine.Pin(12)

ds = ds18x20.DS18X20(onewire.OneWire(dat))
roms = ds.scan()
rom = roms[0] #this assumes just a single temperature sensor
print('found onewire device:', roms)

def read_ds18b20():
    ds.convert_temp()
    time.sleep_ms(750)
    temperature = ds.read_temp(rom)    
    return temperature

#Sample from Analog to Digital Converter (ADS1115 ADC Module)
#note that this can also be done on the ESP8266 on-board 10-bit ADC, but Vmax = 1 V
#and there is only one channel.
import ads1x15    #uses version from https://github.com/robert-hh/ads1x15
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)  #SCL is D1, SDA is D2 on WEMOS D1 mini
print('found i2c device:', i2c.scan())
ads = ads1x15.ADS1115(i2c)
def read_ADC():
    ads.gain=1 #Vmax = 4.096 V
    counts0 = ads.read(0,0)   
    V0 = counts0*4.096/65535    
    counts1 = ads.read(0,1)
    V1 = counts1*4.096/65535        
    #gain can be changed as follows, providing more counts per volt
    ads.gain=5 #Vmax = 0.256 V see http://micropython-ads1015.readthedocs.io/en/latest/ads1x15.html
    #this is the format for a differential measurement.  It takes the voltage difference of pins 2 and 3
    counts2 = ads.read(0,2,3)      
    V2 = counts2*0.256/65535    
    return [counts0, counts1, counts2, V0,V1,V2]
  
def log():
    #prepare file  
    f=open('datalog.txt','a')
    #you can open as write using 'w' instead of 'a' if you want to clear the file  
    #write header line
    f.write('temperature,count0,v0,count1,v1,count2,v2,P2\r\n')  
    f.close()  

    while True:  
        #get readings  
        [c0, c1, c2, v0, v1, v2] = read_ADC()
        P2 = v2 / 0.0002  #power density, in watts per square meter, from datasheet for pyranometer  
        try:    #use a try/except statement so that program works even if DS18B20 isn't working     
            temp = read_ds18b20()  
        except:      
            print('temperature measurement did not work')
            temp = -999
            pass
   
        #format/print to screen. %.#f specifies decimal places, %s outputs all data as string
        PrintString = 'temp = %.3f C, count0 = %s, V0 = %.4f V,' % (temp, c0, v0)  

        #the += statement appends a second text string to the first text string
        PrintString +=  'count1 = %s, V1 = %.4f V,' % (c1, v1)  

        PrintString += 'count2 = %s, V2 = %.3f mV, P = %.3f W/m2' % (c2, v2*1000, P2)  
        print(PrintString)  
     
        #format and send output to file  
        WriteString = '%s,%s,%s,%s,%s,%s,%s,%s\r\n' % (temp, c0, v0, c1, v1, c2, v2, P2)  

        f=open('datalog.txt','a')  
        f.write(WriteString)  
        f.close()  
    
        time.sleep(0.5)   #wait 0.5 seconds between readings

log()




