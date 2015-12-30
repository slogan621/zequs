from zequspluginbase import ZequsPluginBase
import subprocess
import tempfile
import os

class PrinterPlugin(ZequsPluginBase):
    def __init__(self):
        super(PrinterPlugin, self).__init__()
        self._jarfile = "zsdk_card_api-beta-1.0.2220.jar"
        self._command = "java -jar %s" % (self._jarfile)

    def _execute(self, args):
        cmd = cmd + self._command + " " + ' '.join(x for x in args)
        stdout=subprocess.check_output(cmd)
        return stdout

    # return a dictionary of printer ID, description pairs

    def discover(self):
        ret = {}
        args = ["discover", "--usb", "--json"]
        stdout = self._execute(args)
        return ret

    # open the specified printer

    def open(self, printerID):
        raise NotImplementedError

    # print image to specified printer

    def printCard(self, path):
        ret = 3
        '''
        fp = tempfile.NamedTemporaryFile()
        sv = "--save %s" % (fp.name)
        args = ["graphic", path, "--format color", sv]
        stdout = self._execute(args)
        # check result of conversion
        validConversion = True
        # print
        if validConversion:
            ipath = "--image %s" % (fp.name) 
            args = ["print", printerID, ipath, "--usb"]
            stdout = self._execute(args)
            # check result of printing
        else:
        '''
            
        return ret

    # return printer status

    def getStatus(self, printerID):
        raise NotImplementedError

    # close printer

    def close(self, printerID):
        raise NotImplementedError

    # reset printer

    def reset(self, printerID):
        res = {}
        args = ["reset", printerID, "--usb"]
        stdout = self._execute(args)
        return res

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
