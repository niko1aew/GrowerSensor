try:
    import gc
    import usocket as socket
except:
    import socket
import machine
from machine import Pin
from time import sleep
from time import time
import network
import ubinascii
import esp
import json
import urequests
import server
import os

DEBUG = True

SENSOR_PWR_PIN = 23
SENSOR_SIGNAL_PIN = 34

esp.osdebug(None)
gc.collect()

JSON_HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}

# Init config------------------
try:
    with open('config.json') as config_file:
        config = json.load(config_file)
except:
    if DEBUG:
        print("No configuration. Starting config server...")
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid='FlowerSensor')
    ap.config(password='flower')
    server.start_server_init()
# -----------------------------

# Save config-----------------
def save_config(data):
    with open('config.json', 'w') as f:
            json.dump(data, f,)

# Init Pins--------------------
led = Pin(5, Pin.OUT)
sensorPower = Pin(SENSOR_PWR_PIN, Pin.OUT)
sensorPower.value(1)
# dht = Dht11(22)
adc = machine.ADC(machine.Pin(SENSOR_SIGNAL_PIN))
adc.atten(adc.ATTN_11DB)
adc.width(adc.WIDTH_12BIT)
sleep(2)
# -----------------------------



# while not dht.getMeasure():
#     sleep(5)
#     if dht.getMeasure():
#         break

# sleep(1)

led.value(0)

# Init WiFi--------------------
ssid = config['WIFI_SSID']
password = config['WIFI_PASS']
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

attemptCount = 0

while station.isconnected() == False:
    attemptCount+=1
    if attemptCount==30:
        if DEBUG:
            print('connection fail')
        machine.deepsleep(60000*60)
    sleep(1)



led.value(1)

mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()

if DEBUG:
    print('Connection successful')
    print(station.ifconfig())
    print(mac)

# ------------------------------
if 'ACTIVATION_CODE' in config:
    
    url = config["SERVER_ADDRESS"] + "activate/"

    if DEBUG:
        print("Sending %s to server..." % config['ACTIVATION_CODE'])
        print(url)
    
    data = {"ACTIVATION_CODE": config["ACTIVATION_CODE"]}
    r = urequests.post(url, data=json.dumps(data), headers=JSON_HEADERS)
    response = r.json()

    if DEBUG:
        print("Received UUID: %s" % response["UUID"])
        print("Received INTERVAL: %s" % response["INTERVAL"])
    
    config['UUID'] = response["UUID"]
    config['INTERVAL'] = response["INTERVAL"]
    del config['ACTIVATION_CODE'] #Удалять, только если сервер ответил ОК
    save_config(config)
    url = config["SERVER_ADDRESS"] + "confirm-activation/"
    if DEBUG:
        print("Confirming activation on device")
        print(url)
    data = {"UUID": config["UUID"]}
    r = urequests.post(url, data=json.dumps(data), headers=JSON_HEADERS)

    if DEBUG:
        print("Server answer for activation confirm:")
        print(r.status_code)


# Measure-----------------------
sleep(5)
timeMeasure = str(time())
moisture = str(adc.read())
# ------------------------------

# Prepare and send data to server------------------------------
# my_string = "{{ \"time\": {},  \"moisture\": {},   \"temp\": {}, \"hum\": {}, \"desc\": \"Outside\" }}"
# outputStr = my_string.format(timeMeasure, moisture, dht.temperature, dht.humidity)
# my_string = "{{ \"time\": {},  \"moisture\": {}, \"desc\": \"Small lemon\" }}"
# outputStr = my_string.format(timeMeasure, moisture)
data = {}
data["UUID"] = config["UUID"]
data["moisture"] = moisture
# print(outputStr)

if DEBUG:
    print("Sending data to:", config['SERVER_ADDRESS'])
    print("Data:", data)
try:
    response = urequests.post(config['SERVER_ADDRESS']+"send/",
                              data=json.dumps(data), headers=JSON_HEADERS)
    # print(response.text)
except:
    print('connection error')
# -------------------------------------------------------------

# Sleep-----------------------
sensorPower.value(0)
sleep_time = config["INTERVAL"]*1000*60
# print(sleep_time)
# sleep(30)
# machine.deepsleep(sleep_time)
# ----------------------------