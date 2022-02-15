"""Logs a number to a Google Sheet.
Wes Lauer
February 14, 2022
Released under MIT license

This program uses an ESP32-S2 to post data to an
online google sheet using the post_to_google_sheet function.
It requires the file prequests.py

Be sure to set the correct SSID, password, and apikey.
"""

import machine, utime, esp, esp32, usocket, network, uos
#import urequests
import post_to_google_sheet
from machine import Pin

#declare global login variables
ssid = "ENSC2400"
password = "EnvironmentalSensors"

gKey = "AKfycbwMbVHSL_YUBlRPC7mi6XRPhxW6PtKac1S-39dt5xH3UQk5PZ-zcYtnejPC-uz0wzwB"
gSheetKey = "1UmmLPVldYR80taqco8byFmBWe1NnQoFUOR9lttbJS7s"

#connect to wlan
#try:
#    sta_if = network.WLAN(network.STA_IF) #define object to access station mode functions
#    sta_if.active(True) #make station mode active
#    sta_if.connect(ssid, password)
#    print('connected')
#except:
#    print('not connected')
#    pass
    
#utime.sleep(3)
      
data = {}
data['Count'] = 4

#Send data to Google Sheet
result = post_to_google_sheet.send_to_sheet(ssid, password, gKey, gSheetKey, data)
print(result)






