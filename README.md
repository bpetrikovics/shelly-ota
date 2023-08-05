# Shelly OTA update tool

[![CodeQL](https://github.com/bpetrikovics/shelly-ota/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/bpetrikovics/shelly-ota/actions/workflows/codeql-analysis.yml) [![Tests](https://github.com/bpetrikovics/shelly-ota/actions/workflows/python-ci.yml/badge.svg)](https://github.com/bpetrikovics/shelly-ota/actions/workflows/python-ci.yml)

This tool helps to upgrade Shelly devices that are behind a strict firewall or on a network segment without
internet connectivity. Other similar tools already exist with clever features like autodiscovery, but that
approach requires the code to be run on a host within that network segment for the zeroconf/Bonjour to work.

Some examples of other implementations I've checked and learned from:

* https://github.com/ruimarinho/shelly-updater
* https://github.com/bjuretko/shelly-offline-ota-update

In my specific case, due to how the network is organized, this does not work perfectly, and I also wanted
to have a possibility to trigger the update specifically for a given device (so it can be invoked by
Home Assistant, for example).

## How it works

* Model and current firmware information fetched from the device directly via the /shelly API route
* Available firmware versions are queried from the Shelly firmware API (api.shelly.cloud)
* If there is a newer firmware available, we set up a temporary socket server to respond to HTTP requests, and invoke
  the /ota API on the device to trigger the download and installation of the new firmware
* There is no connection from the Shelly device to the outside, it only accesses the webservice opened by the OTA tool
* Devices with restricted login are now supported

## Installation

Easiest is to install to a virtualenv directly from the source tree (please make sure you have python3 installed):

```bash
pip install virtualenv
git clone https://github.com/bpetrikovics/shelly-ota.git
cd shelly-ota
virtualenv -p python3 venv
source venv/bin/activate
pip install -e .
```

You can also build a python package that you can then install inside of a virtualenv:

```bash
python3 -m pip install build
python3 -m build
pip install dist/shelly-ota*tar.gz
```

Or outside of a virtualenv:

```bash
python3 -m pip install build
python3 -m build
deactivate
pip install dist/shelly-ota-*.tar.gz
```
## Updating

Ensure you are removing the correct version:

```
pip uninstall shelly_ota
cd shelly-ota
rm dist/shelly-ota-2022.8.20.tar.gz
git pull
python3 -m pip install build
python3 -m build
pip install dist/shelly-ota*tar.gz
```


## Usage

```
usage: shelly-ota [-h] [-b BINDADDR] [-p PORT] -t TARGET [-v] [-n] [--auth_env AUTH_ENV]
                  [--auth_file AUTH_FILE]

Tool to upgrade Shelly devices that do not have direct internet connectivity

optional arguments:
  -h, --help            show this help message and exit
  -b BINDADDR, --bindaddr BINDADDR
                        Interface address (IP) to listen on (default: 172.18.250.115)
  -p PORT, --port PORT  Port number for the OTA server
  -t TARGET, --target TARGET
                        Device address(es) or hostname(s) to upgrade, comma separated
  -v, --verbose         Increase detail of logging
  -n, --dryrun          Don't actually perform upgrade
  --auth_env AUTH_ENV   Environment variable to load single user:password pair from, will be used
                        for all password protected devices
  --auth_file AUTH_FILE
                        Full path to a file containing credential rule definitions for password
                        protected devices (see README)
```

* Will try to autodetect the bind address based on the interface that is related to the default gateway. IN case it's
  not the one you want to use, specify it with -b; this should correspond to an IP address reachable by the Shelly
  device.
* Port is defaulted to 8080
* Target can be a single device or a comma-separated list

If you want to update multiple devices of the same kind, the best is to do it in one batch as the temporary update
server will cache the
firmware file between requests, in memory.

Output will look like this:

```
$ ./shelly-ota -b 10.xx.xx.xx -t shellyplug-s-XXXXXX -v
03/07/2021 22:24:16 lib.shelly DEBUG Fetching latest firmware information via Shelly API
03/07/2021 22:24:16 urllib3.connectionpool DEBUG Starting new HTTPS connection (1): api.shelly.cloud:443
03/07/2021 22:24:16 urllib3.connectionpool DEBUG https://api.shelly.cloud:443 "GET /files/firmware HTTP/1.1" 200 None
03/07/2021 22:24:16 lib.updateserver DEBUG Starting updateserver on 10.xx.xx.xx:8080
03/07/2021 22:24:16 lib.shelly DEBUG shellyplug-s-XXXXXX: Discovering device
03/07/2021 22:24:16 urllib3.connectionpool DEBUG Starting new HTTP connection (1): shellyplug-s-XXXXXX:80
03/07/2021 22:24:16 urllib3.connectionpool DEBUG http://shellyplug-s-XXXXXX:80 "GET /shelly HTTP/1.1" 200 122
03/07/2021 22:24:16 shelly-ota INFO shellyplug-s-XXXXXX: Device type is SHPLG-S
03/07/2021 22:24:16 shelly-ota INFO shellyplug-s-XXXXXX: Current firmware version is 20190516-073020/master@ea1b23db
03/07/2021 22:24:16 shelly-ota DEBUG shellyplug-s-XXXXXX: Latest version for this model is 20210115-103659/v1.9.4@e2732e05 at http://shelly-api-eu.shelly.cloud/firmware/SHPLG-S.zip
03/07/2021 22:24:16 lib.updateserver DEBUG Preloading firmware <ShellyFirmware(('SHPLG-S', '20210115-103659/v1.9.4@e2732e05'), http://shelly-api-eu.shelly.cloud/firmware/SHPLG-S.zip)>
03/07/2021 22:24:16 urllib3.connectionpool DEBUG Starting new HTTP connection (1): shelly-api-eu.shelly.cloud:80
03/07/2021 22:24:16 urllib3.connectionpool DEBUG http://shelly-api-eu.shelly.cloud:80 "GET /firmware/SHPLG-S.zip HTTP/1.1" 200 826149
03/07/2021 22:24:17 lib.updateserver DEBUG Firmware file preloaded, 826149 bytes
03/07/2021 22:24:17 lib.shelly INFO shellyplug-s-XXXXXX: Will instruct Shelly to download firmware from: http://10.xx.xx.xx:8080/SHPLG-S.zip
03/07/2021 22:24:17 lib.shelly INFO shellyplug-s-XXXXXX: Shelly device API call: http://shellyplug-s-XXXXXX/ota?url=http://10.xx.xx.xx:8080/SHPLG-S.zip
03/07/2021 22:24:17 lib.updateserver DEBUG Socket server initialized
03/07/2021 22:24:17 urllib3.connectionpool DEBUG Starting new HTTP connection (1): shellyplug-s-XXXXXX:80
03/07/2021 22:24:17 urllib3.connectionpool DEBUG http://shellyplug-s-XXXXXX:80 "GET /ota?url=http://10.xx.xx.xx:8080/SHPLG-S.zip HTTP/1.1" 200 136
03/07/2021 22:24:17 lib.updateserver INFO 10.yy.yy.yy: Incoming HTTP request for /SHPLG-S.zip
03/07/2021 22:24:17 lib.updateserver DEBUG 10.yy.yy.yy: Serving firmware
10.yy.yy.yy - - [07/Mar/2021 22:24:17] "GET /SHPLG-S.zip HTTP/1.1" 200 -
03/07/2021 22:24:26 shelly-ota WARNING shellyplug-s-XXXXXX: File was downloaded
```

## Authentication

### Via environment

If all of your devices use the same login credentials, you can set up an environment variable with the username and password, and tell shelly-ota what environment to look for, e.g.:

```
$ export SHELLY_AUTH=admin:password
$ shelly-ota -t x.x.x.x --auth_env SHELLY_AUTH
```

### Using a credentials file

If you have different devices or groups of devices using different passwords, you can use an inventory/credentials file for storing the usernames and passwords. Check the provided ```auth_file.sample```.

```
$ shelly-ota -t x.x.x.x --auth_file /path/to/your/auth.file
```

Any issues, questions, suggestions, please let me know.

As usual, please note, although I've done some testing with my own devices, you're using this at your own risk.
