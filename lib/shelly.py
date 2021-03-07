import logging
import requests


class ShellyCommunicationError(Exception):
    def __repr__(self):
        return 'Unexpected response from Shelly device'


class ShellyDevice:
    def __init__(self, address, data=None):
        self._address = address
        if data:
            self._data = data

    def __repr__(self):
        return f'<ShellyDevice({self._address}>)'

    @classmethod
    def discover(self, address):
        logger.debug('%s: Discovering device', address)
        try:
            res = requests.get(f'http://{address}/shelly')
        except Exception as exc:
            logger.error('Exception during HTTP request: %s', str(exc))
            return None
        if res.status_code != 200:
            logger.error('%s: Communication error (is this a Shelly device?): HTTP/%s: %s',
                         address, res.status_code, res.content)
            return None
        return ShellyDevice(address, res.json())

    @property
    def address(self):
        return self._address

    @property
    def model(self):
        return self._data.get('type', 'Unknown')

    @property
    def mac(self):
        return self._data.get('mac')

    @property
    def has_auth(self):
        return self._data.get('auth')

    @property
    def firmware(self):
        return self._data.get('fw')

    def request_ota(self, url):
        logger.info('%s: Will instruct Shelly to download firmware from: %s',
                    self._address, url)
        logger.info('%s: Shelly device API call: %s', self._address,
                    f'http://{self._address}/ota?url={url}')
        res = requests.get(f'http://{self._address}/ota?url={url}')
        if res.status_code != 200:
           logger.error('OTA update error')


class ShellyFirmware:
    def __init__(self, model, data):
        self._data = data
        self._model = model

    def __repr__(self):
        return f"<ShellyFirmware({self.model}, {self.version}, {self.url})>"

    @property
    def model(self):
        return self._model

    @property
    def version(self):
        return self._data['version']

    @property
    def url(self):
        return self._data['url']


class ShellyFirmwareApi:

    BASEURL = 'https://api.shelly.cloud/files/firmware'

    def __init__(self):
        logger.debug('Fetching latest firmware information via Shelly API')
        res = requests.get(ShellyFirmwareApi.BASEURL)
        if res.status_code != 200:
            raise RuntimeError('Cannot load Shelly firmware versions')
        self._data = res.json()
        if not self._data.get('isok'):
            raise RuntimeError('Shelly firmware API data is invalid')

    def get_latest_firmware(self, model):
        return ShellyFirmware(model, self._data['data'].get(model))


logger = logging.getLogger(__name__)
