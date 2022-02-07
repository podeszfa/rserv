import threading
import time

from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from time import sleep
import cgi
import sys, signal

class WebServer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.host = "localhost"
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
        self.join()


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Title</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("""
<form action="/post" method="POST">
  <div>
    <label for="code">What code to say?</label>
    <input name="code" id="code" value="pi">
  </div>
  <div>
    <button>Send code</button>
  </div>
</form>""", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
        print(self.path)

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
            self.wfile.write("<html><body><h1>POST Request Received!</h1></body></html>")
        except:
            print(sys.exc_info()[1])


def sigterm(a, b):
    print('KILL')
    webServer.shutdown()
    print('K2')
    sys.exit(0)


if __name__=='__main__':
    signal.signal(signal.SIGTERM, sigterm)
    signal.signal(signal.SIGINT, sigterm)
    webServer = WebServer()
    webServer.start()
    while True:
        try:
            sleep(1)
        except KeyboardInterrupt:
            pass

        #print('Keyboard Interrupt sent.')
        #webServer.shutdown()
        #exit(0)