import logging
import base64
import string
import array
import uuid
import random
from ca_apm_agent.connections.constants import CORIDTEMPLATE
from ca_apm_agent.global_constants import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME[0] + '.correlation.correlation')

def get_new_corid_header():

	try:
		cor_len = 32
		corlist = [random.choice(string.digits+string.ascii_letters) for i in range(cor_len)]
		corid = ("".join(corlist)).upper()
		logger.debug('Random CorId Generated %s', corid)
	except Exception as e:
		logger.error('Problem In Generating Random Corid')
    
	encode_string = CORIDTEMPLATE
    
	decode_str = base64.b64decode(encode_string)
	logger.debug('Successfully Decoded The String %s', decode_str)
    
	arrobj = array.array('B', decode_str)
	logger.debug('Converted the Decoded string to Array Object %s', arrobj)
    
	bytevalues = bytearray(arrobj)
	length = bytevalues [96] 
	KEY_LEN = length
	keylist = [random.choice(string.digits+string.ascii_letters) for i in range(KEY_LEN)]
	txnid = ("".join(keylist)).upper()
    
	decode_bytevals = bytevalues.decode('cp855')        
	str_rep = str(decode_bytevals) 
	stxnid = str(txnid)
	logger.debug('New Txn Trace Id generated Successfully %s', stxnid)
    
	repstr = str_rep.replace(str_rep[97:97+KEY_LEN], stxnid)
	logger.debug('New Txn Trace Id Replaced Successfully')
    
	enc_repstr = repstr.encode('cp855')      
	final = base64.b64encode(enc_repstr)
	final_str = str(final, 'utf-8')
    
	comma = ','
	seqId = '1:1'
	propflag = '0'
	seqflag = '0'
    
	header = corid + comma + seqId + comma + propflag + comma + seqflag + comma + comma + comma + final_str
	logger.debug('New Header Sent Successfully %s', header)
	return header


def upd_corid_header(header):

	http_header = header
	
	if http_header is None:
		logger.error('Header Received is NULL')
	else:
		logger.debug('Header Received Successfuly')
    
	corid_received = http_header[:32]  
	seqid_separators = http_header[32:43]

	seqid_complete_check = seqid_separators[4]
	if seqid_complete_check == ',':
		pick_encode_string = http_header[43:]
	else:
		pick_encode_string = http_header[44:]
	
	encode_string = pick_encode_string

	# If http_header carries multiple corids, the below logic consider only the first corid and moves on.
	# Check whether comma is present in the encode_string
	comma_pos = encode_string.find(",")
	
	if comma_pos == -1:
		encode_string = pick_encode_string
		logger.debug('Header has valid corid')
	else:
		if seqid_complete_check == ',':
			encode_string = http_header[43:comma_pos]
		else:
			encode_string = http_header[44:comma_pos]
		logger.debug('Successfully picked the corid from the header received')

	decode_str = base64.b64decode(encode_string)
	logger.debug('Successfully Decoded The String %s', decode_str)
     
	arrobj = array.array('B', decode_str)
	logger.debug('Converted the Decoded string to Array Object %s', arrobj)
    
	bytevalues = bytearray(arrobj)
	length = bytevalues [96] 
	KEY_LEN = length
	keylist = [random.choice(string.digits+string.ascii_letters) for i in range(KEY_LEN)]
	txnid = ("".join(keylist)).upper()
    
	decode_bytevals = bytevalues.decode('cp855')        
	str_rep = str(decode_bytevals) 
	stxnid = str(txnid)
	logger.debug('New Txn Trace Id generated Successfully %s', stxnid)
    
	repstr = str_rep.replace(str_rep[97:97+KEY_LEN], stxnid)
	logger.debug('New Txn Trace Id Replaced Successfully')	
    
	enc_repstr = repstr.encode('cp855')      
	final = base64.b64encode(enc_repstr)
	final_str = str(final, 'utf-8')
    
	http_header = corid_received + seqid_separators + final_str
	logger.debug('Updated the Header Successfully %s', http_header)
	return http_header
    
def get_txn_traceid(header):

	http_header = header

	if http_header is None:
		logger.error('Header Received is NULL')
	else:
		logger.debug('Header Received Successfuly')

	corid_received = http_header[:32]
	seqid_separators = http_header[32:43]
	encode_string = http_header[43:]

	decode_str = base64.b64decode(encode_string)
		 
	arrobj = array.array('B', decode_str)

	bytevalues = bytearray(arrobj)
	length = bytevalues [96] 
	KEY_LEN = length

	decode_bytevals = bytevalues.decode('cp855')        
	str_rep = str(decode_bytevals) 

	traceid = str_rep[97:97+KEY_LEN]
		
	logger.debug('Txn TraceID Sent Successfully %s', traceid)
	return traceid