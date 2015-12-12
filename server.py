
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
        self.printerlock = threading.Lock()     
        self.queuelock = threading.Lock()
        self.engine = create_engine('sqlite:////tmp/foo.db', echo=True)
        Base.metadata.create_all(self.engine)

    def worker(self, path, jobid):
        """thread worker function"""
        # for now, simulate successful print
        print 'Worker: %s' % (path)
        self.queuelock.acquire() 
        Session = sessionmaker(bind=self.engine)
        session = Session()
        job = session.query(PrintJob).filter(PrintJob.id == jobid).all()
        if len(job):
            job = job[0]
            job.state = 3
            session.commit()
        self.queuelock.release() 
        self.printerlock.release()
        return

    def iterate(self): 
        self.printerlock.acquire()
        if True:
            self.queuelock.acquire()
            # get next job in database
            Session = sessionmaker(bind=self.engine)
            session = Session()
            job = session.query(PrintJob).filter(PrintJob.state == 0).all()
            if len(job):
                job = job[0]
                t = threading.Thread(target=worker, args=(job.path,job.id,))
                t.start()
                job.state = 1
                session.commit()
                
            # mark job as active and re-write database
            self.queuelock.release()
    
    def queuePrintJob(self, data):
        # obtain queue lock
        self.queuelock.acquire() 
        # add to database, mark as pending get job ID
        Session = sessionmaker(bind=self.engine)
        session = Session()
        # write data to a file
        # path = XXX(data)
        job = PrintJob(path='/tmp/pathofimage', state=0)
        session.add(job)
        session.commit()
        # release queue lock
        self.queuelock.release()
        # return job ID
        return job.id

    def deletePrintJob(self, jobid):
        # obtain queue lock
        self.queuelock.acquire() 
        # find and delete job in database
        Session = sessionmaker(bind=self.engine)
        session = Session()
        job = session.query(PrintJob).filter(PrintJob.id == jobid).all()
        if len(job):
            session.delete(job[0])
            session.commit()
        # release queue lock
        self.queuelock.release()
        return True

    def getJobStatus(self, jobid):
        status = None 
        # obtain queue lock
        self.queuelock.acquire() 
        # find job in database and get status
        Session = sessionmaker(bind=self.engine)
        session = Session()
        job = session.query(PrintJob).filter(PrintJob.id == jobid).all()
        if len(job):
            job = job[0]
            status = {}
            status["id"] = jobid
            status["state"] = job.state
        # release queue lock
        self.queuelock.release()
        return status
 
class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if None != re.search('/api/v1/zebrabadgeprinter/$', self.path):
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'application/json':
                length = int(self.headers.getheader('content-length'))
                data = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)

                data = PrintManager.Instance().QueuePrintJob(data)
                #PrintJobs.records[recordID] = data
                #print "record %s is added successfully" % recordID
            else:
                data = {}
 
            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
        return
 
    def do_DELETE(self):
        if None != re.search('/api/v1/zebrabadgeprinter/[0-9]+/$', self.path):
            jobID = self.path.split('/')[-2]
            PrintManager.Instance().DeletePrintJob(jobId)
            # delete job
            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(400, 'Bad Request: print job does not exist')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
        return
 
    def do_GET(self):
        if None != re.search('/api/v1/zebrabadgeprinter/[0-9]+/$', self.path):
            # get data about a specific print job
            jobID = self.path.split('/')[-2]
            data = PrintManager.Instance.GetJobStatus(jobID)
            if data:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_response(400, 'Bad Request: record does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
        elif None != re.search('/api/v1/zebrabadgeprinter/$', self.path):
            # get status about the printer (state, number of jobs)
            pass
        else:
            self.send_response(400, 'Bad Request: print job does not exist')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
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
 
    def addRecord(self, recordID, jsonEncodedRecord):
        PrintJobs.records[recordID] = jsonEncodedRecord
 
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
