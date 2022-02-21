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

    def fix_rpy():
        import rpy2.rinterface_lib
        # https://github.com/rpy2/rpy2/issues/754
        import rpy2.rinterface_lib
        import rpy2.rinterface_lib.conversion

        def _cchar_to_str(c, encoding: str = 'cp1252') -> str:
            # TODO: use isStrinb and installTrChar
            s = rpy2.rinterface_lib.openrlib.ffi.string(c).decode(encoding)
            return s

        def _cchar_to_str_with_maxlen(c, maxlen: int, _) -> str:
            # TODO: use isStrinb and installTrChar
            s = rpy2.rinterface_lib.openrlib.ffi.string(c, maxlen).decode('cp1252')
            return s
        rpy2.rinterface_lib.conversion._cchar_to_str = _cchar_to_str
        rpy2.rinterface_lib.conversion._cchar_to_str_with_maxlen = _cchar_to_str_with_maxlen

    fix_rpy()

    import rpy2.robjects as robjects
    from rpy2.robjects.packages import importr

    version = [robjects.r['version'].rx('major')[0][0]] + robjects.r['version'].rx('minor')[0][0].split(sep='.')
    #version[1] = version[1].split(sep='.')
    print('R version: {}.{}.{}'.format(version[0], version[1], version[2]))
    # R_LIBS_USE: Documents/R/win-library/4.1
    if platform.system() == 'Windows' and not 'R_LIBS_USER' in os.environ:
        from pathlib import Path
        from os import path
        rhl = path.join(str(Path.home()), 'Documents', 'R', 'win-library', '{}.{}'.format(version[0], version[1]))
        print('R_LIBS_USER <- {}'.format(rhl))
        os.environ['R_LIBS_USER'] = rhl
        Path(rhl).mkdir(parents=True, exist_ok=True)
    #redirect_std()

    try:
        # import rpy2's package module
        import rpy2.robjects.packages as rpackages

        # import R's utility package
        utils = rpackages.importr('utils')

        # select a mirror for R packages
        utils.chooseCRANmirror(ind=1) # select the first mirror in the list
        # R package names
        packnames = ('svglite', )
        # R vector of strings
        from rpy2.robjects.vectors import StrVector
        # Selectively install what needs to be install.
        # We are fancy, just because we can.
        names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
        if len(names_to_install) > 0:
            print('Install required packages: {}.'.format(names_to_install))
            try:
                utils.install_packages(StrVector(names_to_install))
            except:
                print('Installation problems')
    except:
        print('Installation failed?')

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
        q.put(('QUIT',))
        return None
    rpy2.rinterface_lib.callbacks.cleanup = my_cleanup

    grdevices = importr('grDevices')
    svglite = importr('svglite')

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

        #grdevices.svg(file="plot_%03d.svg")
        grdevices.svg(file="plot.svg")
        svgstring = svglite.svgstring(
            width = 5,
            height = 4,
            bg = "transparent",
            pointsize = 10,
            standalone = False,
            scaling = 0.8 )
        svgstring_output = ""

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
            elif 'names' in ret.slots:
                k=0
                #print('slots', [x for x in ret.slots])
                for i in ret.slots['names']: # or do_slot('names')
                    print('slot {}={}'.format(i, ret[k]), end='\r\n')
                    k+=1
            svgstring_output = svgstring()
        except:
            print("r: '{}' => {}".format(code, sys.exc_info()[1]), end='\r\n')
            ret = "error: {}".format(sys.exc_info()[1])

        print(svgstring_output) # array n-elements
        q.put(("{}".format(ret), "{}".format(svgstring_output)))
        #q.put(ret)
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

    def print_body(self, code, ret = "", plots = ""):
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
        self.wfile.write(bytes(f'''<pre>code:</pre><pre id="out" style="border:1px solid blue; padding:1rem;">{ret}\n\n{plots}</pre>''', "utf-8"))
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
        ret, plots = q.get()
        print(ret)
        #print('plots: {}'.format(plots))
        if accept=='text/plain':
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Access-Control-Allow-Origin", origin)
            self.end_headers()
            self.wfile.write(bytes(str(ret), 'utf-8'))
            self.wfile.write(bytes('\n\n', 'utf-8'))
            self.wfile.write(bytes(str(plots), 'utf-8'))
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Access-Control-Allow-Origin", origin)
            self.end_headers()
            self.print_body(code, ret, plots)


if __name__=='__main__':
    #if sys.platform.startswith('win'):
    #    # On Windows calling this function is necessary.
    multiprocessing.freeze_support()

    if platform.system() == 'Windows' and not 'R_HOME' in os.environ:
        from rhome import rhome
        rh = rhome()
        print('R_HOME <- {}'.format(rh))
        os.environ['R_HOME'] = rh

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
