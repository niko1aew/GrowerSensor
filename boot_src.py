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

# SENSOR_PWR_PIN = 23
SENSOR_PWR_PIN = 33
SENSOR_SIGNAL_PIN = 32
CONFIG_SW = 22

esp.osdebug(None)
gc.collect()

JSON_HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}

def set_error(error_text):
    print(error_text)
    sleep(10)
    machine.reset()

def save_config(data):
    with open('config.json', 'w') as f:
            json.dump(data, f,)

def run_config_server():
    print("Run config...")
    wifi.start_wifi_server()
    server.start_server_init()

def init_pins():
    try:
        config_switch = machine.Pin(CONFIG_SW, machine.Pin.IN, machine.Pin.PULL_UP)
        led = Pin(5, Pin.OUT)
        sensor_power = Pin(SENSOR_PWR_PIN, Pin.OUT)
        sensor_power.value(1)
        adc = machine.ADC(machine.Pin(SENSOR_SIGNAL_PIN))
        adc.atten(adc.ATTN_11DB)
        adc.width(adc.WIDTH_12BIT)
        sleep(2)

        return config_switch, led, sensor_power, adc
    except:
        set_error("Failed to init pins")

def init_config():
    try:
        with open('config.json') as config_file:
            return json.load(config_file)
    except:
        print("Failed to load config...")
        return False

def start_wifi(config, led):
    led.value(0)
    print("Starting wifi...")
    result = wifi.start_wifi_client(config['WIFI_SSID'], config['WIFI_PASS'])
    if result:
        led.value(1)
    return result

def get_config_from_server(config):
    url = config["SERVER_ADDRESS"] + "api/flowers/getsensorconfig?activationCode=" + config['ACTIVATION_CODE']

    print("Requesting configuration...")
    print(url)

    try:
        config_response = urequests.get(url)

        if config_response.status_code == 200:
            config_payload = config_response.json()
            uuid = config_payload["uuid"]
            interval = config_payload["interval"]
            print("Received UUID: %s" % uuid)
            print("Received interval: %s" % interval)
            config['UUID'] = uuid
            config['INTERVAL'] = interval
            return config
        else:
            print("Configuration request failed: %s" % config_response.status_code)
            return False
    except Exception as err:
        print("Configuration request error: {0}".format(err))
        return False

def process_activation(config):
    url = config["SERVER_ADDRESS"] + "api/flowers/activateflower"
    data = { "uuid": config["UUID"], "activationCode": config['ACTIVATION_CODE'] }

    print("Performing activation...")
    print(url)
    activation_response = urequests.get(url, data=json.dumps(data), headers=JSON_HEADERS)

    if activation_response.status_code == 200:
        del config['ACTIVATION_CODE']
        print("Flower activation success")
        return config
    else:
        dir(activation_response)
        print("Activation request failed: %s" % activation_response.status_code)
        return False

def get_measure(adc):
    try:
        sleep(5)
        return str(adc.read())
    except Exception as err:
        print("Measure error: {0}".format(err))
        return False

def send_measure(data):
    url = config["SERVER_ADDRESS"] + "api/flowers/registermeasure"
    try:
        response = urequests.post(url, data=json.dumps(data), headers=JSON_HEADERS)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            print(response_data)
            return response_data
    except:
        return False
        
def go_to_sleep(sleep_time, sensor_power):
    try:
        sensor_power.value(0)
        print("Deep sleep ({0}) in 5 sec", sleep_time)
        sleep(5)
        machine.deepsleep(sleep_time)
        return True
    except:
        return False

# -------------------------------------------------------------
pins = init_pins()

config_switch = pins[0]
led = pins[1]
sensor_power = pins[2]
adc = pins[3]

if config_switch.value() is 0:
    run_config_server()

config = init_config()

if init_config() == False:
    print("No configuration. Starting config server...")
    run_config_server()

if start_wifi(config, led) == False:
    set_error("Wifi connection failed. Rebooting...")

if 'ACTIVATION_CODE' in config:
    config = get_config_from_server(config)

    if config == False:
        set_error("Failed to get config. Rebooting...")
    else:
        save_config(config)

    config = process_activation(config)
    if config == False:
        set_error("Failed to activate")
    else:
        save_config(config)

measure = get_measure(adc)
if measure == False:
    set_error("Failed to read data from sensor. Rebooting...")

data = { "uuid": config["UUID"], "moisture": measure }

print("Sending data to:", config['SERVER_ADDRESS'])
print("Data:", data)

response_data = send_measure(data)

if response_data == False:
    set_error("Failed to send data")
else:
    if "sleepInterval" in response_data:
        print("Go to sleep: %s" % response_data["sleepInterval"])
        if go_to_sleep(response_data["sleepInterval"], sensor_power) == False:
            set_error("Failed to sleep. Rebooting...")
        