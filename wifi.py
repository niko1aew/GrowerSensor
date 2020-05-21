
import network
import machine
import ubinascii
from time import sleep

DEBUG = True

def start_wifi_server():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid='FlowerSensor')
    ap.config(password='flower')

def start_wifi_client(ssid, pwd):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    print(ssid, pwd)
    station.connect(ssid, pwd)
    print("Waiting 5 sec")
    sleep(5)
    attemptCount = 0

    while station.isconnected() == False:
        attemptCount+=1
        if attemptCount==30:
            if DEBUG:
                print('connection fail')
            machine.deepsleep(60000*60)
    
    mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()
    if DEBUG:
        print('Connection successful')
        print(station.ifconfig())
        print(mac)