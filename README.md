# Octoprint-PSUControl-ESPurna

**Description:** This plugin allows to control devices flashed with the ESPurna Firmware.

Bassed on [OctoPrint PSU Control - Tasmota](https://github.com/kantlivelong/OctoPrint-PSUControl-Tasmota)
## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/luismanson/Octoprint-PSUControl-ESPurna/archive/master.zip

**TODO:** Describe how to install your plugin, if more needs to be done than just installing it via pip or through
the plugin manager.

## Configuration

- Log into your ESPurna device
- Go to the _Admin_ Tab and set the following:
  - Enable HTTP API: Yes
  - Restful API: No
- Generate or set an 'HTTP API Key'
- In Octoprint set the address, relaynumber and API key from your ESPurna device.
