#!/usr/bin/env python3

import numpy as np
import sys
import os
import multiprocessing as mp
import shutil
import subprocess
import gzip
import sqlite3
import zlib
import time
import tempfile
from array import array
from struct import unpack
import re
from collections import defaultdict
from pathlib import Path
from bisect import bisect_left
from bisect import bisect_right

CtoPy	   = { 'A':'<c', 'c':'<b', 'C':'<B', 's':'<h', 'S':'<H', 'i':'<i', 'I':'<I', 'f':'<f' }
py4py	   = { 'A':  1 , 'c':  1 , 'C':  1 , 's':  2 , 'S':  2 , 'i':  4 , 'I':  4 , 'f':  4  }
dna_codes   = '=ACMGRSVTWYHKDBN'
cigar_codes = 'MIDNSHP=X'
parse_codes = {
	'sam':					 ' The current alignment in SAM format.',
	'bam':					 ' All the bytes that make up the current alignment ("read"),\n							  still in binary just as it was in the BAM file. Useful\n							  when creating a new BAM file of filtered alignments.',
	'sam_qname':			   ' [1st column in SAM] The QNAME (fragment ID) of the alignment.',
	'bam_qname':			   ' The original bytes before decoding to sam_qname.',
	'sam_flag':				' [2nd column in SAM] The FLAG number of the alignment.',
	'bam_flag':				' The original bytes before decoding to sam_flag.',
	'sam_refID':			   ' The chromosome ID (not the same as the name!).\n							  Chromosome names are stored in the BAM header (file_chromosomes),\n							  so to convert refIDs to chromsome names one needs to do:\n							  "my_bam.file_chromosomes[read.sam_refID]" (or use sam_rname)\n							  But for comparisons, using the refID is much faster that using\n							  the actual chromosome name (for example, when reading through a\n							  sorted BAM file and looking for where last_refID != this_refID)\n							  Note that when negative the alignment is not aligned, and thus one\n							  must not perform my_bam.file_chromosomes[read.sam_refID]\n							  without checking that the value is positive first.',
	'sam_rname':			   ' [3rd column in SAM] The actual chromosome/contig name for the\n							  alignment. Will return "*" if refID is negative.',
	'bam_refID':			   ' The original bytes before decoding to sam_refID.',
	'sam_pos1':				' [4th column in SAM] The 1-based position of the alignment. Note\n							  that in SAM format values less than 1 are converted to "0" for\n							  "no data" and sam_pos1 will also do this.',
	'sam_pos0':				' The 0-based position of the alignment. Note that in SAM all\n							  positions are 1-based, but in BAM they are stored as 0-based.\n							  Unlike sam_pos1, negative values are kept as negative values,\n							  essentially giving one the decoded value as it was stored.',
	'bam_pos':				 ' The original bytes before decoding to sam_pos*.',
	'sam_mapq':				' [5th column in SAM] The Mapping Quality of the current alignment.',
	'bam_mapq':				' The original bytes before decoding to sam_mapq.',
	'sam_cigar_string':		' [6th column in SAM] The CIGAR string, as per the SAM format.\n							  Allowed values are "MIDNSHP=X".',
	'sam_cigar_list':		  ' A list of tuples with 2 values per tuple:\n							  the number of bases, and the CIGAR operation applied to those\n							  bases. Faster to calculate than sam_cigar_string.',
	'bam_cigar':			   ' The original bytes before decoding to sam_cigar_*.',
	'sam_next_refID':		  ' The sam_refID of the alignment\'s mate (if any). Note that as per\n							  sam_refID, this value can be negative and is not the actual\n							  chromosome name (see sam_pnext1).',
	'sam_rnext':			   ' [7th column in SAM] The chromosome name of the alignment\'s mate.\n							  Value is "*" if unmapped. Note that in a SAM file this value\n							  is "=" if it is the same as the sam_rname, however pybam will\n							  only do this if the user prints the whole SAM entry with "sam".',
	'bam_next_refID':		  ' The original bytes before decoding to sam_next_refID.',
	'sam_pnext1':			  ' [8th column in SAM] The 1-based position of the alignment\'s mate.\n							  Note that in SAM format values less than 1 are converted to "0"\n							  for "no data", and sam_pnext1 will also do this.',
	'sam_pnext0':			  ' The 0-based position of the alignment\'s mate. Note that in SAM all\n							  positions are 1-based, but in BAM they are stored as 0-based.\n							  Unlike sam_pnext1, negative values are kept as negative values\n							  here, essentially giving you the value as it was stored in BAM.',
	'bam_pnext':			   ' The original bytes before decoding to sam_pnext0.',
	'sam_tlen':				' [9th column in SAM] The TLEN value.',
	'bam_tlen':				' The original bytes before decoding to sam_tlen.',
	'sam_seq':				 ' [10th column in SAM] The SEQ value (DNA sequence of the alignment).\n							  Allowed values are "ACGTMRSVWYHKDBN and =".',
	'bam_seq':				 ' The original bytes before decoding to sam_seq.',
	'sam_qual':				' [11th column in SAM] The QUAL value (quality scores per DNA base\n							  in SEQ) of the alignment.',
	'bam_qual':				' The original bytes before decoding to sam_qual.',
	'sam_tags_list':		   ' A list of tuples with 3 values per tuple: a two-letter TAG ID, the\n							  type code used to describe the data in the TAG value (see SAM spec.\n							  for details), and the value of the TAG. Note that the BAM format\n							  has type codes like "c" for a number in the range -127 to +127,\n							  and "C" for a number in the range of 0 to 255.\n							  In a SAM file however, all numerical codes appear to just be stored\n							  using "i", which is a number in the range -2147483647 to +2147483647.\n							  sam_tags_list will therefore return the code used in the BAM file,\n							  and not "i" for all numbers.',
	'sam_tags_string':		 ' [12th column a SAM] Returns the TAGs in the same format as would be found \n							  in a SAM file (with all numbers having a signed 32bit code of "i").',
	'bam_tags':				' The original bytes before decoding to sam_tags_*.',
	'sam_bin':				 ' The bin value of the alignment (used for indexing reads).\n							  Please refer to section 5.3 of the SAM spec for how this\n							  value is calculated.',
	'bam_bin':				 ' The original bytes before decoding to sam_bin.',
	'sam_block_size':		  ' The number of bytes the current alignment takes up in the BAM\n							  file minus the four bytes used to store the block_size value\n							  itself. Essentially sam_block_size +4 == bytes needed to store\n							  the current alignment.',
	'bam_block_size':		  ' The original bytes before decoding to sam_block_size.',
	'sam_l_read_name':		 ' The length of the QNAME plus 1 because the QNAME is terminated\n							  with a NUL byte.',
	'bam_l_read_name':		 ' The original bytes before decoding to sam_l_read_name.',
	'sam_l_seq':			   ' The number of bases in the seq. Useful if you just want to know\n							  how many bases are in the SEQ but do not need to know what those\n							  bases are (which requires more decoding effort).',
	'bam_l_seq':			   ' The original bytes before decoding to sam_l_seq.',
	'sam_n_cigar_op':		  ' The number of CIGAR operations in the CIGAR field. Useful if one\n							  wants to know how many CIGAR operations there are, but does not\n							  need to know what they are.',
	'bam_n_cigar_op':		  ' The original bytes before decoding to sam_n_cigar_op.',
	'file_alignments_read':	' A running counter of the number of alignments ("reads"),\n							  processed thus far. Note the BAM format does not store\n							  how many reads are in a file, so the usefulness of this\n							  metric is somewhat limited unless one already knows how\n							  many reads are in the file.',
	'file_binary_header':	  ' From the first byte in the file, until the first byte of\n							  the first read. The original binary header.',
	'file_bytes_read':		 ' A running counter of the bytes read from the file. Note\n							  that as data is read in arbitary chunks, this is literally\n							  the amount of data read from the file/pipe by pybam.',
	'file_chromosome_lengths': ' The binary header of the BAM file includes chromosome names\n							  and chromosome lengths. This is a dictionary of chromosome-name\n							  keys and chromosome-length values.',
	'file_chromosomes':		' A list of chromosomes from the binary header.',
	'file_decompressor':	   ' BAM files are compressed with bgzip. The value here reflects\n							  the decompressor used. "internal" if pybam\'s internal\n							  decompressor is being used, "gzip" or "pigz" if the system\n							  has these binaries installed and pybam can find them.\n							  Any other value reflects a custom decompression command.',
	'file_directory':		  ' The directory the input BAM file can be found in. This will be\n							  correct if the input file is specified via a string or python\n							  file object, however if the input is a pipe such as sys.stdin, \n							  then the current working directory will be used.',
	'file_header':			 ' The ASCII portion of the BAM header. This is the typical header\n							  users of samtools will be familiar with.',
	'file_name':			   ' The file name (base name) of input file if input is a string or\n							  python file object. If input is via stdin this will be "<stdin>"'
}

