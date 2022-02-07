###############################################################################
# (c) 2011-2022, SWD Embedded Systems Limited, http://www.kpda.ru
###############################################################################

#!/usr/bin/python3 -u
import http.server, ssl
import logging
import sys
import os
import re
from enum import Enum, unique
from utils import Request_Status, get_log_path, get_status_desc

@unique
class Page_Type(Enum):
    START = 0
    ORDER_REQUEST = 1
    BAD_REQUEST = 2

class Handler(http.server.BaseHTTPRequestHandler):
    """ 
    A class for http-requests handling. Instance's lifetime is limited by the time of request processing.  
    
    Attributes:
    __________
    pipe_conn : multiprocessing.connection.Connection
        Pipe connection instance for interacting with Scheduler.
    buffer : Storage_Class instance
        Buffer is used to store data from POST-requests obtained by Renderer.
    html_path : str
        The path to a folder with html pages that are used to responde clients.
    
    Methods:
    ________
    get_html_content(page_type)
        Obtains the content of html page of specified type and returns it as a string.
    do_POST()
        Handles POST requests.
    do_GET()
        Handles GET requests.
    bad_request(code, exc="")
        Inserts a error message obtained by code and prints an html-page into wfile. Also supports printing an exception string.
    clear_pipe()
        Obtains all possible data from Pipe connection if it exists.
    """
    
    def __init__(self, pipe_conn, buffer, html_path, *args):
        """ 
        Parameters:
        __________
        pipe_conn : multiprocessing.connection.Connection
            Pipe connection instance for interacting with Scheduler.
        buffer : Storage_Class instance
            Buffer is used to store data from POST-requests obtained by Renderer.
        html_path : str
            The path to a folder with html pages that are used to responde clients.
        """
        self.pipe_conn = pipe_conn
        self.buffer = buffer
        self.html_path = html_path
        http.server.BaseHTTPRequestHandler.__init__(self, *args)
    
    def get_html_content(self, page_type):
        """Obtains the content of html page of specified type and returns it as a string.
        
        Parameters:
        __________
        page_type : Page_Type Enum instance
            Type of page which should be read.
            
        Returns
        -------
        str
            Content of html page
        """
        if page_type == Page_Type.START.value:
            with open(self.html_path + '/start_page.html') as f:
                content = f.read()
            content = content.replace('ADDRESS', str(self.server.server_name))
            content = content.replace('PORT', str(self.server.server_port))
            return content
        elif page_type == Page_Type.ORDER_REQUEST.value:
            with open(self.html_path + '/order_request.html') as f:
                content = f.read()
            content = content.replace('ADDRESS', str(self.server.server_name))
            content = content.replace('PORT', str(self.server.server_port))
            return content
        else:
            return 'BadPage'

    def do_POST(self):
        """ Handles POST requests. """
        try:
            # trying to get payload
            logging.debug('Got POST-request')
            length = int(self.headers['Content-Length'])
            logging.debug('Got length')
            orderId = int(self.headers['orderId'])
            logging.debug('Got orderId')
            img_format = self.headers['Content-Type']
            logging.debug('Got img_format')
            payload = self.rfile.read(length)
            logging.debug('Got payload')
            
            status_code, deleted_ids = self.buffer.push(orderId, payload, img_format, length)
            
            #sending information to scheduler
            self.clear_pipe()
            self.pipe_conn.send((2, deleted_ids))
            if self.pipe_conn.poll(1):
                logging.debug('net_interface: got answer from scheduler')
                answer = self.pipe_conn.recv()
                if answer == False:
                    self.bad_request(Request_Status.REQUEST_FAILED.value, "Scheduler could not delete previous ids from table")
            else:
                self.bad_request(Request_Status.TIMEOUT.value, "Scheduler did not responde")
            
            if status_code == Request_Status.READY.value:
                logging.debug('Push success')
                self.send_response(Request_Status.READY.value, "Got payload")
                self.end_headers()
                self.wfile.write('Accepted'.encode())
            else:
                logging.debug('Error while pushing {status_code}')
                self.bad_request(status_code, "Id is busy")

        except Exception as exc:
            try:
                self.bad_request(Request_Status.INVALID_PARAM.value, exc)
            except Exception as exc:
                logging.debug(f"Bad connection with client {exc}")
            
    def bad_request(self, code, exc=""):
        """ Prints an html-page with error code into wfile and inserts there an error message obtained by code. Also supports printing an exception string.
        
        Parameters:
        __________
        code : Request_Status Enum instance
            An error code to print.A string of thrown exception to print.
        exc : str
            A string of thrown exception to print.
        """
        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write('<html><head><meta charset="utf-8">'.encode())
        self.wfile.write('<title>Bad request</title></head>'.encode())
        self.wfile.write(f'<body><p>Bad request: {code}:{get_status_desc(code)} {exc}</p></body></html>'.encode())
        logging.debug('requested')

    def clear_pipe(self):
        """ Obtains all possible data from Pipe connection if it exists. """
        while True:
            logging.debug('clear pipe start')
            if self.pipe_conn.poll():
                self.pipe_conn.recv()
                continue
            logging.debug('clear pipe finish')
            break
    
    def do_GET(self):
        """ Handles POST requests. """  
        try:
            #analyzing agent
            try:
                if 'gis' in dict(self.headers)['agent']:
                    logging.debug('Agent: GIS')
                    gis_agent = True
            except:
                logging.debug('Agent: Unknown')
                gis_agent = False
            
            # analyzing of parameters
            fields = dict()
            param_line = re.sub('/[?]*[&]*', '', self.path)

            if '&' in param_line:
                for p in param_line.split('&'):
                    print(p.split('='))
                    key, val = p.split('=')
                    fields[key] = val
            logging.debug(f"I've got a GET request, fields = {fields} from {self.path}")
            
            if len(fields) == 0:
                # start page request
                answer = self.get_html_content(Page_Type.START.value)
                self.send_response(Request_Status.READY.value)
                self.send_header("Content-type", "text/html")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(answer.encode())
            
            elif 'orderId' not in fields:
                # first type of GET-request
                
                #sending to scheduler new order
                self.clear_pipe()
                self.pipe_conn.send((0, fields))
                
                # obtaining id from scheduler
                if self.pipe_conn.poll(1):
                    logging.debug('net_interface: got from scheduler')
                    container = self.pipe_conn.recv()
                    logging.debug(f'OBTAINED {container}')
                    id_pin, is_valid = container
                    orderId, pincode = id_pin
                    logging.debug(f'net_interface: got from scheduler {orderId}, {is_valid}, {pincode}')
                    if is_valid:
                        self.send_response(Request_Status.READY.value)
                        logging.debug('net_interface: 0')
                        self.send_header("Content-type", "text/html")
                        self.send_header("Access-Control-Allow-Origin", "*")
                        logging.debug('net_interface: 1')
                        self.end_headers()
                        logging.debug('net_interface: 2')
                        if gis_agent:
                            logging.debug('net_interface: 3')
                            self.wfile.write(f'orderId={orderId}, pincode={pincode}'.encode())
                        else:
                            logging.debug('net_interface: 4')
                            answer = self.get_html_content(Page_Type.ORDER_REQUEST.value)
                            answer = answer.replace('ORDERID', str(orderId))
                            answer = answer.replace('PIN_CODE', pincode)
                            self.wfile.write(answer.encode())
                    else:
                        # internal error, bad request params
                        self.bad_request(Request_Status.INVALID_PARAM.value)
                else:
                    # timeout error 
                    self.bad_request(Request_Status.TIMEOUT.value)
                
                
            else:
                # second type of GET-request
                if 'pincode' not in fields:
                    self.bad_request(Request_Status.INVALID_PARAM.value)
                else:
                    # asking scheduler about status of order
                    orderId = int(fields['orderId'])
                    pincode = fields['pincode']
                    self.clear_pipe()
                    self.pipe_conn.send((1, (orderId, pincode)))
                    
                    # obtaining id from scheduler
                    if self.pipe_conn.poll(2):
                        status = self.pipe_conn.recv()
                        if status == Request_Status.READY.value:
                            output_data, img_format = self.buffer.pop_by_id(orderId)
                            self.send_response(Request_Status.READY.value)
                            self.send_header("Content-type", img_format)
                            self.send_header("Access-Control-Allow-Origin", "*")
                            self.end_headers()
                            self.wfile.write(output_data)
                        else:
                            logging.debug(f'status: {status}')
                            self.bad_request(status)
                    else:
                        self.bad_request(Request_Status.TIMEOUT.value)
                                
        except Exception as exc:
            logging.debug("Error! {0}".format(exc))
            self.bad_request(Request_Status.REQUEST_FAILED.value, exc)

