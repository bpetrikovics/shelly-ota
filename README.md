# Shelly OTA update tool

This tool helps to upgrade Shelly devices that are behind a strict firewall or on a network segment without
internet connectivity. Other similar tools already exist with clever features like autodiscovery, but that
approach requires the code to be run on a host within that network segment for the zeroconf/Bonjour to work.

Some examples of other implementations I've checked and learned from:
* https://github.com/ruimarinho/shelly-updater
* https://github.com/bjuretko/shelly-offline-ota-update

In my specific case, due to how the network is organized, this does not work perfectly, and I also wanted
to have a possibility to trigger the update specifically for a given device (so it can be invoked by
Home Assistant, for example).

More documentation coming soon :)

**WARNING: CODE NOT PROPERLY TESTED YET**

For the time being, this is incomplete code and you use it at your own risk. Any feedback welcome.
