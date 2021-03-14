import time
import machine
import bme280
#import utime
import usocket
import network

#declare global login variables
apiKey = "8O6ZNBR4UVFCLVQX" #key for Thingspeak test page 
#ssid = "EnvironmentalSensors"  #For testing
#ssid = "Karenmarie" #For use at SCC
ssid = "Anduin"
password = "Johnny_1002"
#password = "ENSC2400" #For testing
#password = "Guy33333" #For use at SCC

def http_get(url):   #Sets up http get statement--directly from micropython documentation
    _, _, host, path = url.split('/', 3)
    addr = usocket.getaddrinfo(host, 80)[0][-1]
    s = usocket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    while True:
        data = s.recv(100)
        if data:
            print(str(data, 'utf8'), end='')
        else:
            break
    s.close()

i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))
#for i2c to work on a BMP280 or BME280, CSB nees to be wired to 3.3v
bme1 = bme280.BME280(i2c=i2c, address = 118) #sdo grounded
bme2 = bme280.BME280(i2c=i2c, address = 119) #sdo to 3.3v

#time.sleep(2.0) # Delay at startup

#Opens a file to append. Creates if necessary. If uses flag 'w' instead of 'a', erases file at start.
f = open('data.txt', 'a')
f.close()

counter = 0

#while True:
    ###################################################################
    # Loop code goes inside the while statement, this is called repeatedly: #
    ###################################################################

# read median of 10 values from each sensor
readings1 = [bme1.raw_values for i in range(0, 9)] #loop from i = 1 to i = 9
temperature1 = [readings1[i][0] for i in range(0,9)]
pressure1 = [readings1[i][1] for i in range(0,9)]
humidity1 = [readings1[i][2] for i in range(0,9)]
data1 = (sorted(temperature1)[4], sorted(pressure1)[4], sorted(humidity1)[4])

readings2 = [bme2.raw_values for i in range(0, 9)] #loop from i = 1 to i = 9
temperature2 = [readings2[i][0] for i in range(0,9)]
pressure2 = [readings2[i][1] for i in range(0,9)]
humidity2 = [readings2[i][2] for i in range(0,9)]
data2 = (sorted(temperature2)[4], sorted(pressure2)[4], sorted(humidity2)[4])

#use this to only read a single value
#data1 = bme1.raw_values
#data2 = bme2.raw_values

#connect to wlan
sta_if = network.WLAN(network.STA_IF) #define object to access station mode functions
sta_if.active(True) #make station mode active
sta_if.connect(ssid, password)

#set the internal real time clock from NTP server, which requires connection to router
try:
    from ntptime import settime
    settime()
    #can also set time manually using rtc.datetime(year, month, day, weekday, hour, minute, second, millisecond)
except:
    print("could not set time from NTP server, reverting to RTC for time")
rtc = machine.RTC()
datetime = rtc.datetime()

# send output to terminal so that user knows it's working
print(data1)
print(data2)

# save to logging file
f = open('data.txt', 'a')
f.write('%s/%s/%s %s:%s,' % (datetime[0], datetime[1], datetime[2], datetime[4], datetime[5]))
f.write('%s,%s,%s,' % data1)
f.write('%s,%s,%s\r\n' % data2)  # \r\n indicates a newline character in Windows OS.  Use \n for other OS.
f.close()

url = 'https://api.thingspeak.com/update?api_key=%s&field1=%s&field2=%s&field3=%s&field4=%s' % (apiKey, data1[0], data1[1], data2[0], data2[1])
print(url)
http_get(url)

    # delay for one minute
 #   time.sleep(600.0)
    
 #   import machine

# configure RTC.ALARM0 to be able to wake the device--pin GPIO16 (D0) to RST
rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

# set RTC.ALARM0 to fire after 600 seconds (waking the device)
rtc.alarm(rtc.ALARM0, 600000)

# put the device to sleep
machine.deepsleep()


