from numpy import log10
from math import ceil
import utm

import os
import shutil

import gzip
import tarfile
import zipfile

def _nice_round(val):
	from numpy import log10
	from math import ceil
	vi = int(log10(val))
	return ceil(val/(10**vi))*10**vi

def _represents_int(s):
	try:
		int(s)
		return True
	except ValueError:
		return False

def latlon_to_utm_epsg(lat, lon):
    offset = int(round((183+lon)/6.0))
    return 32600+offset if (lat > 0) else 32700+offset

# def latlonPointToUTMcode(pt):
# 	lat = pt.xy[1][0]
# 	lon = pt.xy[0][0]
# 	zoneNum = utm.latlon_to_zone_number(lat,lon)
# 	zoneLet = utm.latitude_to_zone_letter(lat)
# 	projCode = "+proj=utm +zone="+str(zoneNum)+zoneLet+" +units=m +ellps=WGS84"
# 	return projCode

def _block_separator(line):
	if ":" in line:
		return (line.split(':',1)[0]).rstrip()
	else:
		return None

def _file_in_zip(fileName,zipRef):
	return any(x.endswith(fileName) for x in zipRef.namelist())

def _path_of_file_in_zip(fileName,zipRef):
	return [s for s in zipRef.namelist() if fileName in s]

def _decompress_gz(fileIn):
	filename, fileext = os.path.splitext(fileIn)

	if fileext != '.gz':
		raise ValueError('In _decompress_gz, {} must have extension .gz'.format(fileIn))
	
	with gzip.open(fileIn, 'rb') as f_in:
		with open(filename, 'wb') as f_out:
			shutil.copyfileobj(f_in, f_out)
	
	return filename

def csv_active_cols(filename):
	with open(filename) as f:
		header = f.readline()
	n_commas = header.count(',')
	last_comma = header.rfind(',')
	if len(header[last_comma+1:].rstrip())==0:
		# last comma has no following field so ignore
		cols = range(n_commas)
	else:
		cols = range(n_commas+1)
	return cols

def csv_num_cols(filename):
	cols = csv_active_cols(filename)
	return len(cols)

# def nc_active_cols(filename):
# 