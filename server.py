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

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import threading
import argparse
import re
import cgi
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from time import sleep
import ConfigParser
import os
import sys
from importlib import import_module
from tempfile import mkstemp
import base64

# so far, haven't had luck installing Pillow on Windows 7. 

try:
    from PIL import Image
except:
    pass

# see
# http://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons-in-python

class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

Base = declarative_base()

class PrintJob(Base):
    __tablename__ = 'printjob'

    id = Column(Integer, primary_key=True)
    state = Column(Integer)  # 0=queued, 1=printing, 2=failed, 3=complete
    path = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
       return "<PrintJob(id='%s', path='%s', created_date='%s')>" % (
                          self.id, self.path, self.created_date)

@Singleton
class PrintManager(object):
    def __init__(self):
        self._pluginObj = None
        self.readConfig()
        self.loadPlugin()
        self.printerlock = threading.Lock()     
        self.queuelock = threading.Lock()
        self.engine = create_engine('sqlite:////tmp/zequs.db', echo=False)
        Base.metadata.create_all(self.engine)
        self.enabled = 1 # 1=true, 0=false
        self.testMode = False
        self.thread = threading.Thread(target=self.iterate)
        self.thread.start()

    def readConfig(self):
        try:
            cfg = ConfigParser.ConfigParser()
            cfg.read("/etc/zequs.conf")
            self.plugin_name = cfg.get("plugin", "name")
            try:
                self.spoolonly = cfg.getboolean("printer", "spoolonly")
            except:
                self.spoolonly = False
            try:
                self.spooldir = cfg.get("printer", "spooldir")
            except:
                self.spooldir = None
            try:
                self.rotate = cfg.getint("printer", "rotate")
            except:
                self.rotate = 0
        except:
            print "Unable to open or read /etc/zequs.conf"
            exit()

    def loadPlugin(self):
        try:
            mod = import_module("plugins." + self.plugin_name)
            classattr = getattr(mod, "PrinterPlugin")
            self._pluginObj = classattr()
            
        except:
            e = sys.exc_info()[0]
            print "Unable to load plugin %s: %s" % (self.plugin_name, e)
            exit()

    def worker(self, jobid):
        print "top of worker, have a job to print"
        # print
        self.printerlock.acquire()
        Session = sessionmaker(bind=self.engine)
        session = Session()
        self.queuelock.acquire() 
        job = session.query(PrintJob).filter(PrintJob.id == jobid).all()
        if len(job) and job[0].state == 0:
            job = job[0]
            job.state = 1
            session.commit()
            self.queuelock.release() 
            if self.testMode:
                print "simulating a successful print"
                sleep(10)   # simulate the print
            elif self.spoolonly == False:
                ret = self._pluginObj.printCard(PrintJob.path)
            self.printerlock.release()  # done with the printer
            self.queuelock.acquire()    # update the state of the job
            if self.testMode:
                job.state = 3   # success
            elif self.spoolonly == False:
                job.state = ret
            else:
                job.state = 3   # spooled file, claim success
            session.commit()
            self.queuelock.release() 
        else:
            self.queuelock.release() 
            self.printerlock.release()
        return

    def iterate(self): 
        while True:
            print "top of iterate"
            if not self.enabled: 
                print "printer not enabled"    
                sleep(5)
                continue 
            self.queuelock.acquire()
            # get next job in database
            Session = sessionmaker(bind=self.engine)
            session = Session()
            job = session.query(PrintJob).filter(PrintJob.state == 0).all()
            if len(job):
                job = job[0]
                session.commit()
                # kick of thread to do actual printing
                t = threading.Thread(target=self.worker, args=(job.id,))
                t.start()
                self.queuelock.release()
            else: 
                self.queuelock.release()
                sleep(5)   # nothing to do, sleep a bit

    def enablePrinter(self):
        ret = {}
        self.enabled = 1
        return json.dumps(ret) 

    def disablePrinter(self):
        ret = {}
        self.enabled = 0
        return json.dumps(ret) 

    def setTestMode(self, val):
        self.testMode = val
    
    def queuePrintJob(self, data):
        ret = {}
        # obtain queue lock
        self.queuelock.acquire() 
        # add to database, mark as pending get job ID
        Session = sessionmaker(bind=self.engine)
        session = Session()

        img = base64.decodestring(data)

        fd, temp_path = mkstemp(dir=self.spooldir, suffix=".png")
        f = open(temp_path, "w+")        
        f.write(img)
        f.close()
        os.close(fd)

        # this is lazy and a bit inefficient, but it allows the
        # work to be done without knowing much about the image
        # and can't be any simpler.

        if self.rotate != 0:
            if Image:
                img = Image.open(temp_path)
                img2 = img.rotate(self.rotate)
                img2.save(temp_path)
            else:
                print "Unable to rotate images (Image package missing)"

        job = PrintJob(path=temp_path, state=0)
        session.add(job)
        session.commit()
        # release queue lock
        self.queuelock.release()
        # return job ID
        ret["id"] = job.id
        return json.dumps(ret) 

    def deletePrintJob(self, jobid):
        ret = {}
        # obtain queue lock
        self.queuelock.acquire() 
        # find and delete job in database
        Session = sessionmaker(bind=self.engine)
        session = Session()
        job = session.query(PrintJob).filter(PrintJob.id == jobid).all()
        if len(job):
            if self.spoolonly == False:
                try:
                    os.remove(job[0].path)
                except:
                    pass
            session.delete(job[0])
            session.commit()
        # release queue lock
        self.queuelock.release()
        return json.dumps(ret) 

    # XXX deletePrintJob and deleteAll need some refactoring

    def deleteAll(self):
        ret = {}
        # obtain queue lock
        self.queuelock.acquire() 
        # find and delete job in database
        Session = sessionmaker(bind=self.engine)
        session = Session()
        job = session.query(PrintJob).filter().all()
        for x in job:
            if self.spoolonly == False:
                try:
                    os.remove(job[0].path)
                except:
                    pass
            session.delete(x)
        # release queue lock
        if len(job):
            session.commit()
        self.queuelock.release()
        return json.dumps(ret) 

    def getJobStatus(self, jobid):
        status = {} 
        # obtain queue lock
        self.queuelock.acquire() 
        # find job in database and get status
        Session = sessionmaker(bind=self.engine)
        session = Session()
        job = session.query(PrintJob).filter(PrintJob.id == jobid).all()
        if len(job):
            job = job[0]
            status["id"] = jobid
            status["state"] = job.state
            status = json.dumps(status)
        else:
            status = None
        # release queue lock
        self.queuelock.release()
        return status

    def getPrinterStatus(self):
        status = {}
        # for now, simulate printer is up, report number of jobs
        self.queuelock.acquire() 
        # find job in database and get status
        Session = sessionmaker(bind=self.engine)
        session = Session()
        status["enabled"] = self.enabled
        job = session.query(PrintJob).filter().all()
        status["jobs"] = len(job)
        job = session.query(PrintJob).filter(PrintJob.state==0).all()
        status["queued"] = len(job)
        job = session.query(PrintJob).filter(PrintJob.state==1).all()
        status["printing"] = len(job)
        job = session.query(PrintJob).filter(PrintJob.state==2).all()
        status["failed"] = len(job)
        job = session.query(PrintJob).filter(PrintJob.state==3).all()
        status["complete"] = len(job)
        self.queuelock.release() 
        return json.dumps(status)
 
