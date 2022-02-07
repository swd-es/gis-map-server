###############################################################################
# (c) 2011-2022, SWD Embedded Systems Limited, http://www.kpda.ru
###############################################################################

#!/usr/bin/python3 -uB
from net_interface import Net_Interface
from scheduler import Scheduler
from storage import Storage
from utils import get_log_path

import argparse
import shutil
import os
import sys
import time
from multiprocessing import Process, Pipe
import subprocess

class Server:    
    """ 
    A class used to represent gis-map-server instance consisting of instances of Interface_Class, Storage_Class and Scheduler_Class classes.
    
    Attributes:
    __________
    host : str
        IP adress or host name for the net interface module.
    port : int
        Connection port for the net interface module.
    buf_size : int
        Maximum buffer size in bytes.
    slots_num : int
        A total number of available slots.
    html_path : str
        The path to a folder with html pages that are used to responde clients.

    Methods:
    ________
    server_init(Interface_Class, Storage_Class,  Scheduler_Class)
        Initializes server with instances of Interface_Class, Storage_Class and Scheduler_Class classes.
    start()
        Starts server execution: executes scheduler as a subprocess, executes Interface_Class listening. 
    """
    
    def __init__(self, host, port, slots_num, buf_size, html_path, sharedMemoryId):
        """ 
        Parameters:
        __________
        host : str
            IP adress or host name for the net interface module.
        port : int
            Connection port for the net interface module.
        buf_size : int
            Maximum buffer size in bytes.
        slots_num : int
            A total number of available slots.
        html_path : str
            The path to a folder with html pages that are used to responde clients.
        """
        self.port = port
        self.host = host
        self.buf_size = buf_size
        self.slots_num = slots_num
        self.html_path = html_path
        self.sharedMemoryId = sharedMemoryId
        
    def server_init(self, Interface_Class, Storage_Class,  Scheduler_Class):
        """ Initializes server with instances of Interface_Class, Storage_Class and Scheduler_Class classes. 
        
        Parameters:
        __________
        Interface_Class : class
            A class link to create net_interface.
        Storage_Class : class
            A class link to create storage.
        Scheduler_Class : class
            A class link to create scheduler.
        """
        self.net_interface = Interface_Class(self.host, self.port)
        self.buf_storage = Storage_Class(self.buf_size)
        self.scheduler = Scheduler_Class()
    
    def start(self):
        """ Starts server execution: executes scheduler as a subprocess, executes Interface_Class listening. Creates Pipe between two processes."""
        sched_conn, serv_conn = Pipe()
        sched = Process(target=self.scheduler.start_scheduler, args=(sched_conn, self.host, self.port, self.slots_num, self.sharedMemoryId))
        sched.start()
        
        # Net_Interface start with access to Buf_Storage and Scheduler
        self.net_interface.start_server(serv_conn, self.buf_storage, self.html_path)

def parse_args():
    """ Function for parsing program arguments """
    parser = argparse.ArgumentParser(description='gis-map-server description:')
    parser.add_argument('config_path', type=str,
                help='a required string positional argument, path to gis-map-server config')
    args = parser.parse_args()
    return args

def parse_config(path):
    """ Function parses config and return values of required options """
    with open(path) as f:
        content = f.readlines()
    options = dict()
    for line in content:
        key, val = line.split('=')
        options[key] = val.strip()
    return options['SERVER_ADDRESS'], int(options['SERVER_PORT']), int(options['SLOTS_NUMBER']), int(options['STORAGE_MAX_SIZE']), options['HTML_PAGES_PATH'], options['GIS_SHID']


if __name__ == '__main__':
    try:
        args = parse_args()
    except Exception as exp:
        print(f"Arguments parsing error: {exp}")
        sys.exit(1)
    
    try:
        address, port, slots_num, buf_size, html_path, sharedMemoryId = parse_config(args.config_path)
    except Exception as exp:
        print(f"Config parsing error {exp}")
        sys.exit(1)
    
    # log folder (re)creating
    log_path = get_log_path()
    if log_path == None:
        print("Could not find GIS_ROOT environment variable")
        sys.exit(1)
        
    try:
        shutil.rmtree(log_path)
    except FileNotFoundError:
        pass
    except Exception as exc:
        print("Could not get an access to log folder", log_path, exc)
        sys.exit(1)
        
    try:
        os.mkdir(log_path)
    except Exception as exc:
        print("Could not create log folder", log_path, exc)
        sys.exit(1)
    
    try:
        subprocess.run(["gis-control", f'-s{sharedMemoryId}'])
    except Exception as exc:
        print("Could not make data request for sharedMemoryId", sharedMemoryId, exc)
        sys.exit(1)
    
    # starting the server
    try:
        new_server = Server(address, port, slots_num, buf_size, os.environ['GIS_ROOT'] + '/' + html_path, sharedMemoryId) 
        new_server.server_init(Net_Interface, Storage, Scheduler)
        new_server.start()
    except KeyboardInterrupt:
        print('Server is closed')
        sys.exit(0)
