import ec_logger_deepsleep
import time
from machine import Pin

led = Pin(13, Pin.OUT)
led.value(1)
time.sleep(5)
ec_logger_deepsleep.log(900)