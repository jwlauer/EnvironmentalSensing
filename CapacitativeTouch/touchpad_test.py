from machine import TouchPad, Pin
import utime

while True:
    t = TouchPad(Pin(32))
    touches = []
    lower_index = 3
    upper_index = 9
    for i in range(12):
        utime.sleep(0.01)
        touches.append(t.read())
    touch = sum(touches[3:9])/6
    print(touches)
    print('touch = ', touch)
    utime.sleep(1)
