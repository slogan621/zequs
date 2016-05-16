# (C) Copyright Syd Logan 2016
# (C) Copyright Thousand Smiles Foundation 2016
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from zequspluginbase import ZequsPluginBase
import subprocess
import tempfile
import os

class PrinterPlugin(ZequsPluginBase):
    def __init__(self):
        super(PrinterPlugin, self).__init__()
        self._printerID = None
        self._jarfile = "zsdk_card_api-beta-1.0.2220.jar"
        self._command = "java -jar %s" % (self._jarfile)

    def _execute(self, args):
        cmd = cmd + self._command + " " + ' '.join(x for x in args)
        stdout=subprocess.check_output(cmd)
        return stdout

    # Return the ID of the printer. We only support USB printers
    # and if there are more than one printer attached, we return
    # only the first one in the list

    def _discover(self):
        ret = None
        args = ["discover", "--usb", "--json"]
        stdout = self._execute(args)
        return ret

    # reset printer

    def _reset(self):
        res = {}
        args = ["reset", self._printerID, "--usb"]
        stdout = self._execute(args)
        return res

    # print image to specified printer

    def printCard(self, path):
        ret = 3
        '''
        if self._printerID == None:
            self._discover()
        fp = tempfile.NamedTemporaryFile()
        sv = "--save %s" % (fp.name)
        args = ["graphic", path, "--format color", sv]
        stdout = self._execute(args)
        # check result of conversion
        validConversion = True
        # print
        if validConversion:
            ipath = "--image %s" % (fp.name) 
            args = ["print", self._printerID, ipath, "--usb"]
            stdout = self._execute(args)
            # check result of printing
        else:
        '''
            
        return ret

    # return printer status

    def getStatus(self):
        raise NotImplementedError

    # return driver version

    def getVersion(self):
        return "beta-1.0.2220"

    # return driver name

    def getName(self):
        raise "zsdk_card_api"

    # apply settings to the printer/driver

    def settings(self, settings):
        raise NotImplementedError

    # get settings for specified printer

    def getSettings(self):
        raise NotImplementedError
