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

esp.osdebug(None)
gc.collect()

# Init Pins--------------------
led = Pin(5, Pin.OUT)
sensorPower = Pin(33, Pin.OUT)
sensorPower.value(1)
adc = machine.ADC(machine.Pin(32))
adc.atten(adc.ATTN_11DB)
# -----------------------------

# Init config------------------
with open('config.json') as config_file:
	config = json.load(config_file)
# -----------------------------

sleep(1)

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
        print('connection fail')
        machine.deepsleep(60000*60)
    sleep(1)

print('Connection successful')
led.value(1)
print(station.ifconfig())
mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()
print(mac)
# ------------------------------

# Measure-----------------------
sleep(5)
timeMeasure = str(time())
moisture = str(adc.read())
# ------------------------------

# Prepare and send data to server------------------------------
my_string = "{{ \"time\": {},  \"moisture\": {}, \"desc\": \"prototype_0\" }}"
outputStr = my_string.format(timeMeasure, moisture)
print(outputStr)
try:
    response = urequests.post(config['IP_ENDPOINT'],
                              data=outputStr)
    print(response.text)
except:
    print('connection error')
# -------------------------------------------------------------

# Sleep-----------------------
sensorPower.value(0)
machine.deepsleep(120000*60)
# ----------------------------