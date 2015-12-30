import unittest
import requests
import base64
import json
from time import sleep

'''
Change host and port variables as needed below to identify location of
the print server. 

Tests do not assume that there is a printer attached, and do not test 
plugins.
'''

host = "192.168.0.120"
port = 8081

def encodeImageAsJSON(path):
    ret = {}
    try:
        f = open(path, "rb")
        image = f.read()
        b64 = base64.b64encode(image)
        ret["data"] = b64
        ret = json.dumps(ret)
    except:
        print "failed to read and encode %s" % (path)
    return ret

def enableTestMode():
    url = "http://%s:%d/api/v1/zebrabadgeprinter/testmode/enable/" % (host, port)
    r = requests.put(url)

def disableTestMode():
    url = "http://%s:%d/api/v1/zebrabadgeprinter/testmode/disable/" % (host, port)
    r = requests.put(url)

def enablePrinter():
    url = "http://%s:%d/api/v1/zebrabadgeprinter/enable/" % (host, port)
    r = requests.put(url)

def disablePrinter():
    url = "http://%s:%d/api/v1/zebrabadgeprinter/disable/" % (host, port)
    r = requests.put(url)

def deleteAllJobs():
    url = "http://%s:%d/api/v1/zebrabadgeprinter/" % (host, port)
    r = requests.delete(url)

class TestZequsAPI(unittest.TestCase):

    def test_delete_all(self):
        disablePrinter()
        enableTestMode()
        deleteAllJobs()
        url = "http://%s:%d/api/v1/zebrabadgeprinter/" % (host, port)
        r = requests.get(url)
        self.assertTrue(r.status_code == 200)
        x = r.json()
        self.assertTrue(x["jobs"] == 0)
        url = "http://%s:%d/api/v1/zebrabadgeprinter/" % (host, port)
        data = encodeImageAsJSON("badge.png")
        headers = {'content-type': 'application/json'}
        r = requests.post(url, headers=headers, data=data)
        self.assertTrue(r.status_code == 200)
        x = r.json()
        self.assertTrue("id" in x)
        url = "http://%s:%d/api/v1/zebrabadgeprinter/" % (host, port)
        r = requests.get(url)
        self.assertTrue(r.status_code == 200)
        x = r.json()
        self.assertTrue(x["jobs"] == 1)
        deleteAllJobs()
        url = "http://%s:%d/api/v1/zebrabadgeprinter/" % (host, port)
        r = requests.get(url)
        self.assertTrue(r.status_code == 200)
        x = r.json()
        self.assertTrue(x["jobs"] == 0)

    def test_enable(self):
        enablePrinter()
        enableTestMode()
        url = "http://%s:%d/api/v1/zebrabadgeprinter/" % (host, port)
        r = requests.get(url)
        self.assertTrue(r.status_code == 200)
        x = r.json()
        self.assertTrue("enabled" in x)
        self.assertTrue(x["enabled"] == 1)
        disablePrinter()

    def test_disable_enable(self):
        disablePrinter()
        enableTestMode()
        url = "http://%s:%d/api/v1/zebrabadgeprinter/" % (host, port)
        r = requests.get(url)
        self.assertTrue(r.status_code == 200)
        x = r.json()
        self.assertTrue("enabled" in x)
        self.assertTrue(x["enabled"] == 0)
        enablePrinter()
        url = "http://%s:%d/api/v1/zebrabadgeprinter/" % (host, port)
        r = requests.get(url)
        self.assertTrue(r.status_code == 200)
        x = r.json()
        self.assertTrue("enabled" in x)
        self.assertTrue(x["enabled"] == 1)

    def test_queryprinter(self):
        disablePrinter()
        enableTestMode()
        deleteAllJobs()
        url = "http://%s:%d/api/v1/zebrabadgeprinter/" % (host, port)
        r = requests.get(url)
        self.assertTrue(r.status_code == 200)
        x = r.json()
        self.assertTrue("enabled" in x)
        self.assertTrue(x["enabled"] == 0)
        self.assertTrue("jobs" in x)
        self.assertTrue("queued" in x)
        self.assertTrue("printing" in x)
        self.assertTrue("failed" in x)
        self.assertTrue("complete" in x)

        # create a job and see if queued is set to 1 for the printer

        url = "http://%s:%d/api/v1/zebrabadgeprinter/" % (host, port)
        data = encodeImageAsJSON("badge.png")
        headers = {'content-type': 'application/json'}
        r = requests.post(url, headers=headers, data=data)
        self.assertTrue(r.status_code == 200)
        x = r.json()
        job = x["id"]

        url = "http://%s:%d/api/v1/zebrabadgeprinter/" % (host, port)
        r = requests.get(url)
        self.assertTrue(r.status_code == 200)
        x = r.json()
        self.assertTrue("queued" in x)
        self.assertTrue(x["queued"] == 1)
        self.assertTrue("jobs" in x)
        self.assertTrue(x["jobs"] == 1)

        # now query the job

        url = "http://%s:%d/api/v1/zebrabadgeprinter/%d/" % (host, port, job)
        r = requests.get(url)
        self.assertTrue(r.status_code == 200)
        x = r.json()
        self.assertTrue("state" in x)
        self.assertTrue(x["state"] == 0) # queued
        self.assertTrue("id" in x)

        self.assertTrue(int(x["id"]) == job)

        deleteAllJobs()

    def test_add(self):
        disablePrinter()
        enableTestMode()
        deleteAllJobs()
        url = "http://%s:%d/api/v1/zebrabadgeprinter/" % (host, port)
        data = encodeImageAsJSON("badge.png")
        headers = {'content-type': 'application/json'}
        r = requests.post(url, headers=headers, data=data)
        self.assertTrue(r.status_code == 200)
        x = r.json()
        self.assertTrue("id" in x)
        deleteAllJobs()

    def test_simulated_print(self):
        disablePrinter()
        deleteAllJobs()
        enableTestMode()
        enablePrinter()
        url = "http://%s:%d/api/v1/zebrabadgeprinter/" % (host, port)
        data = encodeImageAsJSON("badge.png")
        headers = {'content-type': 'application/json'}
        r = requests.post(url, headers=headers, data=data)
        self.assertTrue(r.status_code == 200)
        x = r.json()
        self.assertTrue("id" in x)
        job = x["id"]

        # allow for time to print

        sleep(30)

        # verify the simulated print was successful

        url = "http://%s:%d/api/v1/zebrabadgeprinter/%d/" % (host, port, job)
        r = requests.get(url)
        self.assertTrue(r.status_code == 200)
        x = r.json()
        self.assertTrue("state" in x)
        self.assertTrue(x["state"] == 3) # success == 3
        self.assertTrue("id" in x)

        self.assertTrue(int(x["id"]) == job)
        deleteAllJobs()
        disablePrinter()

if __name__ == '__main__':
    unittest.main()
