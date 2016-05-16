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
