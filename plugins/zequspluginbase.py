class ZequsPluginBase(object):
    def __init__(self):
        pass

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
        raise NotImplementedError

    # return driver name

    def getName(self):
        raise NotImplementedError

    # apply settings to the printer/driver

    def settings(self, printerID, settings):
        raise NotImplementedError

    # get settings for specified printer

    def getSettings(self, printerID):
        raise NotImplementedError

'''
 discover - Discover printers
 graphic  - Converts a graphic to a format that can be printed by a Zebra Card
Printer
 help     - Get information about other commands
 position - Positions a card int the printer
 print    - Prints bitmap image files
 reset    - Resets a printer
 settings - Sets or gets the printer's settings
 status   - Gets the specified status from the printer
 update   - Updates the firmware on the printer
''' 