class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_PUT(self):
        if None != re.search('/api/v1/zequs/enable/$', self.path):
            data = PrintManager.Instance().enablePrinter()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(data)
        elif None != re.search('/api/v1/zequs/testmode/enable/$', self.path):
            data = PrintManager.Instance().setTestMode(True)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(data)
        elif None != re.search('/api/v1/zequs/testmode/disable/$', self.path):
            data = PrintManager.Instance().setTestMode(False)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(data)
        elif None != re.search('/api/v1/zequs/disable/$', self.path):
            data = PrintManager.Instance().disablePrinter()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(data)
        else:
            data = json.dumps({})
            self.send_response(400, 'Bad Request')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(data)
        return

    def do_POST(self):
        if None != re.search('/api/v1/zequs/$', self.path):
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'application/json':
                length = int(self.headers.getheader('content-length'))
                data = json.loads(self.rfile.read(length))
                data = PrintManager.Instance().queuePrintJob(data["data"])
                #PrintJobs.records[recordID] = data
                #print "record %s is added successfully" % recordID
            else:
                data = json.dumps({})
 
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(data)
        else:
            data = json.dumps({})
            self.send_response(400, 'Bad request')
            self.end_headers()
            self.wfile.write(data)
        return
 
    def do_DELETE(self):
        if None != re.search('/api/v1/zequs/[0-9]+/$', self.path):
            jobID = self.path.split('/')[-2]
            data = PrintManager.Instance().deletePrintJob(jobID)
            # delete job
            self.send_response(200)
            self.end_headers()
            self.wfile.write(data)
        elif None != re.search('/api/v1/zequs/$', self.path):
            data = PrintManager.Instance().deleteAll()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(data)
        else:
            data = json.dumps({})
            self.send_response(404, 'Bad Request: print job does not exist')
            self.end_headers()
            self.wfile.write(data)
        return
 
    def do_GET(self):
        if None != re.search('/api/v1/zequs/[0-9]+/$', self.path):
            # get data about a specific print job
            jobID = self.path.split('/')[-2]
            data = PrintManager.Instance().getJobStatus(jobID)
            if data:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(data)
            else:
                data = json.dumps({})
                self.send_response(404, 'job ID does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(data)
        elif None != re.search('/api/v1/zequs/$', self.path):
            data = PrintManager.Instance().getPrinterStatus()
            if data:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(data)
            else:
                data = json.dumps({})
                self.send_response(500, "Internal: can't get printer status")
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(data)
        else:
            data = json.dumps({})
            self.send_response(404, 'Bad Request: print job does not exist')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(data)
        return
 
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
 
    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)
 
class SimpleHttpServer():
    def __init__(self, ip, port):
        self.server = ThreadedHTTPServer((ip,port), HTTPRequestHandler)
 
    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
 
    def waitForThread(self):
        self.server_thread.join()
 
    def stop(self):
        self.server.shutdown()
        self.waitForThread()
 
if __name__=='__main__':
    pm = PrintManager.Instance() # avoid race conditions on first call
    parser = argparse.ArgumentParser(description='HTTP Server')
    parser.add_argument('port', type=int, help='Listening port for HTTP Server')
    parser.add_argument('ip', help='HTTP Server IP')
    args = parser.parse_args()
 
    server = SimpleHttpServer(args.ip, args.port)
    print 'HTTP Server Running...........'
    server.start()
    server.waitForThread()