class read():

	def __init__(self,f,fields=False, decompressor="internal"):
		
		self.file_bytes_read		 = 0
		self.file_chromosomes		= []
		self.file_alignments_read	= 0
		self.file_chromosome_lengths = {}

		if fields is not False:
			
			if type(fields) is not list or len(fields) == 0:
				raise PybamError('\n\nFields for the static parser must be provided as a non-empty list. You gave a ' + str(type(fields)) + '\n')
			else:
				for field in fields:
					if field.startswith('sam') or field.startswith('bam'):
						if field not in list(parse_codes.keys()):
							raise PybamError('\n\nStatic parser field "' + str(field) + '" from fields ' + str(fields) + ' is not known to this version of pybam!\nPrint "pybam.wat" to see available field names with explinations.\n')
					else:
						raise PybamError('\n\nStatic parser field "' + str(field) + '" from fields ' + str(fields) + ' does not start with "sam" or "bam" and thus is not an avaliable field for the static parsing.\nPrint "pybam.wat" in interactive python to see available field names with explinations.\n')

		if decompressor:
			if type(decompressor) is str:
				 if decompressor != 'internal' and '{}' not in decompressor: raise PybamError('\n\nWhen a custom decompressor is used and the input file is a string, the decompressor string must contain at least one occurence of "{}" to be substituted with a filepath by pybam.\n')
			else: raise PybamError('\n\nUser-supplied decompressor must be a string that when run on the command line decompresses a named file (or stdin), to stdout:\ne.g. "lzma --decompress --stdout {}" if pybam is provided a path as input file, where {} is substituted for that path.\nor just "lzma --decompress --stdout" if pybam is provided a file object instead of a file path, as data from that file object will be piped via stdin to the decompression program.\n')

		## First we make a generator that will return chunks of uncompressed data, regardless of how we choose to decompress:
		def generator():
			DEVNULL = open(os.devnull, 'wb')
			# First we need to figure out what sort of file we have - whether it's gzip compressed, uncompressed, or something else entirely!
			if type(f) is str:
				try: 
					self._file = open(f,'rb')
				except: 
					raise PybamError('\n\nCould not open "' + str(self._file.name) + '" for reading!\n')
				try: 
					magic = self._file.read(4)
				except: 
					raise PybamError('\n\nCould not read from "' + str(self._file.name) + '"!\n')
			elif type(f) is file:
				self._file = f
				try: 
					magic = self._file.read(4)
				except: 
					raise PybamError('\n\nCould not read from "' + str(self._file.name) + '"!\n')
			else: 
				raise PybamError('\n\nInput file was not a string or a file object. It was: "' + str(f) + '"\n')

			self.file_name = os.path.basename(os.path.realpath(self._file.name))
			self.file_directory = os.path.dirname(os.path.realpath(self._file.name))
			
			if magic == b'BAM\1':
				# The user has passed us already unzipped BAM data! Job done :)
				data = b'BAM\1' + self._file.read(35536)
				self.file_bytes_read += len(data)
				self.file_decompressor = 'None'
				while data:
					yield data
					data = self._file.read(35536)
					self.file_bytes_read += len(data)
				self._file.close()
				DEVNULL.close()
				return

			elif magic == b"\x1f\x8b\x08\x04":  # The user has passed us compressed gzip/bgzip data, which is typical for a BAM file

				if decompressor is not False and decompressor != 'internal':
					if type(f) is str: 
						self._subprocess = subprocess.Popen(									decompressor.replace('{}',f),	shell=True, stdout=subprocess.PIPE, stderr=DEVNULL)
					else:
						self._subprocess = subprocess.Popen('{ printf "'+magic+'"; cat; } | ' + decompressor, stdin=self._file, shell=True, stdout=subprocess.PIPE, stderr=DEVNULL)
					self.file_decompressor = decompressor
					data = self._subprocess.stdout.read(35536)
					self.file_bytes_read += len(data)
					while data:
						yield data
						data = self._subprocess.stdout.read(35536)
						self.file_bytes_read += len(data)
					self._file.close()
					DEVNULL.close()
					return

				# else look for pigz or gzip:
				else:				
					try:
						self._subprocess = subprocess.Popen(["pigz"],stdin=DEVNULL,stdout=DEVNULL,stderr=DEVNULL)
						if self._subprocess.returncode is None: self._subprocess.kill()
						use = 'pigz'
					except OSError:
						try:
							self._subprocess = subprocess.Popen(["gzip"],stdin=DEVNULL,stdout=DEVNULL,stderr=DEVNULL)
							if self._subprocess.returncode is None: self._subprocess.kill()
							use = 'gzip'
						except OSError: 
							use = 'internal'
					if use != 'internal' and decompressor != 'internal':
						if type(f) is str: self._subprocess = subprocess.Popen([								   use , '--decompress','--stdout',	   f		   ], stdout=subprocess.PIPE, stderr=DEVNULL)
						else:			  self._subprocess = subprocess.Popen('{ printf "'+magic+'"; cat; } | ' + use + ' --decompress  --stdout', stdin=f, shell=True, stdout=subprocess.PIPE, stderr=DEVNULL)
						time.sleep(1)
						if self._subprocess.poll() == None:
							data = self._subprocess.stdout.read(35536)
							self.file_decompressor = use
							self.file_bytes_read += len(data)
							while data:
								yield data
								data = self._subprocess.stdout.read(35536)
								self.file_bytes_read += len(data)
							self._file.close()
							DEVNULL.close()
							return

					# Python's gzip module can't read from a stream that doesn't support seek(), and the zlib module cannot read the bgzip format without a lot of help:
					self.file_decompressor = 'internal'
					raw_data = magic + self._file.read(65536)
					self.file_bytes_read = len(raw_data)
					internal_cache = []
					blocks_left_to_grab = 50
					bs = 0
					checkpoint = 0
					decompress = zlib.decompress
					while raw_data:
						if len(raw_data) - bs < 35536:
							raw_data = raw_data[bs:] + self._file.read(65536)
							self.file_bytes_read += len(raw_data) - bs
							bs = 0
						magic = raw_data[bs:bs+4]
						if not magic: break # a child's heart
						if magic != b"\x1f\x8b\x08\x04": raise PybamError('\n\nThe input file is not in a format I understand. First four bytes: ' + repr(magic) + '\n')
						try:
							more_bs = bs + unpack("<H", raw_data[bs+16:bs+18])[0] +1
							internal_cache.append(decompress(raw_data[bs+18:more_bs-8],-15))
							bs = more_bs
						except: ## zlib doesnt have a nice exception for when things go wrong. just "error"
							header_data = magic + raw_data[bs+4:bs+12]
							header_size = 12
							extra_len = unpack("<H", header_data[-2:])[0]
							while header_size-12 < extra_len:
								header_data += raw_data[bs+12:bs+16]
								subfield_id = header_data[-4:-2]
								subfield_len = unpack("<H", header_data[-2:])[0]
								subfield_data = raw_data[bs+16:bs+16+subfield_len]
								header_data += subfield_data
								header_size += subfield_len + 4
								if subfield_id == 'BC': block_size = unpack("<H", subfield_data)[0]
							raw_data = raw_data[bs+16+subfield_len:bs+16+subfield_len+block_size-extra_len-19]
							crc_data = raw_data[bs+16+subfield_len+block_size-extra_len-19:bs+16+subfield_len+block_size-extra_len-19+8] # I have left the numbers in verbose, because the above try is the optimised code.
							bs = bs+16+subfield_len+block_size-extra_len-19+8
							zipped_data = header_data + raw_data + crc_data
							internal_cache.append(decompress(zipped_data,47)) # 31 works the same as 47.

							# Although the following in the bgzip code from biopython, its not needed if you let zlib decompress the whole zipped_data, header and crc, because it checks anyway (in C land)
							# I've left the manual crc checks in for documentation purposes:
							'''
							expected_crc = crc_data[:4]
							expected_size = unpack("<I", crc_data[4:])[0]
							if len(unzipped_data) != expected_size: print 'ERROR: Failed to unpack due to a Type 1 CRC error. Could the BAM be corrupted?'; exit()
							crc = zlib.crc32(unzipped_data)
							if crc < 0: crc = pack("<i", crc)
							else:	   crc = pack("<I", crc)
							if expected_crc != crc: print 'ERROR: Failed to unpack due to a Type 2 CRC error. Could the BAM be corrupted?'; exit()
							'''
						blocks_left_to_grab -= 1
						if blocks_left_to_grab == 0:
							yield b''.join(internal_cache)
							internal_cache = []
							blocks_left_to_grab = 50
					self._file.close()
					DEVNULL.close()
					if internal_cache != b'':
						yield b''.join(internal_cache)
					return

			elif decompressor is not False and decompressor != 'internal':
				# It wouldn't be safe to just print to the shell four random bytes from the beginning of a file, so instead it's
				# written to a temp file and cat'd. The idea here being that we trust the decompressor string as it was written by 
				# someone with access to python, so it has system access anyway. The file/data, however, should not be trusted.
				magic_file = os.path.join(tempfile.mkdtemp(),'magic')
				with open(magic_file,'wb') as mf: 
					mf.write(magic)
				if type(f) is str: 
					self._subprocess = subprocess.Popen(decompressor.replace('{}',f),	shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				else:
					self._subprocess = subprocess.Popen('{ cat "'+magic_file+'"; cat; } | ' + decompressor, stdin=self._file, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				self.file_decompressor = decompressor
				data = self._subprocess.stdout.read(35536)
				self.file_bytes_read += len(data)
				while data:
					yield data
					data = self._subprocess.stdout.read(35536)
					self.file_bytes_read += len(data)
				self._file.close()
				DEVNULL.close()
				return
			else:
				raise PybamError('\n\nThe input file is not in a format I understand. First four bytes: ' + repr(magic) + '\n')

		## At this point, we know that whatever decompression method was used, a call to self._generator will return some uncompressed data.
		self._generator = generator()
		
		#print(self._generator)
				
		## So lets parse the BAM header:
		header_cache = b''
				
		while len(header_cache) < 4:
			header_cache += next(self._generator)
		p_from = 0; p_to = 4
		if header_cache[p_from:p_to] != b'BAM\x01':
			raise PybamError('\n\nInput file ' + self.file_name + ' does not appear to be a BAM file.\n')
			
		## Parse the BAM header:
		p_from = p_to; p_to += 4
		length_of_header = unpack('<i',header_cache[p_from:p_to])[0]
		p_from = p_to; p_to += length_of_header
		while len(header_cache) < p_to: header_cache += str(next(self._generator))
		self.file_header = header_cache[p_from:p_to]
		p_from = p_to; p_to += 4
		while len(header_cache) < p_to: header_cache += str(next(self._generator))
		number_of_reference_sequences = unpack('<i',header_cache[p_from:p_to])[0]
		
		for _ in range(number_of_reference_sequences):
			p_from = p_to; p_to += 4
			while len(header_cache) < p_to: header_cache += next(self._generator)
			l_name = unpack('<l',header_cache[p_from:p_to])[0]
			p_from = p_to; p_to += l_name
			while len(header_cache) < p_to: header_cache += next(self._generator)
			self.file_chromosomes.append(header_cache[p_from:p_to -1].decode('ascii'))
			p_from = p_to; p_to += 4
			while len(header_cache) < p_to: header_cache += next(self._generator)
			self.file_chromosome_lengths[self.file_chromosomes[-1]] = unpack('<l',header_cache[p_from:p_to])[0]

		self.file_bytes_read = p_to
		self.file_binary_header = memoryview(header_cache[:p_to])
		header_cache = header_cache[p_to:]

		
		# A quick check to make sure the header of this BAM file makes sense:
		chromosomes_from_header = []
		for line in str(self.file_header).split('\\n'):
			if line.startswith('@SQ\\tSN:'):
				chromosomes_from_header.append(line.split('\\t')[1][3:])
		if chromosomes_from_header != self.file_chromosomes:
			raise PybamWarn('For some reason the BAM format stores the chromosome names in two locations,\n	   the ASCII text header we all know and love, viewable with samtools view -H, and another special binary header\n	   which is used to translate the chromosome refID (a number) into a chromosome RNAME when you do bam -> sam.\n\nThese two headers should always be the same, but apparently they are not:\nThe ASCII header looks like: ' + self.file_header + '\nWhile the binary header has the following chromosomes: ' + self.file_chromosomes + '\n')
				
		#HL - decoding header
		self.file_header = self.file_header.decode()
	
		
		## Variable parsing:
		def new_entry(header_cache):
			cache = header_cache # we keep a small cache of X bytes of decompressed BAM data, to smoothen out disk access.
			p = 0 # where the next alignment/entry starts in the cache
			while True:
				try:
					while len(cache) < p + 4: cache = cache[p:] + next(self._generator); p = 0 # Grab enough bytes to parse blocksize
					self.sam_block_size  = unpack('<i',cache[p:p+4])[0]
					self.file_alignments_read += 1
					while len(cache) < p + 4 + self.sam_block_size:
						cache = cache[p:] + next(self._generator); p = 0 # Grab enough bytes to parse entry
				except StopIteration: break
				self.bam = cache[p:p + 4 + self.sam_block_size]
				p = p + 4 + self.sam_block_size
				yield self
		self._new_entry = new_entry(header_cache)
		
		

		def compile_parser(self,fields):
			temp_code = ''
			end_of_qname = False
			end_of_cigar = False
			end_of_seq = False
			end_of_qual = False
			dependencies = set(fields)

			if 'bam' in fields:
				fields[fields.index('bam')] = 'self.bam'

			if 'sam_block_size' in fields:
				fields[fields.index('sam_block_size')] = 'self.sam_block_size'

			if 'sam'				  in dependencies:
				dependencies.update(['sam_qname','sam_flag','sam_rname','sam_pos1','sam_mapq','sam_cigar_string','bam_refID','bam_next_refID','sam_rnext','sam_pnext1','sam_tlen','sam_seq','sam_qual','sam_tags_string'])

			if 'sam_tags_string'	  in dependencies:
				dependencies.update(['sam_tags_list'])

			if 'sam_pos1' in dependencies:
				temp_code += "\n		sam_pos1 = (0 if sam_pos0 < 0 else sam_pos0 + 1)"
				dependencies.update(['sam_pos0'])

			if 'sam_pnext1' in dependencies:
				temp_code += "\n		sam_pnext1 = (0 if sam_pnext0 < 0 else sam_pnext0 + 1)"
				dependencies.update(['sam_pnext0'])

			if 'sam_qname' in dependencies or 'bam_qname' in dependencies:
				temp_code += "\n		_end_of_qname = 36 + sam_l_read_name"
				dependencies.update(['sam_l_read_name'])
				end_of_qname = True

			if 'sam_cigar_string' in dependencies or 'sam_cigar_list' in dependencies or 'bam_cigar' in dependencies:
				if end_of_qname:
					pass
				else:
					temp_code += "\n		_end_of_qname = 36 + sam_l_read_name"
				temp_code += "\n		_end_of_cigar = _end_of_qname + (4*sam_n_cigar_op)"
				dependencies.update(['sam_l_read_name','sam_n_cigar_op'])
				end_of_cigar = True

			if 'sam_seq' in dependencies or 'bam_seq' in dependencies:
				if end_of_cigar:
					pass
				elif end_of_qname:
					temp_code += "\n		_end_of_cigar = _end_of_qname + (4*sam_n_cigar_op)"
				else:
					temp_code += "\n		_end_of_cigar = 36 + sam_l_read_name + (4*sam_n_cigar_op)"
				temp_code += "\n		_end_of_seq = _end_of_cigar + (-((-sam_l_seq)//2))"
				dependencies.update(['sam_l_seq','sam_n_cigar_op','sam_l_read_name'])
				end_of_seq = True

			if 'sam_qual' in dependencies or 'bam_qual' in dependencies:
				if end_of_seq:
					pass
				elif end_of_cigar:
					temp_code += "\n		_end_of_seq   = _end_of_cigar + (-((-sam_l_seq)//2))"
				elif end_of_qname:
					temp_code += "\n		_end_of_seq   = _end_of_qname + (4*sam_n_cigar_op) + (-((-sam_l_seq)//2))"
				else:
					temp_code += "\n		_end_of_seq   = 36 + sam_l_read_name + (4*sam_n_cigar_op) + (-((-sam_l_seq)//2))"
				temp_code += "\n		_end_of_qual = _end_of_seq + sam_l_seq"
				dependencies.update(['sam_l_seq','sam_n_cigar_op','sam_l_read_name'])
				end_of_qual = True

			if 'sam_tags_list' in dependencies or 'bam_tags' in dependencies:
				if end_of_qual:
					pass
				elif end_of_seq:
					temp_code += "\n		_end_of_qual = _end_of_seq + sam_l_seq"
				elif end_of_cigar:
					temp_code += "\n		_end_of_qual = _end_of_cigar + (-((-sam_l_seq)//2)) + sam_l_seq"
				elif end_of_qname:
					temp_code += "\n		_end_of_qual = _end_of_qname + (4*sam_n_cigar_op) + (-((-sam_l_seq)//2)) + sam_l_seq"
				else:
					temp_code += "\n		_end_of_qual = 36 + sam_l_read_name + (4*sam_n_cigar_op) + (-((-sam_l_seq)//2)) + sam_l_seq"
				dependencies.update(['sam_l_seq','sam_n_cigar_op','sam_l_read_name'])

			if 'sam_rname'	   in dependencies:
				temp_code += "\n		sam_rname = '*' if sam_refID < 0 else self.file_chromosomes[sam_refID]"
				dependencies.update(['sam_refID'])

			if 'sam_rnext'	   in dependencies:
				temp_code += "\n		sam_rnext = '*' if sam_next_refID < 0 else self.file_chromosomes[sam_next_refID]"
				dependencies.update(['sam_next_refID'])

			## First we figure out what data from the static portion of the BAM entry we'll need:
			tmp = {}
			tmp['code'] = 'def parser(self):\n	from array import array\n	from struct import unpack\n	for _ in self._new_entry:'
			tmp['last_start'] = None
			tmp['name_list']  = []
			tmp['dtype_list'] = []
			def pack_up(name,dtype,length,end,tmp):
				if name in dependencies:
					if tmp['last_start'] is None:
						tmp['last_start'] = end - length
					tmp['name_list'].append(name)
					tmp['dtype_list'].append(dtype)
				elif tmp['last_start'] is not None:
					tmp['code'] += '\n		' + ', '.join(tmp['name_list']) + ' = unpack("<' + ''.join(tmp['dtype_list']) + '",self.bam[' + str(tmp['last_start']) + ':' + str(end-length) + '])'
					if len(tmp['dtype_list']) == 1:
						tmp['code'] += '[0]'
					tmp['last_start'] = None
					tmp['name_list']  = []
					tmp['dtype_list'] = []

			pack_up('sam_refID',	   'i',4, 8,tmp)
			pack_up('sam_pos0',		'i',4,12,tmp)
			pack_up('sam_l_read_name', 'B',1,13,tmp)
			pack_up('sam_mapq',		'B',1,14,tmp)
			pack_up('sam_bin',		 'H',2,16,tmp)
			pack_up('sam_n_cigar_op',  'H',2,18,tmp)
			pack_up('sam_flag',		'H',2,20,tmp)
			pack_up('sam_l_seq',	   'i',4,24,tmp)
			pack_up('sam_next_refID',  'i',4,28,tmp)
			pack_up('sam_pnext0',	  'i',4,32,tmp)
			pack_up('sam_tlen',		'i',4,36,tmp)
			pack_up( None,			None,0,36,tmp) # To add anything not yet added.
			code = tmp['code']
			del tmp

			code += temp_code

			# Fixed-length BAM data (where we just grab the bytes, we dont unpack) can, however, be grabbed individually.
			if 'bam_block_size'  in dependencies: code += "\n		bam_block_size   = self.bam[0			 : 4				]"
			if 'bam_refID'	   in dependencies: code += "\n		bam_refID		= self.bam[4			 : 8				]"
			if 'bam_pos'		 in dependencies: code += "\n		bam_pos		  = self.bam[8			 : 12			   ]"
			if 'bam_l_read_name' in dependencies: code += "\n		bam_l_read_name  = self.bam[12			: 13			   ]"
			if 'bam_mapq'		in dependencies: code += "\n		bam_mapq		 = self.bam[13			: 14			   ]"
			if 'bam_bin'		 in dependencies: code += "\n		bam_bin		  = self.bam[14			: 16			   ]"
			if 'bam_n_cigar_op'  in dependencies: code += "\n		bam_n_cigar_op   = self.bam[16			: 18			   ]"
			if 'bam_flag'		in dependencies: code += "\n		bam_flag		 = self.bam[18			: 20			   ]"
			if 'bam_l_seq'	   in dependencies: code += "\n		bam_l_seq		= self.bam[20			: 24			   ]"
			if 'bam_next_refID'  in dependencies: code += "\n		bam_next_refID   = self.bam[24			: 28			   ]"
			if 'bam_pnext'	   in dependencies: code += "\n		bam_pnext		= self.bam[28			: 32			   ]"
			if 'bam_tlen'		in dependencies: code += "\n		bam_tlen		 = self.bam[32			: 36			   ]"
			if 'bam_qname'	   in dependencies: code += "\n		bam_qname		= self.bam[36			: _end_of_qname	]"
			if 'bam_cigar'	   in dependencies: code += "\n		bam_cigar		= self.bam[_end_of_qname : _end_of_cigar	]"
			if 'bam_seq'		 in dependencies: code += "\n		bam_seq		  = self.bam[_end_of_cigar : _end_of_seq	  ]"
			if 'bam_qual'		in dependencies: code += "\n		bam_qual		 = self.bam[_end_of_seq   : _end_of_qual	 ]"
			if 'bam_tags'		in dependencies: code += "\n		bam_tags		 = self.bam[_end_of_qual  :				  ]"

			if 'sam_qname'	   in dependencies:
				if 'bam_qname'   in dependencies: code += "\n		sam_qname		= bam_qname[:-1]"
				else:							 code += "\n		sam_qname		= self.bam[36			: _end_of_qname -1 ]"

			if 'sam_cigar_list'  in dependencies:
				if 'bam_cigar'   in dependencies: code += "\n		sam_cigar_list = [( cig >> 4  , cigar_codes[cig & 0b1111]) for cig in array('I', bam_cigar) ]"
				else:							 code += "\n		sam_cigar_list = [( cig >> 4  , cigar_codes[cig & 0b1111]) for cig in array('I', self.bam[_end_of_qname : _end_of_cigar]) ]"

			if 'sam_cigar_string'in dependencies:
				if 'bam_cigar'   in dependencies: code += "\n		sam_cigar_string = ''.join([		str(cig >> 4) + cigar_codes[cig & 0b1111] for cig	 in array('I', bam_cigar)])"
				else:							 code += "\n		sam_cigar_string = ''.join([		str(cig >> 4) + cigar_codes[cig & 0b1111] for cig	 in array('I', self.bam[_end_of_qname : _end_of_cigar]) ])"

			if 'sam_seq'		 in dependencies:
				if 'bam_seq'	 in dependencies: code += "\n		sam_seq = ''.join( [ dna_codes[dna >> 4] + dna_codes[dna & 0b1111]   for dna	 in array('B', bam_seq)])[:sam_l_seq]"
				else:							 code += "\n		sam_seq = ''.join( [ dna_codes[dna >> 4] + dna_codes[dna & 0b1111]   for dna	 in array('B', self.bam[_end_of_cigar : _end_of_seq])])[:sam_l_seq]"

			if 'sam_qual'		in dependencies:
				if 'bam_qual'	in dependencies: code += "\n		sam_qual = b''.join( [				   chr(ord(quality) + 33)		for quality in			bam_qual ])"
				else:							 code += "\n		sam_qual = b''.join( [				   chr(ord(quality) + 33)		for quality in			self.bam[_end_of_seq	   : _end_of_qual  ]])"

			if 'sam_tags_list'		in dependencies:
				code += '''
		sam_tags_list = []
		offset = _end_of_qual
		while offset != len(self.bam):
			tag_name = self.bam[offset:offset+2]
			tag_type = self.bam[offset+2]
			if tag_type == 'Z':
				offset_end = self.bam.index('\\0',offset+3)+1
				tag_data = self.bam[offset+3:offset_end-1]
			elif tag_type in CtoPy:
				offset_end = offset+3+py4py[tag_type]
				tag_data = unpack(CtoPy[tag_type],self.bam[offset+3:offset_end])[0]
			elif tag_type == 'B':
				offset_end = offset+8+(unpack('<i',self.bam[offset+4:offset+8])[0]*py4py[self.bam[offset+3]])
				tag_data = array(self.bam[offset+3] , self.bam[offset+8:offset_end] )
			else:
				print 'PYBAM ERROR: I dont know how to parse BAM tags in this format: ',repr(tag_type)
				print '			 This is simply because I never saw this kind of tag during development.'
				print '			 If you could mail the following chunk of text to john at john.uk.com, i will fix this up for everyone :)'
				print repr(tag_type),repr(self.bam[offset+3:end])
				exit()
			sam_tags_list.append((tag_name,tag_type,tag_data))
			offset = offset_end'''

			if 'sam_tags_string'	  in dependencies:
				code += "\n		sam_tags_string = '\t'.join(A + ':' + ('i' if B in 'cCsSI' else B)  + ':' + ((C.typecode + ',' + ','.join(map(str,C))) if type(C)==array else str(C)) for A,B,C in self.sam_tags_list)"

			if 'sam'				  in dependencies:
				code += "\n		sam = sam_qname + '\t' + str(sam_flag) + '\t' + sam_rname + '\t' + str(sam_pos1) + '\t' + str(sam_mapq) + '\t' + ('*' if sam_cigar_string == '' else sam_cigar_string) + '\t' + ('=' if bam_refID == bam_next_refID else sam_rnext) + '\t' + str(sam_pnext1) + '\t' + str(sam_tlen) + '\t' + sam_seq + '\t' + sam_qual + '\t' + sam_tags_string"

			code += '\n		yield ' + ','.join([x for x in fields]) + '\n'

			self._static_parser_code = code # "code" is the static parser's code as a string (a function called "parser")
			exec_dict = {				   # This dictionary stores things the exec'd code needs to know about, and will store the compiled function after exec()
				'unpack':unpack,
				'array':array,
				'dna_codes':dna_codes,
				'CtoPy':CtoPy,
				'py4py':py4py,
				'cigar_codes':cigar_codes
			}
			exec(code, exec_dict)			# exec() compiles "code" to real code, creating the "parser" function and adding it to exec_dict['parser']
			return(exec_dict['parser'])

		if fields:
			static_parser = compile_parser(self,fields)(self)
			def next_read(): return next(self._new_entry)
		else:
			def next_read(): return next(self._new_entry)					
		self.next = next_read
		
	def __next__(self):
		return next(self._new_entry)

	def __iter__(self): return self
	def __str__(self):  return self.sam

	## Methods to pull out raw bam data from entry (so still in its binary encoding). This can be helpful in some scenarios.
	@property
	def bam_block_size(self):   return			   self.bam[						: 4						 ] 
	@property
	def bam_refID(self):		return			   self.bam[ 4					  : 8						 ] 
	@property
	def bam_pos(self):		  return			   self.bam[ 8					  : 12						]
	@property
	def bam_l_read_name(self):  return			   self.bam[ 12					 : 13						] 
	@property
	def bam_mapq(self):		 return			   self.bam[ 13					 : 14						] 
	@property
	def bam_bin(self):		  return			   self.bam[ 14					 : 16						] 
	@property
	def bam_n_cigar_op(self):   return			   self.bam[ 16					 : 18						] 
	@property
	def bam_flag(self):		 return			   self.bam[ 18					 : 20						] 
	@property
	def bam_l_seq(self):		return			   self.bam[ 20					 : 24						] 
	@property
	def bam_next_refID(self):   return			   self.bam[ 24					 : 28						] 
	@property
	def bam_pnext(self):		return			   self.bam[ 28					 : 32						] 
	@property
	def bam_tlen(self):		 return			   self.bam[ 32					 : 36						] 
	@property
	def bam_qname(self):		return			   self.bam[ 36					 : self._end_of_qname		] 
	@property
	def bam_cigar(self):		return			   self.bam[ self._end_of_qname	 : self._end_of_cigar		] 
	@property
	def bam_seq(self):		  return			   self.bam[ self._end_of_cigar	 : self._end_of_seq		  ] 
	@property
	def bam_qual(self):		 return			   self.bam[ self._end_of_seq	   : self._end_of_qual		 ] 
	@property
	def bam_tags(self):		 return			   self.bam[ self._end_of_qual	  :						   ] 

	@property
	def sam_refID(self):		return unpack( '<i', self.bam[ 4					  :  8						] )[0]
	@property
	def sam_pos0(self):		 return unpack( '<i', self.bam[ 8					  : 12						] )[0]
	@property
	def sam_l_read_name(self):  return unpack( '<B', self.bam[ 12					 : 13						] )[0]
	@property
	def sam_mapq(self):		 return unpack( '<B', self.bam[ 13					 : 14						] )[0]
	@property
	def sam_bin(self):		  return unpack( '<H', self.bam[ 14					 : 16						] )[0]
	@property
	def sam_n_cigar_op(self):   return unpack( '<H', self.bam[ 16					 : 18						] )[0]
	@property
	def sam_flag(self):		 return unpack( '<H', self.bam[ 18					 : 20						] )[0]
	@property
	def sam_l_seq(self):		return unpack( '<i', self.bam[ 20					 : 24						] )[0]
	@property
	def sam_next_refID(self):   return unpack( '<i', self.bam[ 24					 : 28						] )[0]
	@property
	def sam_pnext0(self):	   return unpack( '<i', self.bam[ 28					 : 32						] )[0]
	@property
	def sam_tlen(self):		 return unpack( '<i', self.bam[ 32					 : 36						] )[0]
	@property
	def sam_qname(self):		return			   self.bam[ 36					 : self._end_of_qname -1	 ].decode() # -1 to remove trailing NUL byte
	@property
	def sam_cigar_list(self):   return		  [		  (cig >> 4  , cigar_codes[cig & 0b1111] ) for cig	 in array('I', self.bam[self._end_of_qname	 : self._end_of_cigar ])]
	@property
	def sam_cigar_string(self): return ''.join( [	   str(cig >> 4) + cigar_codes[cig & 0b1111]   for cig	 in array('I', self.bam[self._end_of_qname	 : self._end_of_cigar ])])
	@property
	def sam_seq(self):		  return ''.join( [ dna_codes[dna >> 4] +   dna_codes[dna & 0b1111]   for dna	 in array('B', self.bam[self._end_of_cigar	 : self._end_of_seq   ])])[:self.sam_l_seq] # As DNA is 4 bits packed 2-per-byte, there might be a trailing '0000', so we can either
	@property
	def sam_qual(self):  
		return ''.join( [					  chr(quality + 33)	   for quality in			self.bam[self._end_of_seq	   : self._end_of_qual  ]])
	@property
	def sam_tags_list(self):
		result = []
		offset = self._end_of_qual
		while offset != len(self.bam):
			tag_name = self.bam[offset:offset+2].decode()
			tag_type = chr(self.bam[offset+2])			
			if tag_type == 'Z':
				offset_end = self.bam.index(b'\x00',offset+3)+1
				tag_data = self.bam[offset+3:offset_end-1].decode()
			elif tag_type in CtoPy:
				offset_end = offset+3+py4py[tag_type]
				tag_data = unpack(CtoPy[tag_type],self.bam[offset+3:offset_end])[0]
			elif tag_type == 'B':
				offset_end = offset+8+(unpack('<i',self.bam[offset+4:offset+8])[0]*py4py[self.bam[offset+3]])
				tag_data = array(self.bam[offset+3] , self.bam[offset+8:offset_end] )
			else:
				print('PYBAM ERROR: I dont know how to parse BAM tags in this format: ',repr(tag_type))
				print('			 This is simply because I never saw this kind of tag during development.')
				print('			 If you could mail the following chunk of text to john at john.uk.com, ill fix this up :)')
				print(repr(tag_type),repr(self.bam[offset+3:end]))
				exit()
			result.append((tag_name,tag_type,tag_data))
			offset = offset_end
		return result
	@property
	def sam_tags_string(self):
		return '\t'.join(A + ':' + ('i' if B in 'cCsSI' else B)  + ':' + ((C.typecode + ',' + ','.join(map(str,C))) if type(C)==array else str(C)) for A,B,C in self.sam_tags_list)	

	## BONUS methods - methods that mimic how samtools works.
	@property
	def sam_pos1(self):		 return  0  if self.sam_pos0 < 0 else self.sam_pos0 + 1
	@property
	def sam_pnext1(self):	   return  0  if self.sam_pnext0 < 0 else self.sam_pnext0 + 1
	@property
	def sam_rname(self):		return '*' if self.sam_refID	  < 0 else self.file_chromosomes[self.sam_refID	 ]
	@property
	def sam_rnext(self):		return '*' if self.sam_next_refID < 0 else self.file_chromosomes[self.sam_next_refID]
	@property
	def sam(self):		return (
			self.sam_qname													 + '\t' +
			str(self.sam_flag)												 + '\t' +
			self.sam_rname													 + '\t' +
			str(self.sam_pos1)												 + '\t' +
			str(self.sam_mapq)												 + '\t' +
			('*' if self.sam_cigar_string == '' else self.sam_cigar_string)	+ '\t' +
			('=' if self.bam_refID == self.bam_next_refID else self.sam_rnext) + '\t' +
			str(self.sam_pnext1)											   + '\t' +
			str(self.sam_tlen)												 + '\t' +
			self.sam_seq													   + '\t' + 
			self.sam_qual													  + '\t' +
			self.sam_tags_string
		)

	## Internal methods - methods used to calculate where variable-length blocks start/end
	@property
	def _end_of_qname(self):	 return self.sam_l_read_name   + 36						# fixed-length stuff at the beginning takes up 36 bytes.
	@property
	def _end_of_cigar(self):	 return self._end_of_qname	 + (4*self.sam_n_cigar_op)   # 4 bytes per n_cigar_op
	@property
	def _end_of_seq(self):	   return self._end_of_cigar	 + (-((-self.sam_l_seq)//2)) # {blurgh}
	@property
	def _end_of_qual(self):	  return self._end_of_seq	   + self.sam_l_seq			# qual has the same length as seq

	def __del__(self):
		if self._subprocess.returncode is None: self._subprocess.kill()
		self._file.close()

class PybamWarn(Exception): pass
class PybamError(Exception): pass

global bin_width 
bin_width = 250
global bin_height
bin_height = 0.1

	
def detect_fasta(file):
	fh = open(file, "r")
	
	fmt_fine = True
	for i in range(0, 30):
		try:
			line = fh.readline()
		except:
			fmt_fine = False
			break
		if not line.startswith(">"):
			if not set(line) <= set("ATCGatcgNn\n"):
				fmt_fine = False
	fh.close()
	
	return(fmt_fine)
	
def detect_bam(file):
	fh = open(file, "rb")
	
	fmt_fine = True
	
	head = fh.read(4)
	
	if head != b'BAM\1' and head != b"\x1f\x8b\x08\x04":
		fmt_fine = False
	
	fh.close()
	
	return(fmt_fine)
	
def detect_blast(file):
	fh = open(file, "r")
	
	fmt_fine = True

	try:
		line = fh.readline().strip()
	except:
		fmt_fine = False
	else:
		while line.startswith("#"):
			line = fh.readline().strip()
		segment = line.split()
		if len(segment) < 9:
			fmt_fine = False
		else:
			if segment[8].isnumeric() and segment[9].isnumeric():
				fmt_fine = True
			else:
				fmt_fine = False
	
	fh.close()
	
	return(fmt_fine)
	
def detect_sam(file):
	fh = open(file, "r")
	
	fmt_fine = True
	
	try:
		line = fh.readline()
	except :
		fmt_fine = False
	else:
		if line.startswith("@"):
			pass
		else:
			fmt_fine = False
	
	fh.close()
	
	return(fmt_fine)

def detect_is_prodigal(file):
	fh = open(file, "r")
	
	fmt_fine = True
	
	try:
		line = fh.readline()
	except :
		fmt_fine = False
	else:
		if line.startswith("##gff-version"):
			pass
		else:
			fmt_fine = False
	
	fh.close()
	
	return(fmt_fine)
	
def detect_file_format(file):
	detected_format = "none"
	
	#I don't know how this could happen, but good to have it in place?
	toomuch = 0
	
	#If the user supplies a mismatch file, then this will run. Otw, we should only run the requested check to avoid excess effort.
	isfasta = detect_fasta(file)
	isbam = detect_bam(file)
	issam = detect_sam(file)
	isblast = detect_blast(file)
	isprodigalgff = detect_is_prodigal(file)
		
	if isfasta:
		detected_format = "fasta"
		toomuch += 1
	if isbam:
		detected_format = "bam"
		toomuch += 1
	if issam:
		detected_format = "sam"
		toomuch += 1
	if isblast:
		detected_format = "blast"
		toomuch += 1
	if(isprodigalgff):
		detected_format = "genes"
		toomuch += 1
	if toomuch > 1:
		detected_format = "none"
		
	return(detected_format)

def convert_array(bytestring):
	return np.frombuffer(bytestring, dtype = np.int32)

def parse_blast(blast_record):
	if blast_record.startswith("#"):
		return None
	try:
		blast_record = blast_record.strip().split()
		#Outfmt 6 - query, target, %ID, aln length, mismatch, query aln st, query aln end, target aln start (the interesting one), target aln end, e-value, bit score
		#outfmt6 doesn't include seqlen.
		#read_ID, contig, matches, seqlen, alignment_length, h_bins, counts
		read_ID, contig, local_pct_id, align_start, align_end = blast_record[0], blast_record[1], float(blast_record[2]), int(blast_record[6]), int(blast_record[7])
		#This SHOULD produce the count of matches.
		
		#print(read_ID, contig, local_pct_id, align_start, align_end)
		
		if align_start < align_end:
			align_length = (align_end-align_start) + 1
		else:
			align_length = (align_start-align_end) + 1
		
		if local_pct_id != 100:
			matches = int(align_length*local_pct_id/100)						
		else:
			#No need to calc num matches for perfect matches.
			matches = align_length
			
			
		aln_start = min(int(blast_record[8]), int(blast_record[9]))
		#rel_pos = aln_start - (bin_width * (aln_start//bin_width))
			
		#Gotta figure out hbins, counts now.
		starts, ends = [], []
		
		bases_to_add = align_length
		
		#We can't detect gap locations in BLAST reads so we are slightly limited, here.
		starts.append(aln_start)
		ends.append(aln_start + bases_to_add - 1)
		
		starts = np.array(starts, dtype=np.int32)
		ends = np.array(ends, dtype=np.int32)
		starts = starts.tobytes()
		ends = ends.tobytes()
		
		results = [read_ID, contig, matches, None, align_length, starts, ends]
	except:
		results = None
		
	return results
	
def parse_sam_save(sam_record):
	if "MD:Z:" in sam_record:
		sam_record = sam_record.strip().split()
		
		#We adjust the aln start to be zero indexed.
		read_ID, contig, aln_start, cigar = sam_record[0], sam_record[2], int(sam_record[3]) -1 , sam_record[5]
		
		#Unal.
		if contig is None or contig == "":
			return None
		
		rel_pos = aln_start - (bin_width * (aln_start//bin_width))
		
		iter = len(sam_record)-1
		mdz_seg = sam_record[iter]
		# If it's not the correct field, proceed until it is.
		while not mdz_seg.startswith("MD:Z:"):
			iter -= 1
			mdz_seg = sam_record[iter]
		#Remove the MD:Z: flag from the start
		mdz_seg = mdz_seg[5:]
		
		match_count = re.findall('[0-9]+', mdz_seg)
		matches = 0
		for num in match_count:
			matches += int(num)
		
		starts = []
		ends = []
		#h_bins = []
		#counts = []
		
		alignment_length = 0
		for cigar_op in re.findall(r"([0-9]+)([a-z]+)", cigar, re.I):
			if cigar_op[1] == "M" or cigar_op[1] == "X" or cigar_op[1] == "=":
				cigar_value = int(cigar_op[0])
				alignment_length += cigar_value
				
				#Add an alignment to the bin.
				if rel_pos + cigar_value < bin_width:
					#h_bins.append(aln_start//bin_width)
					#counts.append(cigar_op[0])
					starts.append(aln_start)
					ends.append(aln_start + cigar_value)
					#segments.append((aln_start, aln_start + cigar_value))
					aln_start += cigar_value
					rel_pos   += cigar_value
					#This is a rollover. It shouldn't actually be able to happen in these cases
					#if rel_pos = bin_width:
					#	rel_pos = 0
				#A match spills over into the next bin and needs to be split.
				else:
					bp_left = cigar_value
					while bp_left > 0:
						#How far to the end? Right side of bin is non-inclusive.
						to_end = bin_width - rel_pos
						if to_end > bp_left:
							#h_bins.append(aln_start//bin_width)
							#counts.append(bp_left)
							starts.append(aln_start)
							ends.append(aln_start + bp_left - 1)
							aln_start += bp_left
							rel_pos   += bp_left
							bp_left = 0
						else:
							starts.append(aln_start)
							ends.append(aln_start + to_end - 1)
							#h_bins.append(aln_start//bin_width)
							#counts.append(to_end)
							bp_left -= to_end
							aln_start += to_end
							#A rollover should always reset to zero.
							rel_pos  = 0
					
			#Advance the position in the genome, but do not add.
			if cigar_op[1] == "D":
				cigar_value = int(cigar_op[0])
				aln_start += cigar_value
				rel_pos += cigar_value
				#Rollover to next bin.
				if rel_pos >= bin_width:
					rel_pos -= bin_width
		
		#Includes insertions
		seqlen = len(sam_record[9])
		
		#first, last = starts[0], ends[len(ends)-1]
		
		#starts = np.array(starts, dtype = np.int32)
		#starts = starts.tobytes()
		#ends = np.array(ends, dtype = np.int32)
		#ends = ends.tobytes()	
		
		starts = np.array(starts, dtype=np.int32)
		ends = np.array(ends, dtype=np.int32)
		starts = starts.tobytes()
		ends = ends.tobytes()
		#h_bins = np.array(h_bins, dtype = np.int32)
		#h_bins = h_bins.tobytes()
		#counts = np.array(counts, dtype = np.int32)
		#counts = counts.tobytes()
		
		return [read_ID, contig, matches, seqlen, alignment_length, starts, ends]

	#Default behavior, i.e. "MD:Z:" not present.	
	return None


def parse_bam_save(bam_record):
	mdz_seg = ""

	for a,b,c in bam_record.sam_tags_list:
		if a == "MD":
			mdz_seg = c
			
	if mdz_seg == "":
		return None
	else:
		
		#I should reframe this to return lists of contributions to buckets.
		#Buckets are defined every 250 bp and 0.1 %ID. Each read can only be in one %ID bin, but can span width buckets.

		read_ID = bam_record.sam_qname
		contig = bam_record.sam_rname
		
		#Unal.
		if contig is None or contig == "":
			return None
		
		aln_start = bam_record.sam_pos0
		rel_pos = aln_start - (bin_width * (aln_start//bin_width))
		
		match_count = re.findall('[0-9]+', mdz_seg)
		
		#this is the count of matching bases for pct ID
		matches = 0
		for num in match_count:
			matches += int(num)
			
		#Keeps track of the starts, ends of the current read as it aligns to the genome.
		starts = []
		ends = []
		#h_bins = []
		#counts = []
		
		alignment_length = 0
		for cigar_op in bam_record.sam_cigar_list:
			if cigar_op[1] == "M" or cigar_op[1] == "X" or cigar_op[1] == "=":
				alignment_length += cigar_op[0]
				'''
				starts.append(aln_start)
				ends.append(aln_start + cigar_op[0])
				#segments.append((aln_start, aln_start + cigar_op[0]))
				aln_start += cigar_op[0]
				rel_pos   += cigar_op[0]
				'''
				
				#Add an alignment to the bin.
				if rel_pos + cigar_op[0] < bin_width:
					#h_bins.append(aln_start//bin_width)
					#counts.append(cigar_op[0])
					starts.append(aln_start)
					ends.append(aln_start + cigar_op[0])
					#segments.append((aln_start, aln_start + cigar_op[0]))
					aln_start += cigar_op[0]
					rel_pos   += cigar_op[0]
					#This is a rollover. It shouldn't actually be able to happen in these cases
					#if rel_pos = bin_width:
					#	rel_pos = 0
				#A match spills over into the next bin and needs to be split.
				else:
					bp_left = cigar_op[0]
					while bp_left > 0:
						#How far to the end? Right side of bin is non-inclusive.
						to_end = bin_width - rel_pos
						if to_end > bp_left:
							#h_bins.append(aln_start//bin_width)
							#counts.append(bp_left)
							
							starts.append(aln_start)
							ends.append(aln_start + bp_left - 1)
							
							aln_start += bp_left
							rel_pos   += bp_left
							bp_left = 0
						else:
							starts.append(aln_start)
							ends.append(aln_start + to_end - 1)
							
							#h_bins.append(aln_start//bin_width)
							#counts.append(to_end)
							#segments.append((aln_start, aln_start + to_end - 1))
							#print(aln_start, rel_pos, to_end, "before", bp_left, "after", bp_left - to_end)
							bp_left -= to_end
							aln_start += to_end
							#A rollover should always reset to zero.
							rel_pos  = 0
					
			#Advance the position in the genome, but do not add.
			if cigar_op[1] == "D":
				aln_start += cigar_op[0]
				rel_pos += cigar_op[0]
				#Rollover to next bin.
				if rel_pos >= bin_width:
					rel_pos -= bin_width
		
		#Includes insertions
		seqlen = bam_record.sam_l_seq
		
		
		starts = np.array(starts, dtype=np.int32)
		ends = np.array(ends, dtype=np.int32)
		starts = starts.tobytes()
		ends = ends.tobytes()
		#h_bins = np.array(h_bins, dtype = np.int32)
		#h_bins = h_bins.tobytes()
		#counts = np.array(counts, dtype = np.int32)
		#counts = counts.tobytes()
		
		return [read_ID, contig, matches, seqlen, alignment_length, starts, ends]

	
def parse_sam(sam_record):
	if "MD:Z:" in sam_record:
		sam_record = sam_record.strip().split()
		
		#We adjust the aln start to be zero indexed.
		read_ID, contig, aln_start, cigar = sam_record[0], sam_record[2], int(sam_record[3]) -1 , sam_record[5]
		
		#Unal.
		if contig is None or contig == "":
			return None
		
		rel_pos = aln_start - (bin_width * (aln_start//bin_width))
		
		iter = len(sam_record)-1
		mdz_seg = sam_record[iter]
		# If it's not the correct field, proceed until it is.
		while not mdz_seg.startswith("MD:Z:"):
			iter -= 1
			mdz_seg = sam_record[iter]
		#Remove the MD:Z: flag from the start
		mdz_seg = mdz_seg[5:]
		
		match_count = re.findall('[0-9]+', mdz_seg)
		matches = 0
		for num in match_count:
			matches += int(num)
		
		starts = []
		ends = []
		#h_bins = []
		#counts = []
		
		alignment_length = 0
		for cigar_op in re.findall(r"([0-9]+)([a-z]+)", cigar, re.I):
			if cigar_op[1] == "M" or cigar_op[1] == "X" or cigar_op[1] == "=":
				cigar_value = int(cigar_op[0])
				alignment_length += cigar_value
				
				starts.append(aln_start)
				ends.append(aln_start + cigar_value)
				#segments.append((aln_start, aln_start + cigar_value))
				aln_start += cigar_value
					
			#Advance the position in the genome, but do not add.
			if cigar_op[1] == "D":
				cigar_value = int(cigar_op[0])
				aln_start += cigar_value

		#Includes insertions
		seqlen = len(sam_record[9])
		
		starts = np.array(starts, dtype=np.int32)
		ends = np.array(ends, dtype=np.int32)
		starts = starts.tobytes()
		ends = ends.tobytes()
		
		return [read_ID, contig, matches, seqlen, alignment_length, starts, ends]

	#Default behavior, i.e. "MD:Z:" not present.	
	return None

	
def parse_bam(bam_record):
	mdz_seg = ""

	for a,b,c in bam_record.sam_tags_list:
		if a == "MD":
			mdz_seg = c
			
	if mdz_seg == "":
		return None
	else:
		
		#I should reframe this to return lists of contributions to buckets.
		#Buckets are defined every 250 bp and 0.1 %ID. Each read can only be in one %ID bin, but can span width buckets.

		read_ID = bam_record.sam_qname
		contig = bam_record.sam_rname
		
		#Unal.
		if contig is None or contig == "":
			return None
		
		aln_start = bam_record.sam_pos0
		
		match_count = re.findall('[0-9]+', mdz_seg)
		
		#this is the count of matching bases for pct ID
		matches = 0
		for num in match_count:
			matches += int(num)
			
		#Keeps track of the starts, ends of the current read as it aligns to the genome.
		starts = []
		ends = []
		#h_bins = []
		#counts = []
		
		alignment_length = 0
		for cigar_op in bam_record.sam_cigar_list:
			if cigar_op[1] == "M" or cigar_op[1] == "X" or cigar_op[1] == "=":
				alignment_length += cigar_op[0]
				
				starts.append(aln_start)
				ends.append(aln_start + cigar_op[0])
				#segments.append((aln_start, aln_start + cigar_op[0]))
				aln_start += cigar_op[0]
				
			#Advance the position in the genome, but do not add.
			if cigar_op[1] == "D":
				aln_start += cigar_op[0]
				
		#Includes insertions
		seqlen = bam_record.sam_l_seq
		
		starts = np.array(starts, dtype=np.int32)
		ends = np.array(ends, dtype=np.int32)
		starts = starts.tobytes()
		ends = ends.tobytes()
		#h_bins = np.array(h_bins, dtype = np.int32)
		#h_bins = h_bins.tobytes()
		#counts = np.array(counts, dtype = np.int32)
		#counts = counts.tobytes()
		
		return [read_ID, contig, matches, seqlen, alignment_length, starts, ends]
	

	
	
#Functions for reading a sam/bam header to get seqlens.
def get_sam_header(file):
	lengths = {}
	fh = open(file, "r")
	
	for line in fh:
		#End of the header.
		if not line.startswith("@"):
			break
	
		if line.startswith("@SQ"):
			line = line.strip().split()
			seq = line[1][3:]
			len = int(line[2][3:])
			lengths[seq] = len
			
	fh.close()
	
	return lengths
	
def get_bam_header(file):
	lengths = {}
	fh = read(file)
	for line in fh.file_header.split('\n'):
		if line.startswith("@SQ"):
			line = line.strip().split()
			seq = line[1][3:]
			len = int(line[2][3:])
			lengths[seq] = len
			
	return lengths
	
	
#Function for stealing a header to write to output in filtering
def get_full_sam_header(file):
	lines = []
	fh = open(file, "r")
	
	for line in fh:
		if line.startswith("@"):
			lines.append(line.strip())
			
		else:
			break
	
	fh.close()
	
	return lines
	
def get_full_bam_header(file):
	
	fh = read(file)
	lines = fh.file_header.split('\n')
			
	return lines
		
		
		
#These two handle a file passed directly to recploteasy. 
class read_generator_iterator():
	def __init__(self, reader):
		self.reads_ = reader.input
		self.format_ = reader.format
		self.handle_ = None
		if self.format_ == "BLAST":
			self.handle_ = open(self.reads_, "r")
		if self.format_ == "SAM":
			self.handle_ = open(self.reads_, "r")
		if self.format_ == "BAM":
			self.handle_ = read(self.reads_)

		
	def __next__(self):
	
		if self.handle_ is None:
			raise StopIteration
			
		if self.format_ == "BLAST":
			line = self.handle_.readline()
			results = parse_blast(line)
			
		if self.format_ == "SAM":
			line = self.handle_.readline()
			results = parse_sam(line)
				
		if self.format_ == "BAM":
			line = self.handle_.next()
			results = parse_bam(line)
	
		#Ezpz EOF check
		if line:
			return results
		else:
			if self.format_ == "BLAST" or self.format_ == "SAM":
				self.handle_.close()
			raise StopIteration

class read_generator():
	def __init__(self, reads, format = None):
		self.input = reads
		self.format = format
		
	def __iter__(self):
		return read_generator_iterator(self)
		

#If reads are piped in, just pass them to a parser.
class piped_reads():
	def __init__(self, reads, format = None):
		self.input = reads
		self.format = format

class reads_database():
	def __init__(self, path, reads = None, genomes=None, format = None):
		self.path = path
		if reads is not None:
			self.input_reads = reads
		else:
			self.input_reads = None
		
		if genomes is not None:
			self.genomes = genomes
		else:
			self.genomes = None
			
		self.connection = None
		self.cursor = None
		
	#It's possible that reads or genomes may be the first call made to the DB
	#This makes sure the DB is ready, either way. Does nothing if the DB is active.
	def wake_up(self):
		if self.cursor is None:
			self.activate_connection()
			
	def check_valid(self):
		valid = False
		try:
			if os.path.exists(self.path):
				try:
					self.wake_up()
					#This only works if the genome_lengths table exists. I'm trusting nobody else has an SQLite3 db with this table name for this check.
					tabs = self.cursor.execute("SELECT name FROM sqlite_master").fetchall()
					for tab in tabs:
						if tab[0] == "genome_lengths":
							valid = True
							break
					self.close_connection()
				except:
					valid = False
		except:
			valid = False
			
		return valid
	
		
	def activate_connection(self, with_converter = True):
		# Converts np.array to TEXT when inserting
		##sqlite3.register_adapter(np.ndarray, adapt_array)
		#Converts byte string to numpy ndarray(int32) upon read from DB.
		if with_converter:
			sqlite3.register_converter("array", convert_array)
			self.connection = sqlite3.connect(self.path, detect_types=sqlite3.PARSE_DECLTYPES)
		else:
			self.connection = sqlite3.connect(self.path)
			
		self.cursor = self.connection.cursor()
		#Make sure the DB is prepped.
		self.initialize_db()
	
	#Close an SQL connection
	def close_connection(self):
		self.cursor.close()
		self.connection.close()
		#True cleanup - even a closed SQL connection obj cannot be passed to multiple processors, but a nonetype can.
		self.cursor = None
		self.connection = None
		
	#This is for adding reads. Genomes get added separately.
	def initialize_db(self):
		self.wake_up()
		
		self.cursor.execute("CREATE TABLE IF NOT EXISTS genome_lengths (genome_name TEXT PRIMARY KEY, genome_length INTEGER, MAG_group TEXT)")
		self.connection.commit()
		
		self.cursor.execute("CREATE TABLE IF NOT EXISTS sample_locations (sample_name TEXT PRIMARY KEY, sample_path TEXT)")
		self.connection.commit()
		
		self.cursor.execute("CREATE TABLE IF NOT EXISTS genes (contig TEXT, gene_id TEXT PRIMARY KEY, start INTEGER, end INTEGER, strand TEXT, annotation TEXT)")
		self.connection.commit()
		
	#Differentiates between BAM, SAM, and BLAST tabular formats
	def detect_format(self):
		#BAM magic string
		magic = b"\x1f\x8b\x08\x04"
		
		#print("Detecting input format... ", end = '')
		
		try:
			fh = open(self.input_reads, "rb")
			first_4_bytes = fh.read(4)
			fh.close()
			
			if first_4_bytes == magic:
				#print("BAM format.")
				self.read_format = "BAM"
				
		except:
			pass
			
		try:		
			fh = open(self.input_reads, "r")
			line = fh.readline()
			
		except:
			pass
		else:
			while line.startswith("#"):
				line = fh.readline()
				
			segment = line.split()
			try:
				#these will all be ints for a properly formatted blast tabular
				int(segment[6])
				int(segment[7])
				int(segment[8])
				int(segment[9])
				self.read_format = "BLAST"
			except:
				pass

			fh.close()
			
		try:
			fh = open(self.input_reads, "r")
			
			if fh.readline().startswith("@HD"):
				self.read_format = "SAM"
				#print("SAM format.")
			
			fh.close()
		
		except:
			pass
			
	#Add reads to the DB
	def set_reads(self, read_path):
		self.wake_up()
		self.input_reads = read_path
		#SQL table name safety.
		self.input_reads_name = os.path.basename(os.path.normpath(read_path).replace(".", "_"))
		#Windows C: safety and backslash safety.
		#self.input_reads_name = self.input_reads_name.replace(":", "colon")
		#self.input_reads_name = self.input_reads_name.replace("\\", "bs")
		
		self.cursor.execute("DROP TABLE IF EXISTS " + self.input_reads_name)
		self.connection.commit()
		self.cursor.execute("CREATE TABLE " + self.input_reads_name + " (read_ID INTEGER, genome_ID INTEGER, matches INTEGER, read_length INTEGER, align_length INTEGER, starts array, ends array)")
		self.connection.commit()
		
		self.cursor.execute("DROP TABLE IF EXISTS " + self.input_reads_name + "_genome_index")
		self.connection.commit()
		self.cursor.execute("CREATE TABLE " + self.input_reads_name + "_genome_index" + " (genome_name TEXT PRIMARY KEY, genome_ID INTEGER, MAG_group TEXT)")
		self.connection.commit()
		
		self.cursor.execute("DROP TABLE IF EXISTS " + self.input_reads_name + "_read_index")
		self.connection.commit()
		self.cursor.execute("CREATE TABLE " + self.input_reads_name + "_read_index" + " (read_name TEXT, read_ID INTEGER)")
		self.connection.commit()
		
		self.read_format = None
		self.import_reads_from_file()

	#Add genomes to the DB
	def set_genomes(self, genome_path, is_mag = False):
		self.wake_up()
		self.genomes = genome_path
		self.add_genomes_from_fasta(is_mag = is_mag)
		
	#Add genes to a DB; can be done repeatedly, and assumes genes are unique to a contig. Prodigal -f gff is REQUIRED to be the production method.
	def add_genes(self, prodigal_gff):
		self.wake_up()
		try:
			gene_info = []
			fh = open(prodigal_gff)
			for line in fh:
				if line.startswith("#"):
					continue
				else:
					line = line.strip().split()
					contig = line[0]
					start = min(int(line[3]), int(line[4]))
					end = max(int(line[3]), int(line[4]))
					strand = line[6]
					annotation = line[8]
					gene_id = annotation.split(";")[0].split("_")[1]
					gene_id = contig + "_" + gene_id
					#SQL friendliness.
					gene_id = gene_id.replace(".", "_")
					contig = contig.replace(".", "_")
					
					gene_info.append((contig, gene_id, start, end, strand, annotation))
			
			fh.close()
			self.cursor.executemany("INSERT OR REPLACE INTO genes VALUES (?, ?, ?, ?, ?, ?)", gene_info)
			self.connection.commit()
			gene_info = None
		except:
			#It failed, and I want to know.
			return False
		
		return True
			
	def import_reads_from_file(self):
		reader = read_generator(self.input_reads)
		
		parse_failure = False
		
		if self.read_format is None:
			try:
				self.detect_format()
				reader.format = self.read_format
			except:
				#failed to detect format
				parse_failure = True
		else:
			reader.format = self.read_format
			
		#Couldn't auto-detect format when attempted.
		if parse_failure:
			return False
			
		#No format and none detected.
		if self.read_format is None:
			return False
					
		chunk_tracker = 0
		read_index = 0
		seq_index = 0
		
		read_chunk = []
		read_IDs = {}
		genome_IDs = {}
		
		#Attempt to add reads to DB
		try:
			for line in reader:
				#Unsuccessful parses should produce this.
				if line is None:
					continue
				else:
					chunk_tracker += 1
					#Insert every 500K reads.
					if chunk_tracker % 500000 == 0:
						chunk_tracker = 0
						self.insert_reads(read_chunk)
						#Reset.
						read_chunk = []
					
					if line[0] not in read_IDs:
						read_IDs[line[0]] = read_index
						read_index += 1
					if line[1] not in genome_IDs:
						genome_IDs[line[1]] = seq_index
						seq_index += 1
						
					line[0] = read_IDs[line[0]]
					line[1] = genome_IDs[line[1]]
					
					#Format.
					line = tuple(line)
						
					read_chunk.append(line)
			
			#Final iter. There should always be at least one read in this.
			self.insert_reads(read_chunk)
			
			self.connection.commit()
					
			read_chunk = None
			
			self.cursor.executemany("INSERT INTO " + self.input_reads_name + "_read_index VALUES (?, ?)", zip(read_IDs.keys(), read_IDs.values()))
			self.connection.commit()
			
			#SQL doesn't work well with strings that contain '.' characters, as this is SQL's table sep. They're common in names, so clean.
			sql_friendly = {}
			for g in genome_IDs:
				rep = g.replace('.', '_')
				sql_friendly[rep] = genome_IDs[g]
			
			self.cursor.executemany("INSERT OR REPLACE INTO " + self.input_reads_name + "_genome_index VALUES (?, ?, ?)", zip(sql_friendly.keys(), sql_friendly.values(), sql_friendly.keys()))
			self.connection.commit()
						
			self.cursor.execute("INSERT OR REPLACE INTO sample_locations VALUES (?, ?)", (self.input_reads_name, "[" + os.path.normpath(str(Path(self.input_reads).absolute())) + "]"))
			self.connection.commit()
			
			#This is skipped inside the function if it's a blast file.
			self.add_genomes_from_sam_or_bam()
			
			#Double check.
			self.update_mags_upon_new_sample()
			
			self.index_reads()
			
			self.connection.commit()
			
			return True
			
		except:
			return False
	
	def add_genomes_from_fasta(self, is_mag = False):
		self.cursor.execute("CREATE TABLE IF NOT EXISTS genome_lengths (genome_name TEXT, genome_length INTEGER, MAG_group TEXT)")
		self.connection.commit()
		
		if self.genomes is None:
			return False
		else:
			if is_mag:
				mag_group = os.path.splitext(os.path.basename(self.genomes))[0]
				#SQL friendly
				mag_group = mag_group.replace('.', '_')
				
			genome_lengths = {}
			current_genome = ""
			current_seqlen = 0
			is_fasta = True
			
			fh = open(self.genomes)
			
			for line in fh:
				if line.startswith(">"):
					if current_seqlen > 0:						
						genome_lengths[current_genome] = current_seqlen
					current_genome = line.strip()[1:].split()[0]
					current_seqlen = 0
				else:
					line = line.strip()
					if set(line) <= set("ATCGatcgNn"):
						current_seqlen += len(line)
					else:
						is_fasta = False
						break
					
			fh.close()
			
			#Final iter.
			if current_seqlen > 0:						
				genome_lengths[current_genome] = current_seqlen
			
			if is_fasta:
			
				#sql friendly
				cleaned = {}
				for g in genome_lengths:
					rep = g.replace('.', '_')
					cleaned[rep] = genome_lengths[g]
			
				if is_mag:
					self.cursor.executemany("INSERT OR REPLACE INTO genome_lengths VALUES (?,?,?)", zip(cleaned.keys(), cleaned.values(), [mag_group] * len(cleaned)))
					self.update_sample_mag_IDs(cleaned, mag_group)
				else:
					self.cursor.executemany("INSERT OR REPLACE INTO genome_lengths VALUES (?,?,?)", zip(cleaned.keys(), cleaned.values(), cleaned.keys()))
				
				self.connection.commit()
	
	
	#When a sample is added, check the existing MAGs table and update the added genomes according to the  as needed.
	def update_mags_upon_new_sample(self):
		#self.input_reads_name is the sample name already.
		sql = "SELECT genome_name, MAG_group FROM genome_lengths"
		mags = {}
		for r in self.cursor.execute(sql).fetchall():
			mags[r[0]] = r[1]
		
		updates = []
		sql = "SELECT * FROM " + self.input_reads_name + "_genome_index"
		for r in self.cursor.execute(sql).fetchall():
			genome_name, genome_ID, MAG_group = r[0], r[1], r[2]
			if genome_name in mags:
				MAG_group = mags[genome_name]
			updates.append((genome_name, genome_ID, MAG_group))
		
		self.cursor.executemany("INSERT OR REPLACE INTO " + self.input_reads_name + "_genome_index VALUES (?, ?, ?)", updates)
		self.connection.commit()
			
	#Goes through the existing samples and updates mag groupings based on new mag info.
	def update_sample_mag_IDs(self, genomes, mag):
		tables = self.cursor.execute("SELECT name FROM sqlite_master WHERE name LIKE '%_genome_index'").fetchall()
		
		for table in tables:
			update = []
			for result in self.cursor.execute("SELECT * FROM "+ table[0]).fetchall():
				if result[0] in genomes:
					update.append((result[0], result[1], mag))
					
			self.cursor.executemany("INSERT OR REPLACE INTO " + table[0] + " VALUES (?, ?, ?)", update)
			self.connection.commit()
			
		update = None
		
	def add_genomes_from_sam_or_bam(self):
		header = None
		if self.read_format == "SAM":
			header = get_sam_header(self.input_reads)
		if self.read_format == "BAM":
			header = get_bam_header(self.input_reads)
		
		if header is not None:
			#SQL friendliness.
			cleaned = {}
			for g in header:
				rep = g.replace('.', '_')
				cleaned[rep] = header[g]
			
			#We can't extract MAG belongingness from the sam/bam header so we just use self as key.
			self.cursor.executemany("INSERT OR REPLACE INTO genome_lengths VALUES (?,?,?)", zip(cleaned.keys(), cleaned.values(), cleaned.keys()))
			self.connection.commit()
	
	def insert_reads(self, list_of_reads):
		self.cursor.executemany("INSERT INTO " + self.input_reads_name + " VALUES (?, ?, ?, ?, ?, ?, ?)", list_of_reads)
		self.connection.commit()
		
	def index_reads(self):
		self.cursor.execute("CREATE INDEX IF NOT EXISTS " + self.input_reads_name + "_index ON " + self.input_reads_name + " (genome_ID, read_ID)" )
		self.connection.commit()

#Function that converts a read's start and end positions into counts of bases falling into bins from a set of starts and ends.
def convert_to_bins(starts, ends, bin_starts, bin_ends):
	#Starts, ends are lists of ints from the read that correspond to the read's [start, end) pos in the genome.
	#bin_starts, bin_ends are genome coordinates indicating cutoffs where bases are to be counted. Rules:
	#Every start has a matching end. 
	#Overlaps are resolved by eliminating any overlap that is a subsection and by choosing the midpoint of the overlap starts/stops otw.
	#This function expects that to have already been done. i.e., each base can and must fall into EXACTLY one bin.
	#Gotta figure out hbins, counts now.
	#starts, ends = [], []
	
	returns_by_bin = {}
		
	for s, e in zip(starts, ends):
		start_bin = np.searchsorted(bin_ends, s, side = 'right')
		end_bin = np.searchsorted(bin_ends, e, side = 'right')
		#print("----------------")
		#print(s, e, start_bin, end_bin, bin_starts[start_bin], bin_ends[end_bin])
		
		if start_bin == end_bin:
			#start and end bin are the same; the whole read falls into this bin.
			if start_bin in returns_by_bin:
				returns_by_bin[start_bin] += (e-s)+1
			else:
				returns_by_bin[start_bin] = (e-s)+1
		else:
			#Figure out how many bases need adding in total as a running tracker of how many are left.
			total_bases = e-s + 1
			#How far can we go before we run out of bin
			current_end = bin_ends[start_bin]
			#How many do we add to this bin, then?
			to_add = current_end - s
			#remove those from the tracker
			total_bases -= to_add
			#Final position is not counted in the same bin
			total_bases += 1
			#Add as needed.
			if start_bin in returns_by_bin:
				returns_by_bin[start_bin] += to_add -1 
			else:
				returns_by_bin[start_bin] = to_add - 1
			#Update start to start of the next bin	
			s = current_end
				
			#Repeat until done.
			while total_bases > 0:
				#Move to the next bin
				start_bin += 1
				#Next end
				current_end = bin_ends[start_bin]
				
				if current_end > e:
					#This is the last bin for this s-e window, so we use the remaining bases as the count instead of the bases to the end of the bin
					if start_bin in returns_by_bin:
						returns_by_bin[start_bin] += total_bases
					else:
						returns_by_bin[start_bin] = total_bases
					#Doesn't matter what this is, as long as it's less than 0
					total_bases = -1
				else:
					#This is not the last bin to add to, so we use distance to the bin as the marker.
					to_add = current_end - s
					total_bases -= to_add
					#We don't count the final position in the bin, as it's non-inclusive
					total_bases += 1
					if start_bin in returns_by_bin:
						returns_by_bin[start_bin] += to_add - 1
					else:
						returns_by_bin[start_bin] = to_add - 1
					
					s = current_end
					
	return returns_by_bin
	
#Create what amounts to the dataframe for a recplot from a database
#Loading should basically just be selecting a genome. The genome ought to be preprocessed into basically plot-ready form.
#Should just push this to R
class recruitment_plot_data():
	def __init__(self, database_path, bin_width = 1000, bin_height = 0.5, in_group_minimum = 95, min_align_len = 50, min_pct_align = 90, local_pct_id = True, only_one_alignment_per_read = True, best_hit_criteria = "local_percent_ID", calc_breadth_and_depth = True, tad_percent = 80):
		self.path = database_path
		
		self.exists = os.path.exists(os.path.normpath(database_path))
		
		self.width = bin_width
		self.height = bin_height
		self.in_grp = in_group_minimum
		self.min_align_length = min_align_len
		self.min_pct_align = min_pct_align
		
		self.pct_id_is_local = local_pct_id
		self.only_one_alignment_per_read = only_one_alignment_per_read
		self.best_hit_criteria = best_hit_criteria
		
		self.allowable_params = None
		
		self.connection = None
		self.cursor = None
		self.exists = False
		
		self.samples = None
		
		self.current_sample = None
		self.path_to_sample = None
		self.sample_format  = None
		
		self.mags_in_sample = None
		
		self.current_mag = None
		
		self.contigs_in_mag = None
		
		self.lengths_of_contigs = None
		
		self.data_for_this_genome = None
		
		self.gene_starts = None
		self.gene_ends = None
		self.gene_annotations = None
		
		
		self.extended_stats = calc_breadth_and_depth
		self.breadth_for_this_genome = None
		self.depth_for_this_genome = None
		self.tad_middle = tad_percent
		self.ani_r = None
		
		self.ids = None
		
		self.can_be_plotted = False
		
		self.plot_ready = None
		#Basically data for R to correctly place the plot and annotate it if genes are present.
		
		self.plotting_genes = False
		
		self.non_gene_annotations = None
		
		self.describe_y = None
		self.describe_x = None
		
		self.widths = None
		self.main_annotations = None
		self.depth_annotations = None
		self.plot_x_axis = None
		
		#Top-left plot
		self.depth_chart_data = None
		#Bot-right plot
		self.bases_by_pct_id = None
		#top right gets calculated in R because it's very easy from depth data.
		
		self.plot_linear = True
		self.show_peaks = False
		
		self.completed_depth_annot = None
		self.completed_main_annot = None
		
		#Read IDs to select. Works like a cart - add from genomes until you're ready, then export.
		#Really what we need are row IDs, since that should match the input data exactly.
		self.reads_to_select = None
		self.constructed_query = None
		#Add sam/bam header for fmt purposes
	
	def reset(self):
		self.current_mag = None
		self.contigs_in_mag = None
		self.lengths_of_contigs = None
		self.data_for_this_genome = None
		self.gene_starts = None
		self.gene_ends = None
		self.gene_annotations = None
		self.breadth_for_this_genome = None
		self.depth_for_this_genome = None
		self.ani_r = None
		self.ids = None
		self.can_be_plotted = False
		self.plot_ready = None
		#Basically data for R to correctly place the plot and annotate it if genes are present.
		self.non_gene_annotations = None
		self.describe_y = None
		self.describe_x = None
		self.widths = None
		self.main_annotations = None
		self.depth_annotations = None
		self.plot_x_axis = None
		#Top-left plot
		self.depth_chart_data = None
		#Bot-right plot
		self.bases_by_pct_id = None
		#top right gets calculated in R because it's very easy from depth data.
		self.completed_depth_annot = None
		self.completed_main_annot = None
		self.constructed_query = None
	
	def check_valid(self):
		valid = False
		try:
			if os.path.exists(self.path):
				try:
					self.wake_up()
					#This only works if the genome_lengths table exists. I'm trusting nobody else has an SQLite3 db with this table name for this check.
					tabs = self.cursor.execute("SELECT name FROM sqlite_master").fetchall()
					for tab in tabs:
						if tab[0] == "genome_lengths":
							valid = True
							break
					self.close_connection()
				except:
					valid = False
		except:
			valid = False
			
		return valid
	
	def wake_up(self):
		if self.cursor is None:
			self.activate_connection()
		
	def activate_connection(self, with_converter = True):
		# Converts np.array to TEXT when inserting
		##sqlite3.register_adapter(np.ndarray, adapt_array)

		#Converts byte string to numpy ndarray(int32) upon read from DB.
		if with_converter:
			sqlite3.register_converter("array", convert_array)
			self.connection = sqlite3.connect(self.path, detect_types=sqlite3.PARSE_DECLTYPES)
		else:
			self.connection = sqlite3.connect(self.path)
			
		self.cursor = self.connection.cursor()
		self.exists = True
	
	#Close an SQL connection
	def close_connection(self):
		self.cursor.close()
		self.connection.close()
		#True cleanup - even a closed SQL connection obj cannot be passed to multiple processors, but a nonetype can.
		self.cursor = None
		self.connection = None
	
	
	#Basic database assays
	def get_samples(self):
		self.wake_up()
		tables = self.cursor.execute("SELECT name FROM sqlite_master WHERE name LIKE '%_genome_index'").fetchall()
		
		self.samples = []
		for table in tables:
			self.samples.append(table[0].split("_genome_index")[0])
		
		tables = None
		
		if len(self.samples) == 0:
			self.samples = None
			self.current_sample = None
		else:
			if self.current_sample is None:
				self.current_sample = self.samples[0]
				
		self.connection.commit()
			
	def set_sample(self, sample):
		self.wake_up()
		self.current_sample = sample
		self.get_mags()
	
	def get_mags(self):
		self.wake_up()
		if self.current_sample is None:
			#Just don't break.
			pass
		else:	
			self.mags_in_sample = {}
			for result in self.cursor.execute("SELECT * FROM " + self.current_sample + "_genome_index").fetchall():
				#genome, index, mag = result[0], result[1], result[2]
				if result[2] in self.mags_in_sample:
					self.mags_in_sample[result[2]].append(result[0])
				else:
					self.mags_in_sample[result[2]] = [result[0]]
					
			#Update mag as needed or fill the empty place.
			if self.current_mag is None or self.current_mag not in self.mags_in_sample:
				self.current_mag = list(self.mags_in_sample.keys())[0]
				#We don't demand that genomes have already been added.
				self.update_mag_metadata()
				
		self.connection.commit()

	def update_mag_metadata(self):
		try:
			sql = "SELECT genome_name, genome_length FROM genome_lengths WHERE MAG_group = \"" + self.current_mag + "\""
			self.lengths_of_contigs = {}
			for r in self.cursor.execute(sql):
				self.lengths_of_contigs[r[0]] = r[1]
		except:
			self.lengths_of_contigs = None
			#If genome length is missing for this MAG/contigs, we'll just set length to the max pos. observed in each contig upon data load.
			#But we don't want to do that here in the automatic update section.	
		try:
			sql = "SELECT genome_name, genome_ID FROM " + self.current_sample + "_genome_index WHERE genome_name IN ({genomes})".format(genomes = ','.join(['?']*len(self.lengths_of_contigs)))
			self.contigs_in_mag = {}
			for r in self.cursor.execute(sql, tuple(self.lengths_of_contigs.keys())).fetchall():
				self.contigs_in_mag[r[0]] = r[1]
		except:
			self.contigs_in_mag = None
			
		self.connection.commit()
		
	def set_mag(self, mag):
		self.current_mag = mag
		self.update_mag_metadata()		

	def assess_sample_format(self):
		if self.current_sample is not None:
			was_blast = self.cursor.execute("SELECT read_length FROM " + self.current_sample).fetchone()[0] is None
			if was_blast:
				self.sample_format == "BLAST"
			else:
				self.sample_format == "SAM/BAM"
		else:
			self.sample_format = None
			
	def get_allowable_params(self):
		allowable_params = {}
		if self.sample_format == "BLAST":
			allowable_params = {}
		if self.sample_format == "SAM/BAM":
			allowable_params = {}
		
	#update to select genomes in mag
	def query_constructor(self, all_genomes = False):
		#Can't construct a query on a non-genome
		if self.contigs_in_mag is None:
			return None
			
		genome_indices = list(self.contigs_in_mag.values())
		#genome_index = self.mags_in_sample[self.current_genome]
		#Global ID is not reported in BLAST fmt.
		if self.sample_format == "BLAST":
			self.pct_id_is_local = True
		
		#This string gets built depending on user opts until it's good to go and is used. It always starts with this.
		constructed_query = "SELECT "

		bh = "best_hit_reads."
		row_id = "rowid, genome_id, read_length, align_length, round(((cast("
		row_id_bh = "best_hit_reads.rowid, best_hit_reads.genome_id, best_hit_reads.read_length, best_hit_reads.align_length, round(((cast("
		
		match_statement = "matches as REAL)/"
		match_statement_besthits = bh + match_statement
		
		global_align = "read_length)/0.01), 1), "
		
		local_align = "align_length)/0.01), 1), "
		
		bins_counts = "starts, ends FROM "
		
		global_align_besthits = bh + global_align
		local_align_besthits = bh + local_align
		
		bins_counts_besthits = bh+"starts, " + bh + "ends FROM "
		
		with_aligned_bases    = "align_length>" + str(self.min_align_length) 
		with_percent_alignment = "cast(align_length as REAL)/read_length>" + str(self.min_pct_align/100)
		
		select_best_hit = " (SELECT rowid, * FROM " + self.current_sample + " WHERE " + with_aligned_bases
		
		if self.sample_format != "BLAST":
			select_best_hit = select_best_hit + " AND " + with_percent_alignment
					
		select_best_hit += " GROUP BY read_ID ORDER BY "
		
		best_hit_percent_ID_global = "cast(matches as REAL)/read_length DESC) AS best_hit_reads "
		best_hit_percent_ID_local  = "cast(matches as REAL)/align_length DESC) AS best_hit_reads "
		
		#Can only be global
		best_hit_percent_alignment = "cast(align_length as REAL)/read_length DESC) AS best_hit_reads"
		
		#either global or local permitted.
		best_hit_alignment_length  = "read_length DESC) AS best_hit_reads "
		
		if self.pct_id_is_local:
			if self.sample_format == "BLAST":
				if self.best_hit_criteria == "global_percent_ID" or self.best_hit_criteria == "percent_alignment":
				#Not allowed to do these for blast.
					self.best_hit_criteria = "local_percent_ID"
			
			if self.best_hit_criteria == "local_percent_ID":
				select_best_hit += best_hit_percent_ID_local
			if self.best_hit_criteria == "alignment_length":
				select_best_hit += best_hit_percent_ID_local
		else:
			if self.best_hit_criteria == "global_percent_ID":
				select_best_hit += best_hit_percent_ID_global
			if self.best_hit_criteria == "local_percent_ID":
				select_best_hit += best_hit_percent_ID_local
			if self.best_hit_criteria == "percent_alignment":
				select_best_hit += best_hit_percent_ID_global
			if self.best_hit_criteria == "alignment_length":
				select_best_hit += best_hit_percent_ID_local
			
			select_best_hit += best_hit_percent_ID_global
		
		
		#from_the_current_genome    = " WHERE genome_ID="+str(genome_index)
		#from_the_current_genome    = " WHERE genome_ID in ({genomes})".format(genomes = ','.join(['?']*len(genome_indices)))
		from_the_current_genome    = " WHERE genome_ID=(?)"
		
		if self.only_one_alignment_per_read:
			constructed_query = constructed_query + row_id_bh + match_statement_besthits
		
			if self.pct_id_is_local:
				constructed_query = constructed_query + local_align_besthits 

			else:
				constructed_query = constructed_query + global_align_besthits
				
			if all_genomes:
				constructed_query = constructed_query + bins_counts_besthits + select_best_hit
			else:
				constructed_query = constructed_query + bins_counts_besthits + select_best_hit + from_the_current_genome
		
		else:
			constructed_query = constructed_query + row_id + match_statement
			
			if self.pct_id_is_local:
				constructed_query = constructed_query + local_align

			else:
				constructed_query = constructed_query + global_align
				
			if all_genomes:
			
				if self.sample_format == "BLAST":
					constructed_query = constructed_query + bins_counts + self.current_sample +  " WHERE " + with_aligned_bases
				else:
					constructed_query = constructed_query + bins_counts + self.current_sample +  " WHERE " + with_aligned_bases + " AND " + with_percent_alignment
			
			else:
				
				if self.sample_format == "BLAST":
					constructed_query = constructed_query + bins_counts + self.current_sample + from_the_current_genome + " AND " + with_aligned_bases
				else:
					constructed_query = constructed_query + bins_counts + self.current_sample + from_the_current_genome + " AND " + with_aligned_bases + " AND " + with_percent_alignment
			
		self.constructed_query = constructed_query
	
	#Hoverable info for non-gene.
	def create_default_annots(self):
		self.annotations = {}
		for gen in self.describe_x:
			self.annotations[gen] = []
			for i in range(0, len(self.describe_x[gen][0])):
				annot = (gen, str(self.describe_x[gen][0][i]), str(self.describe_x[gen][1][i]))
				self.annotations[gen].append(annot)
	
	#create and fill data frame with data from DB
	#Update this to use bin height, too; currently only works with width
	def create_frame(self):
		#Can't work with nothing.
		if self.current_mag is None:
			return None

		#Genome width is a necessary fact for this...
		self.data_for_this_genome = {}
			
		#Prepare a query
		self.query_constructor()
		
		if self.extended_stats:
			#ani_r is the average pct. ID of all bases falling into a given range.
			self.ani_r = dict.fromkeys(self.contigs_in_mag.keys(), 0)
			#Depths are the TAD-n of each genome; average depth over the middle n percentiles
			self.depth_for_this_genome   = dict.fromkeys(self.contigs_in_mag.keys(), 0)
			#Breadths are num pos covered/genome length
			self.breadth_for_this_genome = dict.fromkeys(self.contigs_in_mag.keys(), 0)

		self.ids = {}
		self.describe_x = {}
			
		#For each contig in the genome, we get the data one query at a time.
		#Time-inefficient to repeatedly query, but plotting is the vast maj. of the time.
		for gen in self.contigs_in_mag:
			id = self.contigs_in_mag[gen]
			results = self.cursor.execute(self.constructed_query, (id,)).fetchall()
			
			#If the reads in a sample have had their parent genomes described in a reference set,
			#then the database should have their lengths. 
			#If not, then we use the maximum of the observed points among the reads as the max
			if self.lengths_of_contigs is not None:
				if gen in self.lengths_of_contigs:
					#We found the genome, just get the length
					genome_length = self.lengths_of_contigs[gen]
				else:
					#We have some described genomes, but didn't find the specific 
					#contig we're looking at in the list of described genomes. 
					genome_length = 1
					#One pass through the data just to get the length.
					for r in results:
						max_in_res = r[6]
						#Max is always the final entry.
						max_in_res = max_in_res[max_in_res.shape[0]-1]
						genome_length = max(genome_length, max_in_res)
			else:
				#We don't have any data on the genomes at all, so we revert to using the reads to get the max length.
				genome_length = 1
				#One pass through the data just to get the length - normally this shouldn't be needed.
				for r in results:
					max_in_res = r[6]
					#Max is always the final entry.
					max_in_res = max_in_res[max_in_res.shape[0]-1]
					genome_length = max(genome_length, max_in_res)
			
			if self.gene_starts is not None and self.plotting_genes:
			#We have genes somewhere in the data.
				if gen in self.gene_starts:
					if len(self.gene_starts[gen]) > 0:
						#Breaks are a given array.
						#starts, ends = self.gene_starts[gen], self.gene_ends[gen]
						
						#Genome legnth is our guaranteed end point
						genome_pos = 0
						cur_start = self.gene_starts[gen][0]
						cur_end   = self.gene_ends[gen][0]
						index = 0
						
						starts = []
						ends = []
						completed_annot = []
						
						#make sure that the first index is set.
						if cur_start > 0:
							starts.append(0)
							ends.append(cur_start)
							#Gene info is contig, gene, start, end, strand, annot.
							#We have contig, None, start, end, None, None
							null_annot = (gen, "NA", str(0), str(cur_start), "NA", "Intergenic")
							completed_annot.append(null_annot)
							
						for i in range(0, len(self.gene_starts[gen])-1):
							cur_start = self.gene_starts[gen][i]
							cur_end   = self.gene_ends[gen][i]
							cur_annot = self.gene_annotations[gen][i]
							
							starts.append(cur_start)
							ends.append(cur_end)
							completed_annot.append(cur_annot)
							
							next_start = self.gene_starts[gen][i+1]
							next_end   = self.gene_ends[gen][i+1]
							if cur_end != next_start:
								#Close the gap
								starts.append(cur_end)
								ends.append(next_start)
								null_annot = (gen, "NA", str(cur_end), str(next_start), "NA", "Intergenic")
								completed_annot.append(null_annot)	
								
						#Final gene info
						final_index = len(self.gene_starts[gen])-1
						cur_start = self.gene_starts[gen][final_index]
						cur_end = self.gene_ends[gen][final_index]
						starts.append(cur_start)
						ends.append(cur_end)
						completed_annot.append(self.gene_annotations[gen][final_index])			
							
						#Make sure the genome is complete.	
						if cur_end < genome_length:
							starts.append(cur_end)
							ends.append(genome_length)
							null_annot = (gen, "NA", str(cur_end), str(genome_length), "NA", "Intergenic")
							completed_annot.append(null_annot)
						
						#Type matching.
						starts = np.array(starts, dtype = np.int32)
						ends = np.array(ends, dtype = np.int32)
						
						#Update class' data repo so access is consistent within R
						self.gene_starts[gen] = starts
						self.gene_ends[gen] = ends
						self.gene_annotations[gen] = completed_annot
						
					else:
						#Effectively a non-gene case. Plots, but is basically a fail.
						breaks = np.linspace(0, genome_length, num = int(genome_length/self.width), dtype = np.int32)
						starts, ends = breaks[:-1], breaks[1:]
						self.plotting_genes = False
				else:
					#Effectively a non-gene case. Plots, but is basically a fail.
					breaks = np.linspace(0, genome_length, num = int(genome_length/self.width), dtype = np.int32)
					starts, ends = breaks[:-1], breaks[1:]
					self.plotting_genes = False
			
			else:
				#Non-gene display case by intention rather than failure to plot genes.
				#Break up the genome/contig into bins of approximately the correct size.
				breaks = np.linspace(0, genome_length, num = int(genome_length/self.width), dtype = np.int32)
				starts, ends = breaks[:-1], breaks[1:]
			
			#We need this for depth of coverage by bin.
			#widths = np.subtract(ends, starts)
			
			self.describe_x[gen] = [starts, ends]
			
			if not self.plotting_genes:
				self.create_default_annots()
			
			#Dict of bins for this genome.
			self.data_for_this_genome[gen] = defaultdict(lambda: np.zeros(starts.shape[0], dtype = np.int32))
			
			#This is guaranteed to have a maximum length if any reads were present for the genome in the DB
			if self.extended_stats:
				#Depth per pos by pct ID
				my_depth = defaultdict(lambda: np.zeros(genome_length, dtype = np.int32))
				my_anir = defaultdict(lambda: 0)
				my_base_count = defaultdict(lambda: 0)
				
				#Second pass through reads for stats and to fill out data.
				for r in results:
					#For the entire length of the read, increment depths - add +1 to the end to include that index, too
					first_pos = r[5][0]
					last_pos = (r[6][len(r[6])-1]+1)
					pct_id_bin = self.height * (r[4] // self.height)
					my_depth[pct_id_bin][first_pos:last_pos] += 1
					
					#r[2] is read length, r[3] is align length
					if self.pct_id_is_local:
						my_anir[pct_id_bin] += r[4] * r[3]
						my_base_count[pct_id_bin] += r[3]
					else:
						my_anir[pct_id_bin] += r[4] * r[2]
						my_base_count[pct_id_bin] += r[2]
						
					#r consists of row_id, genome_id, pct_id, starts, ends
					bin_ct = convert_to_bins(r[5], r[6], starts, ends)
					for bin in bin_ct:
						self.data_for_this_genome[gen][pct_id_bin][bin] += bin_ct[bin]

				
				my_depth = dict(my_depth)
				my_breadth = dict.fromkeys(my_depth.keys(), 0)
				tracker = np.zeros(genome_length, dtype = np.int32)
				
				#Find the range we'll need.
				if self.tad_middle > 100 or self.tad_middle < 1:
					self.tad_middle = 80
				middle_n_percent = (100 - self.tad_middle)/2
						
				cut_at = int(genome_length/middle_n_percent)
				
				cumulative_ani = 0
				cumulative_bases = 0
				
				my_anir = dict(my_anir)
				my_base_count = dict(my_base_count)
				
				#Descending sort means we can track cumulative depth and breadth, which is what we want.
				for pct in sorted(my_depth.keys(), reverse=True):
					cumulative_ani += my_anir[pct]
					cumulative_bases += my_base_count[pct]
					my_anir[pct] = cumulative_ani/cumulative_bases
					#Add the next set of counts to a running sum at or above this pct ID
					tracker += my_depth[pct]
					#percent coverage at or above this percent ID
					my_breadth[pct] = np.count_nonzero(tracker)/genome_length
					#We now need the TAD, so we sort the results up to this point...
					my_depth[pct] = np.sort(tracker)
					#And take the middle n percent.
					my_depth[pct] = np.mean(my_depth[pct][cut_at:(genome_length-cut_at)])
				
				self.depth_for_this_genome[gen] = my_depth
				self.breadth_for_this_genome[gen] = my_breadth
				self.ani_r[gen] = my_anir
				
				
			else:
				for r in results:
					#r consists of row_id, genome_id, pct_id, starts, ends
					bin_ct = convert_to_bins(r[5], r[6], starts, ends)
					for bin in bin_ct:
						self.data_for_this_genome[gen][pct_id_bin][bin] += bin_ct[bin]
			
			self.ids[gen] = list(sorted(self.data_for_this_genome[gen].keys(), reverse = True))
			
			self.data_for_this_genome = dict(self.data_for_this_genome)
			for gen in self.data_for_this_genome:
				self.data_for_this_genome[gen] = dict(self.data_for_this_genome[gen])
			
		
		self.create_default_annots()
			
		return None
	
	#Create an ordered numpy matrix from the dict of counts made by the create_frame function and describes the axes.
	def create_minimal_matrix(self):
		min_id = 100
		max_id = 0
		for gen in self.ids:
			min_id = min(min(self.ids[gen]), min_id)
			max_id = max(max(self.ids[gen]), max_id)
		
		spanning_range = []
		next = max_id
		while next >= min_id:
			spanning_range.append(next)
			next -= self.height
			
		self.describe_y = np.array(spanning_range)
		
		matrices = []
		for gen in self.data_for_this_genome:
			for id in self.data_for_this_genome[gen]:
				size = self.data_for_this_genome[gen][id].shape[0]
			next_mat = np.zeros(shape = (len(spanning_range), size), dtype = np.int32)
			count = 0
			for i in range(0, len(spanning_range)):
				this_id = spanning_range[i]
				if this_id in self.data_for_this_genome[gen]:
					next_mat[i] += self.data_for_this_genome[gen][this_id]
					#print(self.data_for_this_genome[gen][id])
				
			matrices.append(next_mat)
			
		#Readied plotting data.
		self.plot_ready = np.hstack(matrices)
		matrices = None

		return None
	
	def complete_annots(self):
		self.depth_annotations = {"in_group":[], "out_group":[]}
		#By pct ID and region
		self.main_annotations = {}
		for y in self.describe_y:
			self.main_annotations[y] = []
			
		total_annots = []
		if self.plotting_genes:
			for gen in self.gene_annotations:
				total_annots.extend(self.gene_annotations[gen])
				self.gene_annotations[gen] = None
			count = 0
			#Gene info is contig, gene, start, end, strand, annot.
			for region in total_annots:
				formatted = "Genome: " + region[0] + "\nGene: " + region[1] + "\nStrand: "+ region[4] + "\nRange: " + str(region[2]) + "-" + str(region[3]) + "\nAnnotation: " + region[5]
				main_annot = formatted + "\nBase Count: "
				for i in range(0, len(self.describe_y)):
					y_bin = self.describe_y[i]
					self.main_annotations[y_bin].append(main_annot + str(self.plot_ready[i, count]))
					
				for_depth = formatted + "\nWithin Pop.: Yes\nAverage Depth: " + str(self.depth_chart_data["in_group"][count])
				self.depth_annotations["in_group"].append(for_depth)
				for_depth = formatted + "\nWithin Pop.: No\nAverage Depth: "  + str(self.depth_chart_data["out_group"][count])
				self.depth_annotations["out_group"].append(for_depth)
				count += 1
		else:
			for gen in self.annotations:
				total_annots.extend(self.annotations[gen])
				self.annotations[gen] = None
			count = 0
			for region in total_annots:
				formatted = "Genome: " + region[0] + "\nRange: " + str(region[1]) + "-" + str(region[2])
				main_annot = formatted + "\nBase Count: "
				for i in range(0, len(self.describe_y)):
					y_bin = self.describe_y[i]
					self.main_annotations[y_bin].append(main_annot + str(self.plot_ready[i, count]))
					
				for_depth = formatted + "\nWithin Pop.: Yes\nAverage Depth: " + str(self.depth_chart_data["in_group"][count])
				self.depth_annotations["in_group"].append(for_depth)
				for_depth = formatted + "\nWithin Pop.: No\nAverage Depth: "  + str(self.depth_chart_data["out_group"][count])
				self.depth_annotations["out_group"].append(for_depth)
				count += 1
			
		#One row.
		total_annots = []
		for y_bin in self.describe_y:
			total_annots.extend(self.main_annotations[y_bin])
			self.main_annotations[y_bin] = None
		self.main_annotations = total_annots
		total_annots = None
				
	
	def calculate_marginals(self):
		#Data missing.
		if self.plot_ready is None:
			return False
		
		#self.in_grp is the minimum ANI for this
		#self.
		#Top left plot
		self.widths = []
		self.plot_x_axis = []
		for gen in self.describe_x:
			this_width = np.subtract(self.describe_x[gen][1], self.describe_x[gen][0])
			this_midpoints = np.divide(np.add(self.describe_x[gen][1], self.describe_x[gen][0]), 2)
			self.plot_x_axis.append(this_midpoints)
			self.widths.extend(this_width.tolist())
			
		self.widths = np.array(self.widths)
		max_spots = [0]
		
		buffer = 0
		combined = []
		for i in range(0, len(self.plot_x_axis)):
			self.plot_x_axis[i] = np.add(self.plot_x_axis[i], buffer)
			buffer += max(self.plot_x_axis[i])
			combined.extend(self.plot_x_axis[i])
		
		combined = np.array(combined)
			
		self.plot_x_axis = combined
		
		#Colsums of the original, but split by in/out group
		split_point = sum(self.describe_y > self.in_grp) + 1
		#print(split_point, self.describe_y[split_point])
		self.depth_chart_data = {}
		
		self.depth_chart_data["in_group"]  = np.sum(self.plot_ready[0:split_point], axis = 0)
		self.depth_chart_data["out_group"] = np.sum(self.plot_ready[split_point:], axis = 0)
		
		#Normalize to bin width
		self.depth_chart_data["in_group"]  = np.divide(self.depth_chart_data["in_group"], self.widths)
		self.depth_chart_data["out_group"] = np.divide(self.depth_chart_data["out_group"], self.widths)
		
		#fill nans
		np.nan_to_num(self.depth_chart_data["in_group"], copy=False, nan=0.0)
		np.nan_to_num(self.depth_chart_data["out_group"], copy=False, nan=0.0)
		#print(self.depth_chart_data)
		
		#print(self.depth_chart_data["in_group"])
		#print(self.depth_chart_data["out_group"])
		
		#bot right plot
		#This is just the rowsums of the original data, no need to split since it's already by pct id.
		self.bases_by_pct_id = np.sum(self.plot_ready, axis = 1)	
		
		self.complete_annots()
		
	def set_show_peaks(self, show_peaks = False):
		self.show_peaks = show_peaks
		
	def load_genes(self):
		contigs = tuple(self.contigs_in_mag.keys())
		sql = "SELECT * FROM genes WHERE contig IN ({genomes})".format(genomes = ','.join(['?']*len(contigs)))
		
		gene_annotations = self.cursor.execute(sql, contigs).fetchall()
		
		#Couldn't load anything.
		if gene_annotations is None:
			self.plotting_genes = False
			
		self.gene_annotations = {}
		self.gene_starts = {}
		self.gene_ends = {}
		for contig in contigs:
			self.gene_annotations[contig] = []
			self.gene_starts[contig] = []
			self.gene_ends[contig] = []
		
		starts = []
		ends = []
		for result in gene_annotations:
			contig = result[0]
			self.gene_annotations[contig].append(result)
			self.gene_starts[contig].append(result[2])
			self.gene_ends[contig].append(result[3])
			
		for contig in self.gene_starts:
			delete_these = []
			for i in range(0, len(starts)-1):
				#The next interval is a subset of the current interval and needs removing.
				#A contained range would HAVE to have an adjacent start
				if self.gene_starts[contig][i+1] >= self.gene_starts[contig][i] and self.gene_ends[contig][i+1] <= self.gene_ends[contig][i]:
					delete_these.append(i)

			#Clean for subintervals looking the other way.
			for i in range(1, len(self.gene_starts[contig])):
				if self.gene_starts[contig][i-1] >= self.gene_starts[contig][i] and self.gene_ends[contig][i-1] <= self.gene_ends[contig][i]:
					delete_these.append(i)				
			
			#Bump boundaries around as needed.
			for i in range(0, len(self.gene_starts[contig])-1):
				#Don't worry about subintervals
				if i in delete_these:
					continue
				
				if self.gene_starts[contig][i+1] < self.gene_ends[contig][i]:
					#Start and end overlap
					midpt = int((self.gene_starts[contig][i+1] + self.gene_ends[contig][i])/2)
					self.gene_ends[contig][i] = midpt
					self.gene_starts[contig][i+1] = midpt
			
			delete_these = list(set(delete_these))
			for i in sorted(delete_these, reverse=True):
				self.gene_starts[contig].pop(i)
				self.gene_ends[contig].pop(i)
				self.gene_annotations[contig].pop(i)
				
		self.plotting_genes = True
		
	#Automatically attempt to locate seq-discrete gap. Not yet implemented.
	def auto_detect_sequence_discrete_gap(self):
		#Assume 95% ID across the genome is a good starting point.
		default_assumption = 95
		#If the discovered bins are more than this much ID apart from one bin to the next, reset to default assumption.
		maximum_discrepancy = 0.3
		
		
		def find_robust_minima(matrix, distance):
			max_row = matrix.shape[1]
			row_averages = []

			#For each row, take the average of the [DISTANCE] rows above and below the row, where possible.
			for row in range(0, matrix.shape[1]):
				up = distance
				down = distance + 1
				
				if row - distance < 0:
					up = row 
				if row + distance >= max_row:
					down = max_row - row
					
				count = 0
				row_sums = np.zeros(matrix.shape[0], dtype = np.int32)
				for i in range(row-up, row+down):
					count += 1
					row_sums += matrix[: , i]
				
				#These are now the row averages
				row_sums = np.divide(row_sums, count)
				row_averages.append(row_sums)
				
			all_averages = np.transpose(np.vstack(row_averages))
			
			is_minima = np.zeros(shape = all_averages.shape, dtype = np.int32)
			
			#print(all_averages.shape)
			
			for row in range(1, all_averages.shape[1]-1):
				#If the current row is a valley, then the previous and next rows are both increasing.
				decreasing_in = all_averages[row-1] > all_averages[row]
				increasing_out = all_averages[row] < all_averages[row+1]
				
				is_local_min = np.logical_and(decreasing_in, increasing_out)
				
				is_minima[row, is_local_min] = 1
				#print(row, is_minima[row])
			
			#print(all_averages)
			#print(is_minima)
			
			return is_minima
			
			
		x, y, bins = self.create_minimal_matrix()
		
		#print(len(x), )
		
		initial = find_robust_minima(bins, 0)
		#For 0-10, find the gulleys and sum the count of gulleys for each bin, pct ID
		for i in range(1, 11):
			initial += find_robust_minima(bins, i)
			
		print(any(initial[0] > 0))
	
		print(np.argmax(initial, axis = 1))
		
		
		
		return x, y, bins, initial
	
	
	#Read filtering block...
	
	#Differentiates between BAM, SAM, and BLAST tabular formats
	def detect_format(self):
		#BAM magic string
		magic = b"\x1f\x8b\x08\x04"
		
		try:
			fh = open(self.path_to_sample, "rb")
			first_4_bytes = fh.read(4)
			fh.close()
			
			if first_4_bytes == magic:
				#print("BAM format.")
				self.sample_format = "BAM"
			
			fh.close()
				
		except:
			try:
				fh.close()
			except:
				pass
			
		try:		
			fh = open(self.path_to_sample, "r")
			line = fh.readline()
			fh.close()
		except:
			try:
				fh.close()
			except:
				pass
			
		else:
			while line.startswith("#"):
				line = fh.readline()
				
			segment = line.split()
			try:
				#these will all be ints for a properly formatted blast tabular
				int(segment[6])
				int(segment[7])
				int(segment[8])
				int(segment[9])
				self.sample_format = "BLAST"
				fh.close()
			except:
				try:
					fh.close()
				except:
					pass

			
			
		try:
			fh = open(self.path_to_sample, "r")
			
			if fh.readline().startswith("@HD"):
				self.sample_format = "SAM"
			
			fh.close()
		
		except:
			try:
				fh.close()
			except:
				pass
		
	def link_to_file(self):
		self.path_to_sample = self.cursor.execute("SELECT sample_path FROM sample_locations WHERE sample_name='"+self.current_sample+"'").fetchone()[0]
		#For safety, names are enclosed in brackets first.
		self.path_to_sample = self.path_to_sample[1:(len(self.path_to_sample)-1)]
		self.detect_format()
		if self.sample_format not in ["SAM", "BAM", "BLAST"]:
			self.sample_format = None
			
		self.connection.commit()
		
	#Re-executes the same query used to generate the current plot, but filters for [CRITERIA], extracts the read numbers, 
	#and adds them to the current cart, then uniques and sorts the cart to make sure there's no dupes.
	def select_reads_for_export(self, mins = [0], maxes = [np.inf]):
		
		#Don't bother with checking if a read falls into a winning gneome bin if all reads must.
		if mins == [0] and maxes == [np.inf]:
			whole_range = True
		else:
			whole_range = False
			
		if self.constructed_query is None:
			return None

		#Initialize the set if need be. Else, we add to it.
		if self.reads_to_select is None:
			self.reads_to_select = {}
		
		if self.path_to_sample not in self.reads_to_select:
			self.reads_to_select[self.path_to_sample] = []
		
		
		#Interleave starts/ends for the plot range to allow for binary search.
		interleaved_min_max = []
		for i in range(0, len(mins)):
			interleaved_min_max.append(mins[i])
			interleaved_min_max.append(maxes[i])
			
		for gen in self.contigs_in_mag:
			id = self.contigs_in_mag[gen]
			results = self.cursor.execute(self.constructed_query, (id,)).fetchall()
			
			#Has to go genome by genome.
			for result in results:
				read_ID, percent_ID, starts, ends = result[0], result[4], result[5], result[6]
				
				if self.in_grp <= percent_ID:
					#We don't care abput where the read falls if whole_range is true, just if pct ID is enough.
					if whole_range:
						self.reads_to_select[self.path_to_sample].append(read_ID)
					else:
					#We need to discover if a range from the read falls in any min/max pair, so we use binary search
						for start, end in zip(starts, ends):
							#An odd start index means the start is <= to a window end 
							#This is also how we detect if and how much we need to add to a non-standard bin (genes), but we don't have to do that right here. Any overlap, and the read is in.
							start_index = bisect_left(interleaved_min_max, start)
							#An odd start index means the start is >= to a window start.
							end_index = bisect_right(interleaved_min_max, end)
							
							if start_index % 2 == 1 or end_index % 2 == 1:
								#print("read_selected")
								self.reads_to_select[self.path_to_sample].append(read_ID)
								#We have determined that the read is in, so stop looking.
								break
			#Check if we actually selected anything.
			if len(self.reads_to_select[self.path_to_sample]) == 0:
				self.reads_to_select[self.path_to_sample] = None
			else:
				#Keep the list in order	and purge dupes.
				self.reads_to_select[self.path_to_sample] = sorted(set(self.reads_to_select[self.path_to_sample]))
		
		return None
	
	#Opens the input assoc. with a file and exports reads in a selection to the output.
	def export_reads_to_file(self):
		#Needs link to file to be done first,
		#Add a header if sam/bam
		for sample in self.reads_to_select:
			#Skip if there's nothing in the cart.
			if len(self.reads_to_select[sample]) == 0:
				continue
			
			output = os.path.splitext(os.path.basename(sample))[0] + "_recplot_filtered" + os.path.splitext(os.path.basename(sample))[1]
			
			header = []
			
			out_file = open(output, "w")
			
			if self.sample_format == "SAM":
				header = get_full_sam_header(sample)
			if self.sample_format == "BAM":
				header = get_full_bam_bam_header(sample)
			
			#This should only happen with a magic blast alignment, but that's OK.
			if self.sample_format == "BLAST":
				fh = open(sample)
				
				for line in fh:
					if line.startswith("#"):
						header.append(line.strip())
					else:
						break
				
				fh.close()
			
			row_ID_counter = 0		
			#If header is empty, this is effectively skipped.
			for line in header:
				#Lines to skip, basically.
				row_ID_counter -= 1
				out_file.write(line)
				out_file.write("\n")
			
			if self.sample_format == "SAM" or self.sample_format == "BLAST":
				input = open(sample, "r")
			#BAM
			if self.sample_format == "BAM":
				input = read(sample)
			
			current_idx_counter = 0
			current_ID_to_seek = self.reads_to_select[sample][0]
			max_id = len(self.reads_to_select[sample])
			
			for line in input:
				row_ID_counter += 1
				
				if row_ID_counter == current_ID_to_seek:
					out_file.write(line)
					current_idx_counter += 1
					if current_idx_counter < max_id:
						current_ID_to_seek = self.reads_to_select[sample][current_idx_counter]
					else:
						#We're done. No need to look further.
						break
					
			out_file.write("\n")
			
			out_file.close()
			
		self.reads_to_select = None
