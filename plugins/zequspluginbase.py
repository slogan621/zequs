class ZequsPluginBase(object):
    def __init__(self):
        pass

    # print image 

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
