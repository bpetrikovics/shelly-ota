#!/usr/bin/env python3

import sys
import os
import os.path
import argparse
import logging
import threading
import concurrent.futures

import lib.venvtools as venvtools


venvtools.activate(os.path.abspath(os.path.dirname(__file__)))
import netifaces


from lib.shelly import ShellyFirmwareApi, ShellyDevice
from lib.updateserver import UpdateServer


def ifdetect():
    try:
        gw = netifaces.gateways().get('default')
        gw_if = gw[netifaces.AF_INET][1]
        addrs = netifaces.ifaddresses(gw_if)[netifaces.AF_INET]
    except Exception as exc:
        logging.error(f'Exception trying to determine default bind address: {exc}')
        return None

    return addrs[0]['addr']


if __name__ == '__main__':
    default_bind = ifdetect()

    parser = argparse.ArgumentParser(
        description="Tool to upgrade Shelly devices that do not have direct internet connectivity")
    parser.add_argument('-b', '--bindaddr',
                        required=False, default=default_bind, help=f'Interface address (IP) to listen on (default: {default_bind})')
    parser.add_argument('-p', '--port',
                        required=False, default=8080, type=int, help='Port number for the OTA server')
    parser.add_argument('-t', '--target',
                        required=True, help='Device address(es) or hostname(s) to upgrade, comma separated')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        required=False,
                        default=False,
                        help='Increase detail of logging')
    parser.add_argument('-n', '--dryrun',
                        action='store_true',
                        required=False,
                        default=False,
                        help='Don\'t actually perform upgrade'
                        )
    args = parser.parse_args()

    logger = logging.getLogger('shelly-ota')
    logging.basicConfig(
        level=logging.DEBUG if args.verbose is True else logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%m/%d/%Y %H:%M:%S')

    if args.bindaddr is None:
        logger.error('Bind address could not be determined, please pass a correct one with --bindaddr')
        sys.exit(1)

    logger.debug(f'OTA server will listen on {args.bindaddr}')

    api = ShellyFirmwareApi()
    server = UpdateServer(args)

    if args.dryrun:
        logger.info('Dry-run mode, will not actually perform updates')

    device_list = str(args.target).split(',')
    for item in device_list:
        device = ShellyDevice.discover(item)
        if device is None:
            logger.info('%s: Skipping this device', item)
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
            continue

        server.preload_firmware(latest)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(server.serve_once)
            device.request_ota(
                f'http://{args.bindaddr}:{args.port}/' + latest.url.split('/')[-1],
                args.dryrun)
            if future.result():
                logger.warning('%s: File was downloaded', device.address)
            else:
                logger.warning(
                    '%s: No successful download within timeout period', device.address)
