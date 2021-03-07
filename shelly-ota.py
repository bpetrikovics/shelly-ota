#!/usr/bin/env python3

import sys
import os
import os.path
import argparse
import logging
import threading
import concurrent.futures


def activate(basedir):
    """ Look for and activate a virtualenv within the given base directory """

    for dir in [f.path for f in os.scandir(basedir) if f.is_dir()]:
        activate = os.path.join(basedir, dir, 'bin', 'activate_this.py')
        if os.path.isfile(activate):
            try:
                exec(open(activate).read(), {'__file__': activate})
            except Exception as exc:
                print(
                    'Could not run activate script. Module imports will most likely fail.', exc)


if __name__ == '__main__':
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    activate(BASEDIR)

    from lib.shelly import ShellyFirmwareApi, ShellyDevice
    from lib.updateserver import UpdateServer

    parser = argparse.ArgumentParser(
        description="Tool to upgrade Shelly devices that do not have direct internet connectivity")
    parser.add_argument('-b', '--bindaddr',
                        required=True, help='Interface address (IP) to listen on')
    parser.add_argument('-p', '--port',
                        required=False, default=8080, type=int, help='Port number for the OTA server')
    parser.add_argument('-t', '--target',
                        required=True, help='Device address(es) or hostname(s) to upgrade, comma separated')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        required=False,
                        default=False,
                        help='Increase detail of logging')
    args = parser.parse_args()

    logger = logging.getLogger('shelly-ota')
    logging.basicConfig(
        level=logging.DEBUG if args.verbose is True else logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%m/%d/%Y %H:%M:%S')

    api = ShellyFirmwareApi()
    server = UpdateServer(args)

    device_list = str(args.target).split(',')
    for item in device_list:
        device = ShellyDevice.discover(item)
        if device is None:
            logging.info('%s: Skipping this device', item)
            continue

        logger.info('%s: Device type is %s', device.address, device.model)
        logger.info('%s: Current firmware version is %s',
                    device.address, device.firmware)

        latest = api.get_latest_firmware(device.model)
        logger.debug(
            '%s: Latest version for this model is %s at %s', device.address, latest.version, latest.url)

        if device.firmware == latest.version:
            logger.info(
                '%s: No update available, skipping this device', device.address)
            #continue

        server.preload_firmware(latest)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(server.serve_once)
            device.request_ota(
                f'http://{args.bindaddr}:{args.port}/' + latest.url.split('/')[-1])
            if future.result():
                logger.warning('%s: File was downloaded', device.address)
            else:
                logger.warning(
                    '%s: No successful download within timeout period', device.address)
