# imports
import influxdb
import time
import threading
from requests.exceptions import ConnectionError


class InfluxLogger(threading.Thread):

    def __init__(self, host="localhost", port=443, username='user', password='pwd', database='db', ssl=True, verify_ssl=True, 
                 bufferMaxSize=100000, tSubmit=10):
        threading.Thread.__init__(self)

        # input parameters
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.ssl = ssl
        self.verify_ssl = verify_ssl
        self.bufferMaxSize = bufferMaxSize
        self.tSubmit = tSubmit

        # InfluxDB
        self.client = self.getInfluxClient()

        # Buffer
        self.buffer = []
        self.lock = threading.Lock() # To avoid simultanous access to the buffer variable
        self.tLastSubmit = time.time()
        self.bufferCurrentSize = 0

        # Control thread
        self.goOn = True
        self.start()


    def run(self):
        while self.goOn:
            t = time.time()
            if (t - self.tLastSubmit) > self.tSubmit :
                self.tLastSubmit = t
                self.submit()
                
            time.sleep(.1)
                
    
    def stop(self):
        self.goOn = False


    def now(self):
        return int(time.time()*1e9)
        

    def addPoint(self, measurementName="test", tags={"tagkey1":"tagval1"}, fields={"value1":1.0}, timestamp=None ):

        if timestamp==None:
            timestamp = self.now()

        point = {
            "measurement": measurementName, 
            "tags": tags,
            "fields": fields,
            "time": timestamp
        }

        with self.lock: 
            if self.bufferCurrentSize < self.bufferMaxSize :
                    self.buffer.append(point)
                    self.bufferCurrentSize += 1
            return self.bufferCurrentSize


    def getInfluxClient(self):
        return influxdb.InfluxDBClient(
                self.host, 
                self.port, 
                self.username, 
                self.password, 
                self.database,
                ssl = self.ssl,
                verify_ssl = self.verify_ssl)


    def submit(self):
        
        # Create a copy of the buffer
        with self.lock:
            bufferCopy = self.buffer
            self.buffer = []

        status = 0
        try:
            res = self.client.write_points(bufferCopy,batch_size=5000)
        except influxdb.exceptions.InfluxDBServerError as e:
            status = 1
            # 502 Bad gateway (Influx server down behind proxy)
            pass
        except influxdb.exceptions.InfluxDBClientError as e:
            status = 2
            # 400 partial write (wrong data type)
            # 401 authorization failed
            # 403 wrong permissions
            # 404 database not found
            # 413 Request Entity Too Large
        except ConnectionError as e:
            status = 3
            # server down
            # wrong URL
            # No network connection available
        except:
            status = 4
        
        with self.lock:
            if (status == 1 or status == 3):
                # restore data
                self.buffer = self.buffer + bufferCopy
            else:
                self.bufferCurrentSize -= len(bufferCopy)