class Net_Interface():
    """ 
    A class to provide net-interface of map-server. For now it start http server.
    
    Attributes:
    __________
    host : str
        IP adress or host name for the net interface module.
    port : int
        Connection port for the net interface module.
    
    Methods:
    ________
    init_logging(page_type)
        Starts logging to the file, obtained by get_log_path.
    start_server()
        Starts http server using Handler class for requests handling.
    """
    
    def __init__(self, host, port):
        """ 
        Parameters:
        __________
        host : str
            IP adress or host name for the net interface module.
        port : int
            Connection port for the net interface module.
        """
        self.port = port
        self.host = host
        self.init_logging()
        
    def init_logging(self):
        """ Starts logging to the file, obtained by get_log_path. """
        log_path = get_log_path()
        if log_path == None:
            logging.debug("Could not find GIS_ROOT environment variable")
            sys.exit(1)
            
        log_path += '/server.log'
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', filename=log_path, encoding='utf-8', level=logging.DEBUG)

    def start_server(self, pipe_conn, buffer, html_path):
        """ Starts http server using Handler class for requests handling. 
        
        Parameters:
        __________
        pipe_conn : multiprocessing.connection.Connection
            Pipe connection instance for interacting with Scheduler.
        buffer : Storage_Class instance
            Buffer is used to store data from POST-requests obtained by Renderer.
        html_path : str
            The path to a folder with html pages that are used to responde clients.
        """
        def handler(*args):
            Handler(pipe_conn, buffer, html_path, *args)

        self.net_server = http.server.HTTPServer((self.host, self.port), handler)
        logging.debug('net_server Started')
        self.net_server.serve_forever()
