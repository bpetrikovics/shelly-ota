import logging
import http.server
import socketserver
import requests


SERVED = False


class Server(socketserver.TCPServer):

    allow_reuse_address = True
    timeout = 5

    def __init__(self, server_address, RequestHandlerClass, fwdata, bind_and_activate=True):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self._fwdata = fwdata
        logger.debug('Socket server initialized')


class Handler(http.server.BaseHTTPRequestHandler):

    server_version = 'ShellyUpdateServer/0.1'

    def do_GET(self):
        global SERVED

        # /SHPLG-S.zip -> extract model name
        try:
            path = self.path.split('/')[-1].split('.zip')[0]
        except Exception as exc:
            logger.error(
                f'%s: Unexpected/bad request for path {self.path}: {exc}', self.client_address)
            return
        logger.info('%s: Incoming HTTP request for %s',
                    self.client_address[0], self.path)
        if path in self.server._fwdata.keys():
            logger.debug('%s: Serving firmware', self.client_address[0])
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Length",
                             str(len(self.server._fwdata[path])))
            self.end_headers()
            self.wfile.write(self.server._fwdata[path])
            SERVED = True
        else:
            self.send_error(404)


class UpdateServer:
    def __init__(self, args):
        self._args = args
        self._fwdata = {}
        logger.debug(
            'Starting updateserver on %s:%s', self._args.bindaddr, self._args.port)

    def preload_firmware(self, firmware):
        logger.debug(f'Preloading firmware %s', str(firmware))
        _filename = firmware.url.split('/')[-1]

        res = requests.get(firmware.url)
        if res.status_code != 200:
            raise RuntimeError('Unable to download firmware file')

        self._fwdata[firmware.model] = res.content

        logger.debug('Firmware file preloaded, %d bytes', len(res.content))

    def serve_once(self):
        global SERVED

        with Server((self._args.bindaddr, self._args.port), Handler, self._fwdata) as httpd:
            SERVED = False
            httpd.handle_request()

        return SERVED


logger = logging.getLogger(__name__)
