import logging
from http.client import responses
from ca_apm_agent.python_modifiers.singleton import Singleton
from ca_apm_agent.connections.constants import CLASS, MESSAGE
from ca_apm_agent.global_constants import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME[0] + '.probes.aiohttp.http_error_status_code')

def get_http_status_code(status_reason):

#### Clinet Error Status Code ################### 
  statuscode = 200 
  if (status_reason == '<Response Bad Request not prepared>' or status_reason == 'Bad Request' ) :
    statuscode = 400

  if (status_reason == '<Response Unauthorized not prepared>' or status_reason == 'Unauthorized' ) :
    statuscode = 401

  if (status_reason == '<Response Payment Required not prepared>' or status_reason == 'Payment Required' ) :
    statuscode = 402

  if (status_reason == '<Response Forbidden not prepared>' or status_reason == 'Forbidden' ) :
    statuscode = 403

  if (status_reason == '<Response Not Found not prepared>' or status_reason == 'Not Found' ) :
    statuscode = 404

  if (status_reason == '<Response Method Not Allowed not prepared>' or status_reason == 'Method Not Allowed' ) :
    statuscode = 405

  if (status_reason == '<Response Not Acceptable not prepared>' or status_reason == 'Not Acceptable' ) :
    statuscode = 406

  if (status_reason == '<Response Proxy Authentication Required not prepared>' or status_reason == 'Proxy Authentication Required' ) :
    statuscode = 407

  if (status_reason == '<Response Request Timeout not prepared>' or status_reason == 'Request Timeout' ) :
    statuscode = 408

  if (status_reason == '<Response Conflict not prepared>' or status_reason == 'Conflict' ) :
    statuscode = 409

  if (status_reason == '<Response Gone not prepared>' or status_reason == 'Gone' ) :
    statuscode = 410

  if (status_reason == '<Response Length Required not prepared>' or status_reason == 'Length Required' ) :
    statuscode = 411

  if (status_reason == '<Response Precondition Failed not prepared>' or status_reason == 'Precondition' ) :
    statuscode = 412

  if (status_reason == '<Response Request Entity Too Large not prepared>' or status_reason == 'Request Entity Too Large' ) :
    statuscode = 413

  if (status_reason == '<Response Request-URI Too Long not prepared>' or status_reason == 'Request-URI Too Long' ) :
    statuscode = 414

  if (status_reason == '<Response Unsupported Media Type not prepared>' or status_reason == 'Unsupported Media Type' ) :
    statuscode = 415

  if (status_reason == '<Response Requested Range Not Satisfiable not prepared>' or status_reason == 'Requested Range Not Satisfiable' ) :
    statuscode = 416

  if (status_reason == '<Response Expectation Failed not prepared>' or status_reason == 'Expectation Failed' ) :
    statuscode = 417

  if (status_reason == '<Response Misdirected Request not prepared>' or status_reason == 'Misdirected Request' ) :
    statuscode = 421

  if (status_reason == '<Response Unprocessable Entity not prepared>' or status_reason == 'Unprocessable Entity' ) :
    statuscode = 422

  if (status_reason == '<Response Unprocessable Entity not prepared>' or status_reason == 'Unprocessable Entity' ) :
    statuscode = 424

  if (status_reason == '<Response Upgrade Required not prepared>' or status_reason == 'Upgrade Required' ) :
    statuscode = 426

  if (status_reason == '<Response Precondition Required not prepared>' or status_reason == 'Precondition Required' ) :
    statuscode = 428

  if (status_reason == '<Response Too Many Requests not prepared>' or status_reason == 'Too Many Requests' ) :
    statuscode = 429

  if (status_reason == '<Response Request Header Fields Too Large not prepared>' or status_reason == 'Request Header Fields Too Large' ) :
    statuscode = 431

#  if status_reason == '<Response  not prepared>' :
#    statuscode = 451

#### Server Error Status Code ###################

  if (status_reason == '<Response Internal Server Error not prepared>' or status_reason == 'Internal Server Error' ) :
    statuscode = 500

  if (status_reason == '<Response Not Implemented not prepared>' or status_reason == 'Not Implemented' ) :
    statuscode = 501

  if (status_reason == '<Response Bad Gateway not prepared>' or status_reason == 'Bad Gateway' ) :
    statuscode = 502

  if (status_reason == '<Response Service Unavailable not prepared>' or status_reason == 'Service Unavailable' ) :
    statuscode = 503
    
  if (status_reason == '<Response Gateway Timeout not prepared>' or status_reason == 'Gateway Timeout' ) :
    statuscode = 504
    
  if (status_reason == '<Response HTTP Version Not Supported not prepared>' or status_reason == 'HTTP Version Not Supported' ) :
    statuscode = 505
                    
  return statuscode
  
  

