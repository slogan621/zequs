'''
Template plugin. Copy this file to a file with a name that reflects your 
printer/driver, and implement the methods. To use, update the plugin name 
in /etc/zequs.conf. For example, if the plugin file is named "my-printer.py", 
then /etc/zequs.conf should look like this:

[plugin]
name: my-printer

Note that the file must implement a class named PrinterPlugin that inherits
ZequsPluginBase. The rest is up to you, and depends on how your plugin 
intefaces with the printer (via a driver, commandline app, network connection,
or whatever).
'''

from zequspluginbase import ZequsPluginBase

class PrinterPlugin(ZequsPluginBase):
    def __init__(self):
        super(PrinterPlugin, self).__init__()

    # print image to specified printer

    def printCard(self, path):
        raise NotImplementedError

    # return printer status

    def getStatus(self):
        raise NotImplementedError

    # return driver version

    def getVersion(self):
        raise NotImplementedError 

    # return driver name

    def getName(self):
        raise NotImplementedError 

    # apply settings to the printer/driver

    def settings(self, settings):
        raise NotImplementedError

    # get settings for specified printer

    def getSettings(self):
        raise NotImplementedError
