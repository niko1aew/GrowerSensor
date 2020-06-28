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
    print(formData)
    config = {
        'WIFI_SSID': formData["ssid"],
        'WIFI_PASS': formData["password"],
        'ACTIVATION_CODE': formData["code"],
        'SERVER_ADDRESS': formData["serverUrl"],
        # 'INTERVAL': formData["interval"]
    }
    print(config)
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f,)
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