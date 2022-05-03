import re
import socket
import logging
import numpy as np
import threading
import webbrowser
import http.server
import socketserver

from gpcharts import figure

from EnlightenPlugin import EnlightenPluginBase,    \
                            EnlightenPluginField,    \
                            EnlightenPluginResponse,  \
                            EnlightenPluginConfiguration

log = logging.getLogger(__name__)

##
# A simple plug-in that spawns a webserver publishing the latest
# spectrum at port 8000.
#
# @todo use settings.eeprom.serial_number to cache latest spectra per connected 
#       spectrometer, so chart can have multiple traces
# @todo frame spectra with WasatchPhotonics logo, product links etc
class HTTPServer(EnlightenPluginBase):

    INITIALIZING = b"""
        <html><head><title>ENLIGHTEN HTTPServer</title></head><body>
        <h1>ENLIGHTEN HTTPServer</h1>
        <p>initializing...</p>
        </body></html>
    """
    PORT = 8000

    ##
    # This is static (a class attribute) because the TCPServer will instantiate
    # new handlers of the given class (MyHandler) on its own, without opportunity
    # for us to pass parameters to them.  Therefore they need to be able to 
    # get the latest rendered chart on their own, with no references or instance
    # handles.  Note this must be in UTF-8 bytes, not a Python string.
    latest_html = None

    def __init__(self):
        super().__init__()
        self.thread = None

    def get_configuration(self):
        fields = []

        fields.append(EnlightenPluginField(
            name="URL", 
            initial=f"http://localhost:{HTTPServer.PORT}", 
            tooltip="Browse here to see spectra"))

        fields.append(EnlightenPluginField(
            name="Refresh",
            direction="input",
            datatype="int",
            initial=5,
            minimum=0,
            maximum=30,
            tooltip="Seconds to auto-refresh (0 to disable)"))

        fields.append(EnlightenPluginField(
            name="Open URL", 
            datatype='button', 
            callback=self.button_callback, 
            tooltip="Click to open URL"))

        return EnlightenPluginConfiguration(
            name = "HTTP Server",
            fields = fields)

    ##
    # @see https://docs.python.org/3/library/socketserver.html
    # @see https://docs.python.org/3/library/http.server.html
    def connect(self, enlighten_info):
        super().connect(enlighten_info)

        self.hostname = socket.gethostname()
        self.ip = socket.gethostbyname(self.hostname)
        log.debug("hostname {self.hostname} has IP {self.ip}")

        HTTPServer.latest_html = HTTPServer.INITIALIZING
        self.httpd = socketserver.TCPServer(("", HTTPServer.PORT), MyHandler)
        self.thread = ServerThread(self.httpd)
        self.thread.start()
        return True

    ## 
    # @see https://github.com/Dfenestrator/GooPyCharts
    # @todo save to EnlightenSpectra/plugins
    def process_request(self, request):
        spectrum    = np.array(request.processed_reading.processed, dtype=np.float32).round(2).tolist()
        wavelengths = np.array(request.settings.wavelengths, dtype=np.float32).round(2)
        refresh     = request.fields["Refresh"]

        fig = figure(title=request.settings.eeprom.serial_number, xlabel='Wavelength (nm)', ylabel='Intensity (counts)')
        fig.plot(wavelengths, spectrum, disp=False)

        html = str(fig)
        if refresh > 0:
            html = re.sub("<head>", f'<head><meta http-equiv="refresh" content="{refresh}"/>', html)
        HTTPServer.latest_html = html.encode("utf-8")

        return EnlightenPluginResponse(request, outputs = { 'URL': self.get_url() })

    def disconnect(self):
        if self.httpd is not None:
            log.debug("closing httpd")
            self.httpd.shutdown()
        self.thread = None 
        super().disconnect()

    def get_url(self):
        if self.httpd is None:
            return f"http://localhost:{HTTPServer.PORT}"
        return f"http://{self.ip}:{HTTPServer.PORT}"

    def button_callback(self):
        url = self.get_url()
        log.debug(f"opening browser to {url}")
        webbrowser.open(url)

class ServerThread(threading.Thread):
    def __init__(self, httpd):
        threading.Thread.__init__(self)
        self.httpd = httpd

    def run(self):
        self.httpd.serve_forever()

##
# This HTTPRequestHandler doesn't care what GET request comes in; it sends the 
# latest Google Chart to the client regardless.
class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    ##
    # @see https://stackoverflow.com/a/7647695/6436775
    # @see https://docs.python.org/3/library/http.server.html#http.server.BaseHTTPRequestHandler.wfile
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        print(self.wfile) # needed?
        self.wfile.write(HTTPServer.latest_html)
        self.wfile.close() # needed?
