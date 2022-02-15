import machine, utime,  network, prequests

gSheetKey = "1UmmLPVldYR80taqco8byFmBWe1NnQoFUOR9lttbJS7s"
gKey = "AKfycbx8Che9DZwgA8SUrGgFiBCUkFB9zn9jZnlXEY2B4H5Hif5ND2DUdMYQpc-DJqqC8LOF"
url = "https://script.google.com/macros/s/"+gKey+"/exec"

data = {}
data["Field1"] = 4
data["Field2"] = "whatever"
data["Field3"] = "you"
data["Field4"] = "want"
data["Sheet_id"] = gSheetKey

ssid = "Enter SSID here"
password = "Enter Password Here"
try:
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True) 
    sta_if.connect(ssid, password)
    print("connected")
except:
    print("not connected")  

for n in range(4):
    try:
        request = prequests.post(url, json = data)
        utime.sleep(1)
        outcome = ("Posted with reason: ",request.reason)
        request.close()
        break
    except Exception as e:
        print("error message")
        utime.sleep(1)
        if isinstance(e, OSError):
            try:
                request.close()
            except:
                print("request did not exist when closing")
        outcome = "Post failed"
print(outcome)
