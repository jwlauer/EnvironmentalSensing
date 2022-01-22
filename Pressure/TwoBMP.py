import machine
import bme280

i2c = machine.I2C(scl=machine.Pin(21), sda=machine.Pin(22)) 
bme1 = bme280.BME280(i2c=i2c, address = 118) #sdo grounded
bme2 = bme280.BME280(i2c=i2c, address = 119) #sdo to 3.3v

def depth():
  [T1,P1,H1] = bme1.raw_values      #T in degrees C, P in hPa
  [T2,P2,H2] = bme2.raw_values
  WaterLevelDifference = (P2-P1)*100/9810 
  return WaterLevelDifference
