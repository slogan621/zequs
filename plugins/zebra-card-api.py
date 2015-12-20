from zequspluginbase import ZequsPluginBase

class PrinterPlugin(ZequsPluginBase):
    def __init__(self):
        super(PrinterPlugin, self).__init__()

    # return a dictionary of printer ID, description pairs

    def discover(self):
        raise NotImplementedError

    # open the specified printer

    def open(self, printerID):
        raise NotImplementedError

    # print image to specified printer

    def printCard(self, printerID, img):
        raise NotImplementedError

    # return printer status

    def getStatus(self, printerID):
        raise NotImplementedError

    # close printer

    def close(self, printerID):
        raise NotImplementedError

    # reset printer

    def reset(self, printerID):
        raise NotImplementedError 

    # return driver version

    def getVersion(self):
        return "beta-1.0.2220"

    # return driver name

    def getName(self):
        raise "zsdk_card_api"

    # apply settings to the printer/driver

    def settings(self, printerID, settings):
        raise NotImplementedError

    # get settings for specified printer

    def getSettings(self, printerID):
        raise NotImplementedError
