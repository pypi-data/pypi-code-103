#!/usr/bin/env python3

import requests
import time, datetime
import json
import brotli
import math 
import sqlite3
import os, sys

import traceback
from pprint import pprint

SERVER_DATALOG_ENDPOINT = 'https://%s/datalogs.php?serialno=%s&id=%s'
DATALOG_BINS = [ 86400, 2629746 ]
READING_MISSING = 2147483648
MODELS_FILE = 'models.json'
READINGS_FILE = 'readings.json'
CACHE_DB = '.cached.db'
BINS_PER_REQUEST = 15
EDGE_DT = 0.01


def utc_timestamp():
	d = datetime.datetime.utcnow()
	epoch = datetime.datetime(1970,1,1)
	t = (d - epoch).total_seconds()
	return t


def timestamped_mean(timestamps, data):
	sum = 0
	sumt = 0
	for i in range(1, len(data)):
		val = data[i-1] if not math.isnan(data[i-1]) else 0
		dt = timestamps[i] - timestamps[i-1]
		if val == READING_MISSING or math.isnan(dt) or dt <= EDGE_DT:
			continue

		sum += val*dt
		sumt += dt
	return sum/sumt if sumt != 0 else (data[-1] if len(data) else 0)


def timestamp_mean(timestamps, data):
	return (timestamps[-1]+timestamps[0])/2 if len(data) == 0 else 0

def accumulator_aggregate(timestamps, data):
	if len(data) == 0 or data[-1] == READING_MISSING:
		return 0
	return data[-1] if len(data) else 0

def divide_by_1000(val): 
    return (val/1000.).toFixed(3)

def divide_by_100(val): 
    return val / 100

def divide_by_1000000(val): 
    return val / 1000000

def only_positive(val):
    return max(math.floor(val), 0)

def ws_to_kwh(val): 
    return val / (3600 * 1000)

def divide_by_1000_max_1(val): 
    return min(max(val / 1000, 0), 1.)

def divide_by_10(val):
    return val / 10

def divide_by_100_max_100(val): 
    return min(max(val / 100, 0), 100.)

def divide_by_1000_max_100(val): 
    return min(max(val/1000., 0), 100.0)

def geocoordinates_translation(val): 
    return val/1000000

def binary_translation(val): 
    return 1 if val > 0 else 0

def percent_translation(val): 
    return min(max(val*100, 0), 100.0).toFixed(1)

d = os.path.dirname(__file__)
print(d)

