import unittest
import requests
import base64
import json

'''
The following assumes zequs service is running on localhost and listening on 
port 8081. Change host and port variables as needed below if this assumption 
is false.

Also, tests do not assume that there is a printer attached.
'''

host = "127.0.0.1"
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

def disablePrinter():
    url = "http://%s:%d/api/v1/zebrabadgeprinter/disable/" % (host, port)
    r = requests.put(url)

def enablePrinter():
    url = "http://%s:%d/api/v1/zebrabadgeprinter/enable/" % (host, port)
    r = requests.put(url)

def deleteAllJobs():
    url = "http://%s:%d/api/v1/zebrabadgeprinter/" % (host, port)
    r = requests.delete(url)

class TestZequsAPI(unittest.TestCase):

    def test_delete_all(self):
        disablePrinter()
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
        enablePrinter()

    def test_enable(self):
        enablePrinter()
        url = "http://%s:%d/api/v1/zebrabadgeprinter/" % (host, port)
        r = requests.get(url)
        self.assertTrue(r.status_code == 200)
        x = r.json()
        self.assertTrue("enabled" in x)
        self.assertTrue(x["enabled"] == 1)

    def test_disable_enable(self):
        disablePrinter()
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
        enablePrinter()

    def test_add(self):
        disablePrinter()
        deleteAllJobs()
        url = "http://%s:%d/api/v1/zebrabadgeprinter/" % (host, port)
        data = encodeImageAsJSON("badge.png")
        headers = {'content-type': 'application/json'}
        r = requests.post(url, headers=headers, data=data)
        self.assertTrue(r.status_code == 200)
        x = r.json()
        self.assertTrue("id" in x)
        deleteAllJobs()
        enablePrinter()

if __name__ == '__main__':
    unittest.main()
