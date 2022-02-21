import requests
#the app script is located here: https://script.google.com/home/projects/1VkOI6Ij-d32U2MzyNgA3A6d8H6ruKV5xuYZ8N_cVVyycHUzegTTVWkAw/edit
#the google sheet is located here: https://docs.google.com/spreadsheets/d/1UmmLPVldYR80taqco8byFmBWe1NnQoFUOR9lttbJS7s/edit?usp=sharing

gKey = "AKfycbx8Che9DZwgA8SUrGgFiBCUkFB9zn9jZnlXEY2B4H5Hif5ND2DUdMYQpc-DJqqC8LOF"
gSheetKey = "1UmmLPVldYR80taqco8byFmBWe1NnQoFUOR9lttbJS7s"
url = 'https://script.google.com/macros/s/'+gKey+'/exec'
data = {}
data['Field1'] = "Some text"
data['Field2'] = 32
data['Field3'] = 0x32 
data['Sheet_id'] = gSheetKey
response = requests.post(url = url, json = data)
print(response.text)