class hamapi:
	def __init__(self, api_key=None, access_token=None, server='hamsystems.eu', datalog_bins=DATALOG_BINS, device_families_file=os.path.join(d, MODELS_FILE), readings_file=os.path.join(d, READINGS_FILE), cache_db_file=CACHE_DB, local_datalogs_dir=None):
		self.api_key = api_key
		self.access_token = access_token
		self.server_url = server
		self.datalog_bins = datalog_bins
		self.items_raw = {}
		self.local_datalogs_dir = local_datalogs_dir

		try:
			with open(device_families_file) as fp:
				self.family_info_map = json.load(fp)
		except Exception:
			print('Warning - failed to load device families json file (%s)' % (device_families_file))

		try:
			with open(readings_file) as fp:
				self.reading_info_map = self.reading_info_map_load(json.load(fp))
		except Exception:
			traceback.print_exc()
			print('Warning - failed to load device readings json file (%s)' % (readings_file))

		self.cache_conn = sqlite3.connect(cache_db_file)
		self.cache_cursor = self.cache_conn.cursor()

		self.cache_cursor.execute('CREATE TABLE IF NOT EXISTS datalog_data (serialno TEXT, levelbin TEXT, data TEXT, PRIMARY KEY (serialno, levelbin))')

	def datalog_segmentation(self, start, end, level=None):
		length = end - start
		if level is None or level < 0:
			level = len(self.datalog_bins)
			for i, bin in enumerate(self.datalog_bins):
				if bin > 0.32*length:
					level = i
					break
			print('level is none, choosing level=%d' % (level))

		B = []
		if level >= len(self.datalog_bins):
			B.append('m')
		else:
			timestamp = start
			while timestamp <= end:
				bin = math.floor(timestamp/self.datalog_bins[level])
				B.append(bin)
				timestamp += self.datalog_bins[level]

		ret = []
		for b in B:
			ret.append([level, b])

		return ret

	def datalog_bin_to_timestamp(self, level, data_bin):
		return self.datalog_bins[level]*int(data_bin)
		
	def get_cached_bin(self, serialno, levelbin):
		self.cache_cursor.execute('SELECT data FROM datalog_data WHERE serialno=? AND levelbin=?', (serialno, levelbin))
		data = self.cache_cursor.fetchone()
		return None if data is None else data[0]

	def get_local_bin(self, serialno, levelbin):
		if not self.local_datalogs_dir:
			return None

		parts = serialno.split(':')
		try:
			local_filename = os.path.join(self.local_datalogs_dir, parts[0], parts[1], levelbin+'.hal.br')
			with open(local_filename, 'rb') as f:
				d = brotli.decompress(f.read()).decode('utf8')
				return d
		except:
			local_filename = os.path.join(self.local_datalogs_dir, parts[0], parts[1], levelbin+'.hal')
			try:
				with open(local_filename, 'rb') as f:
					return f.read().decode('utf8')
			except:
				pass
				# traceback.print_exc()
				# print('Local file (%s) for %s %s not found as un-compressed' % (local_filename, serialno, levelbin))
		return None

	def get_local_datalogs_list_for_device(self, serialno):
		ret = {}
		if not self.local_datalogs_dir:
			return ret

		try:
			family, serial = serialno.split(":")
			for entry in os.scandir(os.path.join(self.local_datalogs_dir, family, serial)):
				try:
					levelbin = entry.name.split('.')[0:2]
					levelbin[0] = int(levelbin[0])
					if levelbin[0] not in ret:
						ret[levelbin[0]] = []
					ret[levelbin[0]].append(levelbin[1])
				except:
					pass
		except:
			# traceback.print_exc()
			pass
		
		return ret

	def get_local_datalogs_list(self):
		ret = {}
		if not self.local_datalogs_dir:
			return ret

		for entry in os.scandir(self.local_datalogs_dir):
			if entry.is_dir():
				family = entry.name
				ret[family] = {}
				for entry2 in os.scandir(entry.path):
					if entry2.is_dir():
						serial = entry2.name
						ret[family][serial] = {}
						for entry3 in os.scandir(entry2.path):
							try:
								levelbin = entry3.name.split('.')[0:2]
								levelbin[0] = int(levelbin[0])
								if levelbin[0] not in ret[family][serial]:
									ret[family][serial][levelbin[0]] = []
								ret[family][serial][levelbin[0]].append(levelbin[1])
							except:
								pass
		return ret

	def get_local_last_state(self, serialno):
		if not self.local_datalogs_dir:
			return {}

		parts = serialno.split(':')
		try:
			with open(os.path.join(self.local_datalogs_dir, parts[0], parts[1], 'state.json')) as f:
				return json.load(f)
		except:
			pass
		return {}

	def set_cached_bin(self, serialno, levelbin, data):
		# print('Setting cache for serialno = %s levelbin = %s' % (serialno, levelbin))
		self.cache_cursor.execute('INSERT OR REPLACE INTO datalog_data VALUES (?,?,?)', (serialno, levelbin, data))
		self.cache_conn.commit()

	
	def get_data_bins(self, serialno, levelbins):
		data = {}
		if self.api_key is not None:
			data['api_key'] = self.api_key
		elif self.access_token is not None:
			data['access_token'] = self.access_token
		
		headers = {
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
 			'Accept-Encoding': 'br, deflate, gzip',
		}

		ret = {}
		if not self.server_url:
			return ret
			
		for level in levelbins:
			levelbin = str(level[0])+'.'+str(level[1])
			r = requests.post(SERVER_DATALOG_ENDPOINT % (self.server_url, serialno, levelbin), data = data, headers = headers)
			if r.headers.get('Content-Encoding') == 'br':
				try:
					r._content = brotli.decompress(r.content)
				except:
					pass
			if len(r.text) > 0:
				ret[levelbin] = r.text
		return ret


	def get_datalog_data(self, serialno, start, end, averaging_step=0, level=0, no_data_value='last', raw_accumulator_values=False):
		bins = self.datalog_segmentation(start, end, level)
		if serialno not in self.items_raw:
			self.items_raw[serialno] = {}

		missing_bins = []
		data = {}
		for bin in bins:
			levelbin = '.'.join([str(b) for b in bin])
			if levelbin in self.items_raw[serialno]:
				data[levelbin] = self.items_raw[serialno][levelbin]
			else:
				bin_ = self.get_local_bin(serialno, levelbin)
				if not bin_:
					bin_ = self.get_cached_bin(serialno, levelbin)
				
				if bin_:
					data[levelbin] = bin_
				else:
					# print('Missing bin serialno = %s levelbin = %s' % (serialno, '.'.join([str(b) for b in bin])))
					missing_bins.append(bin)
		
		level = bins[0][0]
		latest_bin = '.'.join([str(level), str(int(math.floor(utc_timestamp())/self.datalog_bins[level]) if level < len(self.datalog_bins) else 'm')])

		for i in range(0, len(missing_bins), BINS_PER_REQUEST):
			newdata = self.get_data_bins(serialno, missing_bins[i:i+BINS_PER_REQUEST])
			for levelbin, d in newdata.items():
				data[levelbin] = d
				self.items_raw[serialno][levelbin] = d
				if levelbin < latest_bin:
					self.set_cached_bin(serialno, levelbin, d)

		parsed_data = self.parse_datalog_data(serialno, data, start, end)
		return parsed_data if averaging_step == 0 else self.average_step_datalog_data(parsed_data, start, end, averaging_step, no_data_value=no_data_value, raw_accumulator_values=raw_accumulator_values)


	def family_serial_from_serialno(self, serialno):
		return serialno.split(':')	
		

	def get_device_family_info(self, serialno):
		family, serial = self.family_serial_from_serialno(serialno)
		return self.family_info_map[family]

	def reading_info_map_load(self, map):
		self.reading_info_map = {}
		for g, data in map.items():
			self.reading_info_map[g] = data
			self.reading_info_map[g]["aggregation"] = globals()[self.reading_info_map[g]["aggregation"]] if "aggregation" in self.reading_info_map[g] and self.reading_info_map[g]["aggregation"] in globals() else timestamped_mean 
			self.reading_info_map[g]["transform"] = globals()[self.reading_info_map[g]["transform"]] if "transform" in self.reading_info_map[g] and self.reading_info_map[g]["transform"] in globals() else lambda x: float(x)
		return self.reading_info_map

	def reading_transform(self, reading, value):
		return self.reading_info_map[reading]["transform"](float(value)) if reading in self.reading_info_map and "transform" in self.reading_info_map[reading] else float(value)


	def parse_datalog_data(self, serialno, bin_data, start=0, end=0):
		family_info = self.get_device_family_info(serialno)
		keys = ['timestamp'] + family_info['readings'] + family_info['output_names']

		ret = {}
		for k in keys:
			ret[k] = []

		lines = []
		for levelbin, data in bin_data.items():
			lines.extend(data.split('\n'))
		
		lines.sort()
		previous = False
		for line in lines:
			try:
				parts = line.split(';')
				if len(parts) != len(keys):
					continue
				
				t = float(parts[0])
				if (start and t < start) or (end and t > end):
					continue

				set_previous = False
				for i, k in enumerate(keys):
					p = parts[i]
					if p == str(READING_MISSING) or len(p) == 0:
						if previous:
							ret[k].append(self.reading_transform(k, previous[i]))
							ret[k].append(self.reading_transform(k, previous[i]))
						else:
							ret[k].append(0)
							ret[k].append(0)
					else:
						if previous:
							ret[k].append(self.reading_transform(k, previous[i]) if k != 'timestamp' else self.reading_transform(k, p) - EDGE_DT)
						ret[k].append(self.reading_transform(k, p))
						set_previous = True

				if set_previous:
					previous = parts
			except Exception:
				pass
				# traceback.print_exc()

		# print('length : %d' % (len(ret['timestamp'])))
		return ret
		
			
	def average_step_datalog_data(self, data, start, end, step, no_data_value='last', raw_accumulator_values=False):
		timestamps = data['timestamp']
		keys = data.keys()
		
		data_buffer = {}
		last_value = {}
		previous_value = {}
		ret = {}
		for k in keys:
			ret[k] = []
			data_buffer[k] = []
			previous_value[k] = math.nan
			last_value[k] = 0

		last_timestamp	= start
		next_end = start + step
		for i in range(len(timestamps)):
			timestamp = timestamps[i]
			last_timestamp = timestamp
			if timestamp < start:
				continue
			if timestamp > end:
				break

			aggregated_value = False
			# if timestamp is over the next end
			while timestamp > next_end:
				rtimestamp = next_end - step

				no_data = len(data_buffer['timestamp']) <= 1
				if not aggregated_value:
					aggregated_value = {}
					for k in keys:
						if k == 'timestamp':
							continue

						if len(data_buffer[k]) > 0:
							rvalue = self.reading_info_map[k]['aggregation'](data_buffer['timestamp'], data_buffer[k])
							last_value[k] = rvalue
							if self.reading_info_map[k]['accumulated'] and not raw_accumulator_values:
								rvalue = rvalue - data_buffer[k][0]
							aggregated_value[k] = rvalue
							data_buffer[k] = [data_buffer[k][-1]]
						else:
							aggregated_value[k] = last_value[k]
					data_buffer['timestamp'] = [data_buffer['timestamp'][-1]] if len(data_buffer['timestamp']) else []

				ret['timestamp'].append(rtimestamp)
				for k in keys:
					if k == 'timestamp':
						continue
					
					if no_data:
						if no_data_value == 'last':
							ret[k].append(ret[k][len(ret[k])-1] if len(ret[k]) else float('nan'))
						elif no_data_value != 'skip':
							ret[k].append(no_data_value)
					else:
						ret[k].append(no_data_value if no_data else aggregated_value[k])
			
				next_end += step

			# add the values at this timestamp
			for k in keys:
				try:
					data_buffer[k].append(data[k][i])
				except:
					data_buffer[k].append(data_buffer[k][-1] if len(data_buffer[k]) else 0)

		# take care of the end of data
		aggregated_value = False
		rtimestamp = last_timestamp
		no_data = len(data_buffer[k]) == 0
		while rtimestamp < end:
			if not aggregated_value:
				aggregated_value = {}
				for k in keys:
					if k == 'timestamp':
						continue

					rvalue = self.reading_info_map[k]['aggregation'](data_buffer['timestamp'], data_buffer[k])
					last_value[k] = rvalue
					if self.reading_info_map[k]['accumulated'] and not raw_accumulator_values:
						rvalue = rvalue - (data_buffer[k][0] if len(data_buffer[k]) > 0 else last_value[k])
					aggregated_value[k] = rvalue
			
			rtimestamp = next_end - step/2

			ret['timestamp'].append(rtimestamp)
			for k in keys:
				if k == 'timestamp':
					continue
				
				if no_data:
					if no_data_value == 'last':
						ret[k].append(ret[k][len(ret[k])-1] if len(ret[k]) else 0)
					elif no_data_value != 'skip':
						ret[k].append(no_data_value)
				else:
					ret[k].append(no_data_value if no_data else aggregated_value[k])
			
			next_end += step
			no_data = True
		for k in ret:
			ret[k] = ret[k][:-1]
		return ret
	
	def send_device_command(serialno, command):
		raise NotImplementedError

	def get_realtime_data(serialno):
		raise NotImplementedError
