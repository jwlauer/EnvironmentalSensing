""" Micropython Library for reading Measurement Specialties (MS) I2C pressure sensors.

Code modified from code originally developed for raspberry pi at the `control
everything community <https://github.com/ControlEverythingCommunity/MS5803-05BA/blob/master/Python/MS5803_05BA.py>`_.
Uses the maximum oversamping ratio of 4096.

Example
-------
>>> from machine import I2C, Pin
>>> import ms_pressure
>>> i2c = I2C(0, scl=Pin(4), sda=Pin(3), freq = 100000)
>>> VDD_pin = Pin(0, Pin.OUT_PP)
>>> ground_pin = Pin(2, Pin.OUT_PP)
>>> [pres, ctemp] = pressure.ms5840_02(i2c, VDD_pin, ground_pin)

"""

import time

def read_uncompensated(i2c,address,VDD_pin,ground_pin):
    #turn on power and turn off ground if necessary
    if not(VDD_pin is None):
        VDD_pin.value(1)
        
    if not(ground_pin is None):
        ground_pin.value(0)
            
    reset_command = bytearray([0x1E])
    i2c.writeto(0x76, reset_command)
    time.sleep(0.1)

    # Read 12 bytes of calibration data
    # Read pressure sensitivity
    data = bytearray(2)
    data = i2c.readfrom_mem(0x76, 0xA2, 2)
    C1 = data[0] * 256 + data[1]

    # Read pressure offset
    data = i2c.readfrom_mem(0x76, 0xA4, 2)
    C2 = data[0] * 256 + data[1]

    # Read temperature coefficient of pressure sensitivity
    data = i2c.readfrom_mem(0x76, 0xA6, 2)
    C3 = data[0] * 256 + data[1]

    # Read temperature coefficient of pressure offset
    data = i2c.readfrom_mem(0x76, 0xA8, 2)
    C4 = data[0] * 256 + data[1]

    # Read reference temperature
    data = i2c.readfrom_mem(0x76, 0xAA, 2)
    C5 = data[0] * 256 + data[1]

    # Read temperature coefficient of the temperature
    data = i2c.readfrom_mem(0x76, 0xAC, 2)
    C6 = data[0] * 256 + data[1]

    pressure_command = bytearray([0x48])
    i2c.writeto(0x76, pressure_command)
    time.sleep(0.1)

    # Read digital pressure value
    # Read data back from 0x00(0), 3 bytes
    # D1 MSB2, D1 MSB1, D1 LSB
    value = bytearray(3)
    value = i2c.readfrom_mem(0x76, 0x00, 3)
    D1 = value[0] * 65536 + value[1] * 256 + value[2]

    #0x50(64)    Temperature conversion(OSR = 256) command
    temperature_command = bytearray([0x58])
    i2c.writeto(0x76, temperature_command)
    time.sleep(0.1)

    # Read digital temperature value
    # Read data back from 0x00(0), 3 bytes
    # D2 MSB2, D2 MSB1, D2 LSB

    value = i2c.readfrom_mem(0x76, 0x00, 3)
    D2 = value[0] * 65536 + value[1] * 256 + value[2]

    return[C1,C2,C3,C4,C5,C6,D1,D2]

def ms5803_02(i2c, address = 0x76, VDD_pin=None, ground_pin=None):
    """ Reads pressure and temperature from an MS5803_02 sensor.
    
    Parameters
    ----------
	i2c : :obj:'machine.I2C'
		An I2C bus object
	address : int, optional
        I2C address of the sensor, 118 or 119.  Default is 118 (0x76).
	VDD_pin : :obj:'machine.PIN', optional
		Pin object representing the pin used to power the device 
	ground_pin : :obj:'machine.PIN', optional
		Pin object representing the pin used to ground the device
    Returns
    -------
    pressure : float
        Pressure in hPa.
    temperature : float
        Temperature in degrees C.
           
    """
    
    [C1,C2,C3,C4,C5,C6,D1,D2] = read_uncompensated(i2c, address, VDD_pin, ground_pin)

    dT = D2 - C5 * 2**8
    TEMP = 2000 + dT * C6 / 2**23
    OFF = C2 * 2**17 + (C4 * dT) / 2**6
    SENS = C1 * 2**16 + (C3 * dT ) / 2**7
    
    if TEMP > 2000 :
        T2 = 0
        OFF2 = 0
        SENS2 = 0
    elif TEMP < 2000 :
        T2 = (dT * dT) / 2**31
        OFF2 = 61 * ((TEMP - 2000) * (TEMP - 2000)) / 2**4
        SENS2 = 2 * ((TEMP - 2000) * (TEMP - 2000)) 
        if TEMP < -1500 :
            OFF2 = OFF2 + 20 * (TEMP + 1500) * (TEMP + 1500)
            SENS2 = SENS2 + 12 * ((TEMP + 1500) * (TEMP +1500))

    TEMP = TEMP - T2
    OFF = OFF - OFF2
    SENS = SENS - SENS2
    pressure = ((((D1 * SENS) / 2**21) - OFF) / 2**15) / 100.0
    cTemp = TEMP / 100.0
    
    if not(VDD_pin is None):
        VDD_pin.value(0)
        
    return([cTemp, pressure])

