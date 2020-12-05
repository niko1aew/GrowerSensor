'use strict';
window.addEventListener('load', function () {
  var errorBlock = document.getElementsByClassName('error')[0],
    spinnerBlock = document.getElementsByClassName('spinner')[0],
    settingsBlock = document.getElementsByClassName('settings-form')[0],
    activationCodeBlock = document.getElementById('activationCodeBlock'),
    serverInput = document.getElementById('serverInput'),
    codeInput = document.getElementById('codeInput'),
    ssidInput = document.getElementById('ssidInput'),
    passwordInput = document.getElementById('passwordInput');
    // intervalInput = document.getElementById('intervalInput');

  spinnerBlock.style.display = 'block';

  fetch('http://192.168.4.1/get_config')
    .then((response) => response.json())
    .then((data) => {
      spinnerBlock.style.display = 'none';
      if (data && data.STATUS === 'NO_CONFIG') {
        settingsBlock.style.display = 'block';
      } else if (data && data.STATUS === 'OK') {
        serverInput.value = data.SERVER_ADDRESS;
        codeInput.value = data.ACTIVATION_CODE ?? '';
        activationCodeBlock.remove();
        // activationCodeBlock.style.display = data.ACTIVATION_CODE
        //   ? 'block'
        //   : 'none';
        ssidInput.value = data.WIFI_SSID;
        passwordInput.value = data.WIFI_PASS;
        settingsBlock.style.display = 'block';
      }
    })
    .catch((error) => {
      spinnerBlock.style.display = 'none';
      errorBlock.innerHTML =
        'Внутренняя ошибка. Попробуйте перезагрузить устройство.';
      errorBlock.style.display = 'block';
      console.error('Error:', error);
    });
});
