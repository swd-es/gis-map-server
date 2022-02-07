###############################################################################
# (c) 2011-2022, SWD Embedded Systems Limited, http://www.kpda.ru
###############################################################################

#!/usr/bin/python3 -uB
from utils import Request_Status

class Storage():
    """ 
    A class used to represent data storage for buffers obtained from Renderer. 
    From the storage data is popped from Iterface class when it is requested by the client.
    
    Attributes:
    __________
    storage : dict
        A dictionary used to store buffers. Key: id, val: (data, img_format).
    current_size : int
        Current size of buffer in bytes. It counts only size of data, not the dictionary element.
    buf_size : int
        Maximum buffer size in bytes.

    Methods:
    ________
    push(id, data, img_format, img_length)
        Pushes data to the storage.
    pop_by_id(id)
        Pops data by id.
    """
    def __init__(self, buf_size):
        self.storage = dict()
        self.current_size = 0
        self.buf_size = buf_size

    def push(self, id, data, img_format, img_length):
        """Pushes data to the storage.
        
        Parameters:
        __________
        id : int
            An id of the order, whose data will be stored.
        data : byte str
            Data to store in the storage.
        img_format : str
            A string which specifies a format of data.
        img_length : int
            Data size in bytes.
        
        Returns
        -------
        status
            New order status after pushing the data
        """
        if id in self.storage:
            return Request_Status.INVALID_PARAM.value
        
        if img_length > self.buf_size:
            return Request_Status.NOMEM.value
        
        deleted_ids = list()
        if self.buf_size < (self.current_size + img_length):
            keys = list(self.storage.keys())
            for i in keys:
                d = self.storage.pop(i)
                deleted_ids.append(i)
                self.current_size -= len(d[0])
                if self.buf_size >= (self.current_size + img_length):
                    break
        
        self.storage[id] = (data, img_format)
        self.current_size += img_length
        return Request_Status.READY.value, deleted_ids

    def pop_by_id(self, id):
        """
        Pops data by id.
        
        Parameters:
        __________
        id : int
            An id of the order, whose data is stored.
            
        Returns
        -------
        data
            Data popped by id
        """
        data = self.storage[id]
        #self.current_size -= len(data[0])
        return data
