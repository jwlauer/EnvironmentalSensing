import machine, time
from machine import Pin, I2C
i2c = I2C('Y', freq=400000)
i2c.scan()
from mpu9250 import MPU9250
imu = MPU9250('Y')
from fusion import Fusion
fuse = Fusion()
def getmag():                               # Return (x, y, z) tuple (blocking read)
    return imu.mag.xyz
count = 0
while True:
    fuse.update(imu.accel.xyz, imu.gyro.xyz, imu.mag.xyz) # Note blocking mag read
    if count % 50 == 0:
        print("Heading, Pitch, Roll: {:7.3f} {:7.3f} {:7.3f}".format(fuse.heading, fuse.pitch, fuse.roll))
    time.sleep_ms(20)
    count += 1