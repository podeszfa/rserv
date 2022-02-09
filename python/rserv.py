from logging import shutdown
import threading
import time, os, subprocess

from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from time import sleep
import cgi
import sys, signal
import readchar


#import rpy2.robjects
#.robjects as robjects
# r = robjects.r
#robjects = rpy2.robjects
if not 'R_HOME' in os.environ:
    rhome = subprocess.check_output(['r', 'RHOME'], shell=False, stderr=subprocess.PIPE)
    print('R_HOME <- %s' % (rhome.decode('UTF-8')))
    os.environ['R_HOME'] = rhome.decode('UTF-8')

import rpy2.robjects as robjects

# def threadFunc():
#     x = robjects.IntVector(range(10))
#     y = robjects.r.rnorm(10)
#     for i in range(100):
#         print(f'Hello from new Thread {x} {y}')
#         time.sleep(1)
#     webServer.shutdown()
#     sys.exit(0)
# th = threading.Thread(target=threadFunc, daemon=True)
# th.start()

from multiprocessing import Process, Queue


def test2(q):
    x = robjects.r('rt(1,1)\n')
    print(x)
    x = robjects.r('''
        rt(1,1)
        library('dfphase1')
        set.seed(12345)
        y <- matrix(rt(100,3),5)
        y[,20] <- y[,20]+3
        y[,2] <- y[,2]-2
        shewhart(y)
        #plot(cars)
        #quit("no")
''')
    time.sleep(15)

def rlang_proc(q):
    while True:
        code=q.get()
        try:
            ret = robjects.r(code)
            print('ret={}'.format(ret))
        except:
            print("r: '{}' => {}".format(code, sys.exc_info()[1]))
            ret = "???"
        q.put(ret)

q = Queue()
p = Process(target=rlang_proc, args=(q,))

#test2()
#th = threading.Thread(target=test2, daemon=True)
#th.start()

class WebServer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.host = "127.0.0.1"
        self.port = 8080
        self.ws = ThreadingHTTPServer((self.host, self.port), MyHandler)

    def run(self):
        print("WebServer started at Port:", self.port)
        self.ws.serve_forever()

    def shutdown(self):
        # set the two flags needed to shutdown the HTTP server manually
        self.ws._BaseServer__is_shut_down.set()
        self.ws.__shutdown_request = True
        print('Shutting down server.')
        # call it anyway, for good measure...
        self.ws.shutdown()
        print('Closing server.')
        self.ws.server_close()
        print('Closing thread.')
        self.join(timeout=3)
        print('Closed thread.')
        self.running = False



class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/favicon.ico':
            self.send_response(404)
            self.send_header("Content-type", "image/x-icon")
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.print_body("pi")

    def print_body(self, code, ret = ""):
        self.wfile.write(bytes("<html><body><h1>POST Request Received!</h1>", "utf-8"))
        self.wfile.write(bytes(f"""
        <form action="/r" method="POST">
        <div>
            <label for="code">Code:</label><br>
            <textarea name="code" id="code" value="{code}" rows="10" cols="80" style="padding: 1rem; width: 100%; resize: vertical; min-height:3rem; max-height:100rem;">{code}</textarea>
        </div>
        <div>
            <button>Run code</button>
        </div>
        </form>""", "utf-8"))
        self.wfile.write(bytes(f'''<pre>code:</pre><pre style="border:1px solid blue; padding:1rem;">{ret}</pre>''', "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

    def do_POST(self):
        try:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            print(form.getvalue("code"))
            code = form.getvalue("code")
        except:
            print(sys.exc_info()[1])
        code=code.replace('\r', '')
        q.put(code)
        ret = q.get()
        print(ret)

        self.print_body(code, ret)


def sigterm(a, b):
    webServer.shutdown()
    p.join(timeout = 1)
    p.terminate()
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm)
signal.signal(signal.SIGINT, sigterm)


if __name__=='__main__':
    webServer = WebServer()
    webServer.start()

    p.start()
    while webServer.running:
        r = readchar.readchar()
        print(r)
        if r == b'q' or r == b'\x03':
            webServer.shutdown()
            p.join(timeout = 1)
            p.terminate()
        try:
            sleep(0.1)
            print('.')
        except KeyboardInterrupt:
            print('Ctrl+C')
            webServer.shutdown()

        #print('Keyboard Interrupt sent.')
        #webServer.shutdown()
        #exit(0)