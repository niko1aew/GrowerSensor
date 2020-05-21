try:
    import gc
    import usocket as socket
except:
    import socket
import machine
from machine import Pin
from time import sleep
from time import time
import wifi
import machine
import esp
import json
import urequests
import server
import os

DEBUG = True

SENSOR_PWR_PIN = 23
SENSOR_SIGNAL_PIN = 34
CONFIG_SW = 12

esp.osdebug(None)
gc.collect()

JSON_HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}



# Save config-----------------
def save_config(data):
    with open('config.json', 'w') as f:
            json.dump(data, f,)

# Init Pins--------------------
config_switch = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
led = Pin(5, Pin.OUT)
sensor_power = Pin(SENSOR_PWR_PIN, Pin.OUT)
sensor_power.value(1)
# dht = Dht11(22)
adc = machine.ADC(machine.Pin(SENSOR_SIGNAL_PIN))
adc.atten(adc.ATTN_11DB)
adc.width(adc.WIDTH_12BIT)
sleep(2)
# -----------------------------
if config_switch.value() is 0:
    print("Run config...")
    wifi.start_wifi_server()
    server.start_server_init()

# Init config------------------
try:
    with open('config.json') as config_file:
        config = json.load(config_file)
except:
    if DEBUG:
        print("No configuration. Starting config server...")
    wifi.start_wifi_server()
    server.start_server_init()
# -----------------------------

led.value(0)
wifi.start_wifi_client(config['WIFI_SSID'], config['WIFI_PASS'])
led.value(1)

# ------------------------------
if 'ACTIVATION_CODE' in config:
    
    url = config["SERVER_ADDRESS"] + "activate/"

    if DEBUG:
        print("Sending %s to server..." % config['ACTIVATION_CODE'])
        print(url)
    
    data = {"ACTIVATION_CODE": config["ACTIVATION_CODE"]}

    try:
        r = urequests.post(url, data=json.dumps(data), headers=JSON_HEADERS)
    except:
        print("Failed to post data to server")
        sleep(10)
        machine.reset()
    print(r)
    response = r.json()
    print(dir(response))
    result_success = response["SUCCESS"]

    if not result_success:
        print(response["MSG"])
        sleep(10)
        machine.reset()
    
    
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
sensor_power.value(0)
sleep_time = config["INTERVAL"]*1000*60
# print(sleep_time)
# sleep(30)
# machine.deepsleep(sleep_time)
# ----------------------------