import unittest
import requests

'''
The following assumes zequs service is running on localhost and listening on 
port 8081. Change host and port variables as needed below if this assumption 
is false.

Also, tests do not assume that there is a printer attached.
'''

host = "127.0.0.1"
port = 8081

def disablePrinter():
    url = "http://%s:%d/api/v1/zebrabadgeprinter/disable/" % (host, port)
    r = requests.put(url)

def enablePrinter():
    url = "http://%s:%d/api/v1/zebrabadgeprinter/enable/" % (host, port)
    r = requests.put(url)

class TestZequsAPI(unittest.TestCase):

    def test_enable(self):
        enablePrinter()
        url = "http://%s:%d/api/v1/zebrabadgeprinter/" % (host, port)
        r = requests.get(url)
        self.assertTrue(r.status_code == 200)
        x = r.json()
        self.assertTrue("enabled" in x)
        self.assertTrue(x["enabled"] == 1)

    def test_disable(self):
        disablePrinter()
        url = "http://%s:%d/api/v1/zebrabadgeprinter/" % (host, port)
        r = requests.get(url)
        self.assertTrue(r.status_code == 200)
        x = r.json()
        self.assertTrue("enabled" in x)
        self.assertTrue(x["enabled"] == 0)

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
        pass

if __name__ == '__main__':
    unittest.main()
