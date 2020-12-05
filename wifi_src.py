
import network
import machine
import ubinascii
from time import sleep

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
            print('Wifi connection fail')
            return False
    
    mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()
    
    print('Connection successful')
    print(station.ifconfig())
    print(mac)

    return True