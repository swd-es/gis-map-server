###############################################################################
# (c) 2011-2022, SWD Embedded Systems Limited, http://www.kpda.ru
###############################################################################

#!/usr/bin/python3 -uB
from enum import Enum, unique
import os

@unique
class Request_Status(Enum):
    # statuses below are saved inside of Scheduler order table
    READY = 200
    PROCESSING = 202
    INVALID_PARAM = 400
    DONE = 410
    NOMEM = 418
    RENDER_FAILED = 500
    
    # codes below are used only to responde to the client
    TIMEOUT = 408
    REQUEST_FAILED = 520

def get_status_desc(status):
    """Function returns a description for an error code."""
    if status == Request_Status.READY.value:
        return 'Request is ready'
    elif status == Request_Status.PROCESSING.value:
        return 'Request is processing'
    elif status == Request_Status.INVALID_PARAM.value:
        return 'Request has invallid parameters'
    elif status == Request_Status.DONE.value:
        return 'Request has been already obtained'
    elif status == Request_Status.NOMEM.value:
        return 'Request is not ready - not enough memory on server'
    elif status == Request_Status.RENDER_FAILED.value:
        return 'Request is failed - renderer did not finish successfully'
    elif status == Request_Status.TIMEOUT.value:
        return 'Request status is unknown, timeout error'
    elif status == Request_Status.REQUEST_FAILED.value:
        return 'Request is failed'
    else:
        return 'Unknown Error'

def get_log_path():
    """Function returns the log path for gis-map-server."""
    try:
        path = os.environ['GIS_ROOT']
        path += '/data/logs/gis-map-server/'
    except:
        path = None
    return path
