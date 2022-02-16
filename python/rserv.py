import threading
import time, os, subprocess

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from time import sleep
import cgi
import sys, signal
import readchar
import platform

#import rpy2.robjects
#.robjects as robjects
# r = robjects.r
#robjects = rpy2.robjects





#grdevices.png(file="path/to/file.png", width=512, height=512)
#grdevices.png(file="path/to/file.png", width=512, height=512)
#grdevices.svg(file="plot_%03d.svg")
# plotting code here
#grdevices.dev_off()

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

import multiprocessing

from multiprocessing import Process, Queue


def test2(q):
    import rpy2.robjects as robjects
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

#from redirect import redirect_std

class CustomProcess(Process):
    def run(self, *args, **kwargs):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return Process.run(self, *args, **kwargs)

# print('  -------   ')
def rlang_proc(q):
    import rpy2
    import rpy2.rinterface_lib
    import rpy2.robjects as robjects
    from rpy2.robjects.packages import importr
    #redirect_std()
    print('rlang initialized, waiting for jobs...', end='\r\n')
    # import warnings
    # warnings.warn('TEST')
    def  my_consoleread(prompt: str) -> str:
        custom_prompt = '???' + prompt
        return 'c'
        #return input(custom_prompt)

    rpy2.rinterface_lib.callbacks.consoleread = my_consoleread

    #buf = []
    def f(x):
        # function that append its argument to the list 'buf'
        print('> {}'.format(x), end='\r\n')
        #buf.append(x)

    # output from the R console will now be appended to the list 'buf'
    #consolewrite_print_backup = rpy2.rinterface_lib.callbacks.consolewrite_print
    rpy2.rinterface_lib.callbacks.consolewrite_print = f
    rpy2.rinterface_lib.callbacks.consolewrite_warnerror = f

    #date = rinterface.baseenv['date']
    #rprint = rinterface.baseenv['print']
    #rprint(date())

    # the output is in our list (as defined in the function f above)
    #print(buf)

    # restore default function
    # rpy2.rinterface_lib.callbacks.consolewrite_print = consolewrite_print_backup

    #rpy2.rinterface.initr()

    import rpy2.rinterface as ri

    @ri.rternalize
    def quit(v):
        return 0

    def my_cleanup(saveact, status, runlast):
        # cancel all attempts to quit R programmatically
        print("No one can't escape...")
        q.put('QUIT')
        return None
    rpy2.rinterface_lib.callbacks.cleanup = my_cleanup

    grdevices = importr('grDevices')
    sys.stdout.flush()
    while True:
        robjects.globalenv.clear()
        robjects.globalenv['quit'] = quit
        robjects.globalenv['q'] = quit
        try:
            code,data=q.get()
        except:
            print("queue error: {}".format(sys.exc_info()[1]), end='\r\n')
            # q.put('')
            continue

        grdevices.svg(file="plot_%03d.svg")
        try:
            if data:
                # f=robjects.FloatVector([1, 2, 3])
                # robjects.DataFrame({"a": f, "b": f})
                robjects.globalenv['d'] = robjects.r(data)

            ret = robjects.r(code)
            print('ret={}'.format(ret), end='\r\n')
            #if not ret:
            if type(ret) == rpy2.rinterface_lib.sexp.NULLType:
                ret = '{}'.format(ret) #??? rpy2.rinterface_lib.sexp.NULLType
            elif len(ret.slots):
                k=0
                for i in ret.slots['names']: # or do_slot('names')
                    print('slot {}={}'.format(i, ret[k]), end='\r\n')
                    k+=1
        except:
            print("r: '{}' => {}".format(code, sys.exc_info()[1]), end='\r\n')
            ret = "error: {}".format(sys.exc_info()[1])
        q.put(ret)
        print("env={}".format( [x for x in robjects.globalenv] ))
        #try:
        grdevices.dev_off()
        sys.stdout.flush()
        #except:
        #    print("{}".format(sys.exc_info()[1]))


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
        print(self.path)
        print(self.headers.get('Accept'))
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.print_body("pi")

    def print_body(self, code, ret = ""):
        self.wfile.write(bytes("<html><body><h1>Rserv 0.5</h1>", "utf-8"))
        self.wfile.write(bytes(f"""
        <style>
            body {{ font-family: monospace; }}
            * {{ padding: 0.5rem; }}
            input {{ width: 100% }}
        </style>
        <form action="/r" method="POST">
        <div>
            <label for="data">Data:</label><br>
            <textarea name="data" id="data" size=30 rows="2" cols="80" style="padding: 1rem; width: 100%; resize: vertical; min-height:2rem; max-height:100rem;">c(0,1,2,3,4,5,6,7,8,9)</textarea><br>
            <label for="code">Code:</label><br>
            <textarea autofocus name="code" id="code" value="{code}" rows="10" cols="80" style="padding: 1rem; width: 100%; resize: vertical; min-height:3rem; max-height:100rem;">{code}</textarea>
        </div>
        <div>
            <button>Run code &gt;</button>
        </div>
        </form>
        <script>
            const c = document.getElementById('code');

            const sub_cb = function(e) {{
                var out = document.getElementById("out"),
                    data = new FormData(form);

                //data.set("code", "2");

                fetch('/r', {{
                    method: 'POST',
                    headers: {{
                        'Accept': 'text/plain'
                    }},
                    body: data,
                }})
                .then(response => response.text())
                .then(result => {{
                    //console.log('Success:', result);
                    out.innerHTML = result;
                }})
                .catch(error => {{
                    console.error('Error:', error);
                    out.innerHTML = 'Error: ' + error;
                }});
                e.preventDefault();
            }}

            document.addEventListener('keydown', e => {{ if (e.code=='Enter' && e.shiftKey) {{
                    //document.forms[0].submit();
                    sub_cb(e);
                    e.preventDefault();
                    e.stopPropagation();
                }}
            }} );

            var form = document.forms[0];
            form.addEventListener('submit', e => sub_cb(e), false);

            //c.focus()
        </script>""", "utf-8"))
        self.wfile.write(bytes(f'''<pre>code:</pre><pre id="out" style="border:1px solid blue; padding:1rem;">{ret}</pre>''', "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

    def do_POST(self):
        print(self.path)
        print('headers: {}'.format(self.headers))
        accept=self.headers.get('Accept')

        origin=str(self.headers.get('Origin'))
        if self.headers.get('Sec-Fetch-Mode') != 'cors' or not origin.startswith('http://127.0.0.1'):
            self.send_response(400)
            self.send_header("Content-type", "text/plain")
            self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1")
            self.end_headers()
            self.wfile.write(bytes("", 'utf-8'))
            return
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            data = form.getvalue("data")
            code = form.getvalue("code")
            print(f'''data: {data}\ncode: {code}''')
        except:
            print(sys.exc_info()[1])
        if code == None: code = ''
        if data == None: data = ''
        code=code.replace('\r', '')
        data=data.replace('\r', '')
        q.put((code, data))
        ret = q.get()
        print(ret)

        if accept=='text/plain':
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Access-Control-Allow-Origin", origin)
            self.end_headers()
            self.wfile.write(bytes(str(ret), 'utf-8'))
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Access-Control-Allow-Origin", origin)
            self.end_headers()
            self.print_body(code, ret)


if __name__=='__main__':
    #if sys.platform.startswith('win'):
    #    # On Windows calling this function is necessary.
    multiprocessing.freeze_support()

    if platform.system() == 'Windows' and not 'R_HOME' in os.environ:
        rhome = subprocess.check_output(['R', 'RHOME'], shell=False, stderr=subprocess.PIPE)
        print('R_HOME <- %s' % (rhome.decode('UTF-8')))
        os.environ['R_HOME'] = rhome.decode('UTF-8')

    q = Queue()
    p = Process(target=rlang_proc, args=(q,))
    p.start()

    #multiprocessing.set_start_method('spawn')

    webServer = WebServer()
    def sigterm(a, b):
        print('sigterm')
        webServer.shutdown()
        p.join(timeout = 1)
        p.terminate()
        time.sleep(1)
        sys.exit(0)

    signal.signal(signal.SIGTERM, sigterm)
    signal.signal(signal.SIGINT, sigterm)

    webServer.start()

    while webServer.running:
        if platform.system() != 'Darwin':
            r = readchar.readchar()
            if type(r) is bytes: r = r.decode()
            #r='o'
            if r == 'q' or r == '\x03':
                # print('quit')
                webServer.shutdown()
                p.join(timeout = 1)
                p.terminate()
        try:
            sleep(0.1)
            #print('.')
        except KeyboardInterrupt:
            print('Ctrl+C')
            webServer.shutdown()
            p.join(timeout = 1)
            p.terminate()

        #print('Keyboard Interrupt sent.')
        #webServer.shutdown()
        #exit(0)
