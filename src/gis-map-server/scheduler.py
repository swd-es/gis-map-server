###############################################################################
# (c) 2011-2022, SWD Embedded Systems Limited, http://www.kpda.ru
###############################################################################

#!/usr/bin/python3 -u -B
import time
import os
import logging
import subprocess
import string
import random

from utils import Request_Status, get_log_path


class Worker():
    """ 
    A class for organizing the parallel execution of any processes with required number of slots.
    
    Attributes:
    __________
    slots_num : int
        A total number of available slots.
    slots : array
        An array of processes. 
    size : int
        Current number of executing processes.
    
    Methods:
    ________
    fill_slot(page_type)
        Adds new process to the array. 
    free_slot(num)
        Removes a process from slot with index = num.
    check_free_slot()
        Checks if there is at least one free slot in processes array.
    is_busy()
        Checks if there is at least one active process.
    active_slots()
        Returns a list of elements and its indexes from processes array if they are active.
    """
    
    def __init__(self, slots_num):
        """ 
        Parameters:
        __________
        slots_num : int
            A total number of available slots.
        """
        self.slots_num = slots_num
        self.slots = [0] * self.slots_num
        self.size = 0
        
    def fill_slot(self, element):
        """ Adds new process to the array. 
        This function has to be called only after cheking free slot with "check_free_slot".
        
        Parameters:
        __________
        element : any type
            New element to be add into the processes array.
        """
        logging.debug(f'{self.slots}')
        for i in range(self.slots_num):
            if self.slots[i] == 0:
                self.slots[i] = element
                self.size += 1
                return
        raise IndexError
    
    def free_slot(self, num):
        """ Removes a process from slot with index = num.
        
        Parameters:
        __________
        num : int
            Index of removed slot.
        """
        self.slots[num] = 0
        self.size -= 1
        
    def check_free_slot(self):
        """ Checks if there is at least one free slot in processes array. """
        if self.size < self.slots_num:
            return True
        return False
        
    def is_busy(self):
        """ Checks if there is at least one active process. """
        if self.size > 0:
            return True
        return False
    
    def active_slots(self):
        """ Returns a list of elements and its indexes from processes array if they are active. """
        return [ (self.slots[i], i) for i in range(self.slots_num) if self.slots[i] != 0]

