from machine import I2C, Pin
import bme280, ms_pressure
i2c = I2C(1, scl=Pin(4), sda=Pin(3))
i2c.scan()
bme=bme280.BME280(i2c=i2c, address=119)
bmedata=bme.raw_values
print(f"BMP Temperature = {bmedata[0]} C, BMP Pressure = {bmedata[1]} hPa")
msdata = ms_pressure.ms5839_02(i2c)
print(f"MS Temperature = {msdata[0]} C, MS Pressure = {msdata[1]} hPa")
depth = (msdata[1]-bmedata[1])/97.9
print(f"Depth = {depth} m")