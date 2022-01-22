import machine
import bme280
import os
i2c = machine.I2C(1,scl=machine.Pin(4), sda=machine.Pin(3)) #on Adafruit ESP32-S2 Feather
i2c.scan()
bme1 = bme280.BME280(i2c=i2c, address = 119) #sdo to 3.3V
data = bme1.raw_values
print(f'pressure = {data[1]} hPa, temperature = {data[0]}°C')

