import unittest
import requests

# The following assumes zequs service is running on localhost and 
# listening on port 8081. Change host and port variables as needed
# below if this assumption is false

host = "127.0.0.1"
port = 8081

class TestZequsAPI(unittest.TestCase):

    def test_queryprinter(self):
        url = "http://%s:%d/api/v1/zebrabadgeprinter/" % (host, port)
        r = requests.get(url)
        self.assertTrue(r.status_code == 200)
        x = r.json()
        self.assertTrue("status" in x)
        self.assertTrue("jobs" in x)
        self.assertTrue("queued" in x)
        self.assertTrue("printing" in x)
        self.assertTrue("failed" in x)
        self.assertTrue("complete" in x)

if __name__ == '__main__':
    unittest.main()