def ms5803_05(i2c, address = 0x76, VDD_pin=None, ground_pin=None):
    """ Reads pressure and temperature from an MS5803_05 sensor.
    
    Parameters
    ----------
	i2c : :obj:'machine.I2C'
		An I2C bus object
	address : int, optional
        I2C address of the sensor, 118 or 119.  Default is 118 (0x76).
	VDD_pin : :obj:'machine.PIN', optional
		Pin object representing the pin used to power the device 
	ground_pin : :obj:'machine.PIN', optional
		Pin object representing the pin used to ground the device
    Returns
    -------
    pressure : float
        Pressure in hPa.
    temperature : float
        Temperature in degrees C.
           
    """
    
    [C1,C2,C3,C4,C5,C6,D1,D2] = read_uncompensated(i2c, address, VDD_pin, ground_pin)

    dT = D2 - C5 * 2**8
    TEMP = 2000 + dT * C6 / 2**23
    OFF = C2 * 2**18 + (C4 * dT) / 2**5
    SENS = C1 * 2**17 + (C3 * dT ) / 2**7

    if TEMP > 2000 :
        T2 = 0
        OFF2 = 0
        SENS2 = 0
    elif TEMP < 2000 :
        T2 = 3 * (dT * dT) / 2**33
        OFF2 = 3 * ((TEMP - 2000) * (TEMP - 2000)) / 2**3
        SENS2 = 7 * ((TEMP - 2000) * (TEMP - 2000)) / 2**3
        if TEMP < -1500 :
            SENS2 = SENS2 + 3 * ((TEMP + 1500) * (TEMP +1500))

    TEMP = TEMP - T2
    OFF = OFF - OFF2
    SENS = SENS - SENS2
    pressure = ((((D1 * SENS) / 2**21) - OFF) / 2**15) / 100.0
    cTemp = TEMP / 100.0
    
    if not(VDD_pin is None):
        VDD_pin.value(0)
        
    return([cTemp, pressure])

def ms5840_02(i2c, VDD_pin=None, ground_pin=None):
    """ Reads pressure and temperature from an MS5840_02 sensor.
    
    Parameters
    ----------
	i2c : :obj:'machine.I2C'
		An I2C bus object
	VDD_pin : :obj:'machine.PIN', optional
		Pin object representing the pin used to power the device 
	ground_pin : :obj:'machine.PIN', optional
		Pin object representing the pin used to ground the device
    Returns
    -------
    pressure : float
        Pressure in hPa.
    temperature : float
        Temperature in degrees C.

    """
    #import time
    address = 0x76
    [C1,C2,C3,C4,C5,C6,D1,D2] = read_uncompensated(i2c,address,VDD_pin,ground_pin)

    dT = D2 - C5 * 2**8
    TEMP = 2000 + dT * C6 / 2**23 
    OFF = C2 * 2**17 + (C4 * dT) / 2**6  #MS5840
    SENS = C1 * 2**16 + (C3 * dT ) / 2**7 #MS5840

    #T2 = 0
    #OFF2 = 0
    #SENS2 = 0

    if TEMP > 2000 :
        Ti = 0
        OFFi = 0
        SENSi = 0
    elif TEMP > 1000 :
        Ti = 12 * (dT * dT) / 2**35
        OFFi = 30 * ((TEMP - 2000) * (TEMP - 2000)) / 2**8
        SENSi = 0
    else:
        Ti = 14 * (dT * dT) / 2**35
        OFFi = 35 * ((TEMP - 2000) * (TEMP - 2000)) / 2**3
        SENSi = 63 * ((TEMP - 2000) * (TEMP - 2000)) / 2**5      
    TEMP2 = (TEMP-Ti)/100
    OFF2 = OFF - OFFi
    SENS2 = SENS - SENSi
    P2 = ((D1 * SENS2 / 2**21 - OFF2) / 2**15 ) / 100

    pressure = P2
    cTemp = TEMP2

    if not(VDD_pin is None):
        VDD_pin.value(0)
        
    return([cTemp, pressure])

def ms5839_02(i2c, VDD_pin=None, ground_pin=None):
    """ Reads pressure and temperature from an MS5839_02 sensor (same as MS5840_02).
    
    Parameters
    ----------
	i2c : :obj:'machine.I2C'
		An I2C bus object
	VDD_pin : :obj:'machine.PIN', optional
		Pin object representing the pin used to power the device 
	ground_pin : :obj:'machine.PIN', optional
		Pin object representing the pin used to ground the device
    Returns
    -------
    pressure : float
        Pressure in hPa.
    temperature : float
        Temperature in degrees C.

    """
    return ms5840_02(i2c,VDD_pin = None, ground_pin = None)
    
