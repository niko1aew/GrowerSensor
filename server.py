from microWebSrv import MicroWebSrv
import json
import machine

def start_server_init():
    """Run server for device configuration"""
    print('Starting init server...')
    srv = MicroWebSrv(webPath='www/init/')
    srv.Start(threaded=False)

@MicroWebSrv.route('/init_settings')
def _httpHandlerInitSettingsGet(httpClient, httpResponse):
    print("GET init settings")
    page = open('./www/init/index.html', 'r').read()

    httpResponse.WriteResponseOk(headers=None,
                                 contentType="text/html",
                                 contentCharset="UTF-8",
                                 content=page)

@MicroWebSrv.route('/init_settings', 'POST')
def _httpHandlerInitSettingsPost(httpClient, httpResponse):
    formData = httpClient.ReadRequestPostedFormData()
    config = {}
    config['WIFI_SSID'] = formData["ssid"]
    config['WIFI_PASS'] = formData["password"]
    config['ACTIVATION_CODE'] = formData["code"]
    config['SERVER_ADDRESS'] = formData["serverUrl"]
    with open('config.json', 'w') as f:
        json.dump(config, f,)
    page = open('./www/init/config_success.html', 'r').read()

    httpResponse.WriteResponseOk( headers		 = None,
								  contentType	 = "text/html",
								  contentCharset = "UTF-8",
								  content 		 = page )
    
@MicroWebSrv.route('/reboot')
def _httpHandlerRebootGet(httpClient, httpResponse):
    machine.reset()
# -----------------------------------------------------