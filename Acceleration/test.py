import machine, pyb, mpu9250
from machine import I2C, Pin
from pyb import Accel
from mpu9250 import MPU9250

i2c = I2C('Y')
i2c = I2C(scl = 'Y9', sda = 'Y10')
