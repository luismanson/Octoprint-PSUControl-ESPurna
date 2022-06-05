# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import requests

__plugin_pythoncompat__ = ">=3,<4"


class PSUControl_Espurna(octoprint.plugin.StartupPlugin,
                         octoprint.plugin.RestartNeedingPlugin,
                         octoprint.plugin.TemplatePlugin,
                         octoprint.plugin.SettingsPlugin):

    def __init__(self):
        self.config = dict()

    def get_settings_defaults(self):
        return dict(
            address='',
            relay=0,
            apikey=''
        )

    def on_settings_initialized(self):
        self.reload_settings()

    def reload_settings(self):
        for k, v in self.get_settings_defaults().items():
            if type(v) == str:
                v = self._settings.get([k])
            elif type(v) == int:
                v = self._settings.get_int([k])
            elif type(v) == float:
                v = self._settings.get_float([k])
            elif type(v) == bool:
                v = self._settings.get_boolean([k])

            self.config[k] = v
            self._logger.debug("{}: {}".format(k, v))

    def on_startup(self, host, port):
        psucontrol_helpers = self._plugin_manager.get_helpers("psucontrol")
        if not psucontrol_helpers or 'register_plugin' not in psucontrol_helpers.keys():
            self._logger.warning(
                "The version of PSUControl that is installed does not support plugin registration.")
            return
        self._logger.debug("Registering plugin with PSUControl")
        psucontrol_helpers['register_plugin'](self)

    def send(self, cmd):
        url = "http://{}/api/relay/{}".format(
            self.config['address'], self.config['relay'])
        params = dict(apikey=self.config['apikey'], timeout=5, headers={
                      'Accept': 'application/json'})
        params.update(cmd)
        response = None
        try:
            response = requests.get(url, params=params, timeout=15)
        except (
                requests.exceptions.InvalidURL,
                requests.exceptions.ConnectionError
        ):
            self._logger.error(
                "Unable to communicate with device. Check settings.")
        except Exception:
            self._logger.exception("Exception while making API call")
        else:
            self._logger.debug("cmd={}, status_code={}, text={}".format(
                cmd, response.status_code, response.text))

            if response.status_code == 401:
                self._logger.warning(
                    "Server returned 401 Unauthorized. Check credentials.")
                response = None

        return response

    def turn_psu_on(self):
        self._logger.debug("Switching PSU On")
        cmd = {'value': '1'}
        self.send(cmd)

    def turn_psu_off(self):
        self._logger.debug("Switching PSU Off")
        cmd = {'value': '0'}
        self.send(cmd)

    def get_psu_state(self):
        self._logger.debug("Check PSU status")
        elrelay = "relay/" + str(self.config['relay'])
        response = self.send('')
        if not response:
            return False
        data = response.json()
        status = None
        try:
            status = (data == 1)
        except KeyError:
            pass

        if status == None:
            self._logger.error("Unable to determine status. Check settings.")
            status = False
        return status

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.reload_settings()

    def get_settings_version(self):
        return 1

    def on_settings_migrate(self, target, current=None):
        pass

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]

    def get_update_information(self):
        return dict(
            psucontrol_espurna=dict(
                displayName="PSU Control - ESPurna",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="luismanson",
                repo="OctoPrint-PSUControl-Espurna",
                current=self._plugin_version,

                # update method: pip w/ dependency links
                pip="https://github.com/luismanson/OctoPrint-PSUControl-Espurna/archive/{target_version}.zip"
            )
        )


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PSUControl_Espurna()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
