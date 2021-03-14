#import libraries.  Uses upower library to ensure it only does regular sleep if USB connected.
import upower, pyb, time, fusion
from machine import Pin, I2C
from mpu9250 import MPU9250
from fusion import Fusion
imu = MPU9250('Y')
fuse = Fusion()

#Define builtin LED
green = pyb.LED(2)
yellow = pyb.LED(3)
blue = pyb.LED(4)

#Define logging function that can be called at arbitrary interval (seconds)
def log(t):
    """ A function for logging data to file at a regular interval.
    
    The function saves a line of text at each interval representing conductivity, temperature,
    pressure. The device then goes into standby mode for interval t.  After interval t, the
    device awakes as if from a hard reset.  The function is designed to be called from
    main.py.

    Args:
        t: logging interval (seconds)

    Returns:
        Nothing--puts device into standby mode upon completion.
    
    Example:
        To log data at 30 second intervals, save the following two lines as main.py
        
        import logger
        logger.log(30)

    """
    # Calibrate Sensor
    sw = pyb.Switch()
    print("Calibrating. Press switch when done.")
    yellow.on()
    def getmag():                               # Return (x, y, z) tuple (blocking read)
        return imu.mag.xyz
    fuse.calibrate(getmag, sw, lambda : pyb.delay(100))
    print(fuse.magbias)
    yellow.off()
    time.sleep(3)

    nexttime = time.time()+t
    #write header line
    header = 'datetime,heading,pitch,roll,temperature\r\n'
    f = open('finallog.txt','a') 
    f.write(header)
    f.close()

    while True:
        #Wait until it's time to sample by blinking briefly, then sleeping in low power the rest of the second 
        while time.time()<nexttime:
            green.on()
            upower.lpdelay(4)
            green.off()
            upower.lpdelay(996)
            print('Just waiting for the right time.')
        print('It\'s time!')

        #Find next time to take a reading
        nexttime += t

        #Read sensor values
        count = 0
        while count < 300:
            fuse.update(imu.accel.xyz, imu.gyro.xyz, imu.mag.xyz) # Note blocking mag read
            time.sleep_ms(20)
            count += 1
        heading = fuse.heading
        pitch = fuse.pitch
        roll = fuse.roll
        temperature = imu.temperature
        
        #Get time
        [year, month, day, hour, minute, second, weekday, yesterday] = time.localtime()
        
        #Format sensor values to write
        writeline = ('%s/%s/%s %s:%s:%s,%s,%s,%s,%s\r\n' %
                     (year,month,day,hour,minute,second,heading,pitch,roll,temperature))
        print(writeline)
        
        #Write sensor values
        f = open('finallog.txt','a') 
        f.write(writeline)
        f.close()
        
        #Flash an LED here to show it worked
        blue.on()
        upower.lpdelay(20)
        blue.off()