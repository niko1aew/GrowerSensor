from microWebSrv import MicroWebSrv
import json
import machine

def start_server_init():
    """Run server for device configuration"""
    print('Starting init server...')
    srv = MicroWebSrv(webPath='/www/')
    srv.Start(threaded=False)

@MicroWebSrv.route('/init_settings')
def _httpHandlerInitSettingsGet(httpClient, httpResponse):
    print("GET init settings")
    page = open('./www/index.html', 'r').read()

    httpResponse.WriteResponseOk(headers=None,
                                 contentType="text/html",
                                 contentCharset="UTF-8",
                                 content=page)

@MicroWebSrv.route('/get_config')
def _httpHandlerInitSettingsGet(httpClient, httpResponse):
    print("Get config method")
    try:
        with open('config.json') as config_file:
            print("openning config file")
            response = json.load(config_file)
            response["STATUS"] = "OK"
    except:
        print("no or bad config file")
        response = {
            'STATUS': 'NO_CONFIG',
            'MESSAGE': 'Отсутствует файл конфигурации'
        }

    httpResponse.WriteResponseJSONOk(response)

@MicroWebSrv.route('/init_settings', 'POST')
def _httpHandlerInitSettingsPost(httpClient, httpResponse):
    formData = httpClient.ReadRequestPostedFormData()
    device_config = init_config()

    print('Form data:')
    print(formData)
    
    print('Saved config:')
    print(device_config)

    device_config['WIFI_SSID'] = formData["ssid"]
    device_config['WIFI_PASS'] = formData["password"]
    device_config['SERVER_ADDRESS'] = formData["serverUrl"]
    device_config['WIFI_SSID'] = formData["ssid"]

    if 'code' in formData:
        device_config['ACTIVATION_CODE'] = formData["code"]

    print('New config:')
    print(device_config)

    try:
        with open('config.json', 'w') as f:
            json.dump(device_config, f,)
        page = open('./www/config_success.html', 'r').read()
    except:
        page = 'Error while writing config'

    httpResponse.WriteResponseOk( headers		 = None,
								  contentType	 = "text/html",
								  contentCharset = "UTF-8",
								  content 		 = page )
    
@MicroWebSrv.route('/reboot')
def _httpHandlerRebootGet(httpClient, httpResponse):
    machine.reset()

def init_config():
    try:
        with open('config.json') as config_file:
            return json.load(config_file)
    except:
        print("Failed to load config...")
        return {}