class Scheduler():
    """ 
    A class for organizing orders execution, id and pin codes generation, saving orders return codes, orders validating.
    
    Attributes:
    __________
    orders : dict
        A dictionary of all oders. Key: id, value: [parameters, return codes, pincode]
    queue : list
        A queue with new orders that have not been executed.
    counter : int
        Total number of orders.
    
    Methods:
    ________
    validator(params)
        Validates parameters of an order.
    generate_pincode(dictionary, size)
        Generates new pincode of length = size, using characters from dictionary string.
    add_order(params)
        Adds new order with parameters = params to orders and queue.
    check_order(id)
        Checks if order with id exists.
    start_scheduler(pipe_conn, host, port, slots_num)
        Executes scheduler, starts an infinite loop for listening pipe connection = pipe_conn and organizing orders execution.
        
    """
    
    def __init__(self):
        self.orders = dict()
        self.cached = dict()
        self.queue = list()
        self.counter = 0
        
    def validator(self, params):
        """ Validates parameters of an order.
        
        Parameters:
        __________
        params : list
            A list of parameters for validating.
        """
        params_list = ['lat', 'lon', 'scale', 'w', 'h', 'format']
        for par in params_list:
            if par not in params:
                logging.debug(f'Bad params: no {par} in {params}')
                return False
        try:
            float(params['lon'])
            float(params['lat'])
        except ValueError:
            logging.debug(f'Bad params: lat, lan, w, h or scale is not float in {params}')
            return False
        
        if not params['scale'].isdigit() or not params['w'].isdigit() or not params['h'].isdigit():
            return False
        
        return True
    
    def generate_pincode(self, dictionary, size):
        """ Generates new pincode of length = size, using characters from dictionary string.
        
        Parameters:
        __________
        dictionary : str
            A string with characters that is used as a dictionary for pincode creating.
        size : int
            A number of characters in picode.
        
        Returns
        -------
        pincode
            Generated pincode
        """
        pincode = ''.join(random.choice(dictionary) for x in range(size))
        return pincode

    def add_order(self, params):
        """ Adds new order with parameters = params to orders and queue.
        
        Parameters:
        __________
        params : list
            A list of parameters of a new order.
            
                    
        Returns
        -------
        id
            Id for new order, equal to self.counter value
        pincode
            Generated pincode for new order
        """
        self.counter += 1
        pincode = self.generate_pincode(string.digits + string.ascii_letters, 6)
        self.orders[self.counter] = [params, Request_Status.PROCESSING.value, pincode]
        
        self.cached[tuple(params.values())] = self.counter
        self.queue.append(self.counter)
        return self.counter, pincode

    def check_order(self, id):
        """ Checks if order with id exists. """
        return id in self.orders


    def start_scheduler(self, pipe_conn, host, port, slots_num, sharedMemoryId):
        """ Executes scheduler, starts an infinite loop for listening pipe connection = pipe_conn and organizing orders execution. 
        
        Parameters:
        __________
        pipe_conn : multiprocessing.connection.Connection
            Pipe connection instance for interacting with Net_Interface.
        host : str
            IP adress or host name for net interface.
        port : int
            Connection port for net interface.
        slots_num : int
            A total number of available slots.
        """
        logging.debug('start')
        try:
            gis_path = os.environ['GIS_ROOT']
            util_path = gis_path + '/sbin/gis-buffer-renderer'
            logging.debug(f'Renderer path ={util_path}')
        except Exception as exc:
            logging.debug('Could not find GIS_ROOT')
        
        worker = Worker(slots_num)
        
        while True:
            # checking new data in Pipe
            if pipe_conn.poll():
                data = pipe_conn.recv()
                logging.debug(f'Scheduler got: {data}')
                
                if data[0] == 0:
                    # request for new order
                    logging.debug(f'Scheduler new order {data[1]}')
                    code = 0
                    orderId = 0
                    pincode = 0
                    
                    if self.validator(data[1]):
                        param_tuple = tuple(data[1].values())
                        if param_tuple in self.cached:
                            logging.debug(f'Order exist, cached data is used')
                            orderId = self.cached[param_tuple]
                            pincode = self.orders[self.cached[param_tuple]][2]
                        else:
                            orderId, pincode = self.add_order(data[1])
                        code = 1
                    pipe_conn.send(((orderId, pincode), code))
                elif data[0] == 1:
                    # request to check order
                    orderId, pincode = data[1]
                    logging.debug(f'Scheduler checking order id={orderId}')
                    if self.check_order(orderId):
                        logging.debug(f'Status: {self.orders[orderId][1]}')
                        if self.orders[orderId][2] == pincode:
                            pipe_conn.send(self.orders[orderId][1])
                            if self.orders[orderId][1] == Request_Status.READY.value:
                                #self.orders[orderId][1] = Request_Status.DONE.value
                                pass
                        else:
                            logging.debug(f'Bad pincode {pincode} (not {self.orders[orderId][2]}) for order with id={orderId}')
                            pipe_conn.send(Request_Status.INVALID_PARAM.value)
                    else:
                        logging.debug(f'No order in scheduler with ID {orderId}')
                        pipe_conn.send(Request_Status.INVALID_PARAM.value)
                elif data[0] == 2:
                    deleted_ids = data[1]
                    logging.debug(f'Scheduler deletes ids={deleted_ids}')
                    for i in deleted_ids:
                        self.cached.pop(tuple(self.orders[i][0].values()))
                        self.orders.pop(i)
                        try:
                            self.queue.remove(i)
                        except:
                            pass
                    pipe_conn.send(True)
                continue
            else:
                #print('No data for scheduler')
                pass
            
            # checking queue
            
            #if any of slots are free
            if worker.check_free_slot():
            #if current_order == False:
                if self.queue:
                    current_order_id = self.queue.pop(0)
                    logging.debug(f'Current order id {current_order_id}')
                    params = self.orders[current_order_id][0]
                    logging.debug(f'{params}')
                    child = subprocess.Popen([util_path, f'-uhttp://{host}:{port}', f'-o{current_order_id}',f"-x{params['lon']}", f"-y{params['lat']}",
                                              f"-s{params['scale']}", f"-w{params['w']}", f"-h{params['h']}", f"-f{params['format']}", f"-e{Request_Status.RENDER_FAILED.value}", f"-d{sharedMemoryId}"])
                                        
                    worker.fill_slot((current_order_id, child))
                    
                    logging.debug('popen')
                    
            # if some slots are busy
            # checking if order is ready
            if worker.is_busy():
            #if child.poll() != None:
                for slot, id in worker.active_slots():
                    if slot[1].poll() != None:
                        print('order status ready', Request_Status.READY.value, type(Request_Status.READY.value))
                        logging.debug(f'Scheduler detects process as ready, return code: {slot[1].returncode}, order status ready {Request_Status.READY.value}')
                        if slot[1].returncode == 200:
                            self.orders[slot[0]][1] = Request_Status.READY.value
                        elif slot[1].returncode == Request_Status.NOMEM.value:
                            self.orders[slot[0]][1] = Request_Status.NOMEM.value
                        else:
                            self.orders[slot[0]][1] = Request_Status.RENDER_FAILED.value
                        worker.free_slot(id)
            time.sleep(0.1)
        return 2
