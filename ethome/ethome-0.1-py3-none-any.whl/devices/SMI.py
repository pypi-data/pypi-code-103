from glasses import Glasses
import os.path
import time
import serial
from libopensesame import exceptions
from openexp.canvas import canvas
from openexp.keyboard import keyboard
from openexp.synth import synth

class SMI(Glasses):
    """A child class of Glasses, which will contain functions just for calling
    the SMI API.

    Arguments:
        Glasses {[type]} -- [description]
    """

    def __init__(self):
        super().__init__()

class LibSMI:

	def __init__(self, experiment, port='COM1', baudrate=115200, sound=True):
	
		self.experiment = experiment
		self.tracker = serial.Serial(port=port, baudrate=baudrate, timeout=0.5)		
		self.my_keyboard = keyboard(experiment)
		self.my_canvas = canvas(experiment)
		self.streaming = False
		self.sound = sound
		if self.sound:
			self.beep1 = synth(self.experiment, freq=220)
			self.beep1.volume(0.5)
			self.beep2 = synth(self.experiment, freq=440, length=200)
			self.beep2.volume(0.5)
		self.stop_recording()
		
	def send(self, msg, sleep=10):
		
		self.tracker.write('%s\t\n' % msg)
		self.experiment.sleep(sleep)
		
	def recv(self):
		
		s = ''
		while True:
			c = self.tracker.read(size=1)		
			if c == None:
				raise exceptions.runtime_error('The tracker said "%s"' % s)
			if c == '\n':
				if len(s) > 1:
					break
				else:
					s = ''
					continue
			s += c
		return s[:-1]
				
	def calibrate(self, nr_of_pts=9):

		h = self.experiment.get('height')
		w = self.experiment.get('width')
		m = 0.05 * w
		
		# ET_CPA [command] [enable]
		self.send('ET_CPA 0 1') # Enable wait for valid data
		self.send('ET_CPA 1 1') # Enable randomize point order
		self.send('ET_CPA 2 1') # Enable auto accept

		# ET_LEV [calibration level]
		self.send('ET_LEV 2') # Set to medium

		# ET_CSZ [xres] [yres]
		self.send('ET_CSZ %d %d' % (w, h)) # Set the screen resolution

		# Start the calibration with default calibration points
		self.send('ET_DEF')
		self.send('ET_CAL %d' % nr_of_pts)
		
		pts = {}
		while True:

			# Poll the keyboard to capture escape pressed
			self.my_keyboard.get_key(timeout=0)	

			# Receive a line from the tracker and split it
			s = self.recv()
			cmd = s.split()

			# Ignore empty commands	
			if len(cmd) == 0:
				continue
	
			# Change thc coordinates of the calibration points
			if cmd[0] == 'ET_PNT':
				pt_nr = int(cmd[1])
				x = int(cmd[2])
				y = int(cmd[3])
				pts[pt_nr-1] = x, y
	
			# Indicates that the calibration point has been changed
			elif cmd[0] == 'ET_CHG':				
				pt_nr = int(cmd[1])
				if pt_nr-1 not in pts:
					raise exceptions.runtime_error('Something went wrong during the calibration. Please try again.')
				x, y = pts[pt_nr-1]
				self.my_canvas.clear()
				self.my_canvas.fixdot(x, y)
				self.my_canvas.show()
				if self.sound:
					self.beep1.play()
		
			# Indicates that the calibration was successful
			elif cmd[0] == 'ET_FIN':
				break
		
		# Initially recording is off
		self.stop_recording()
		
		if self.sound:
			self.beep2.play()
		
	def save_data(self, path=None):
		if path == None:
			path = os.path.splitext(os.path.basename(self.experiment.logfile))[0] + time.strftime('_%m_%d_%Y_%H_%M') + '.idf'
		self.send('ET_SAV "%s"' % path)
				
	def start_recording(self, stream=True):
		
		self.send('ET_REC')

		if stream:
			self.streaming = True
			self.send('ET_FRM "%SX %SY"')
			self.send('ET_STR')
		else:
			self.streaming = False
			
	def stop_recording(self):
	
		if self.streaming:
			self.send('ET_EST')
		self.send('ET_STP')
		self.streaming = False
		
	def clear(self):
		
		self.tracker.flushInput()
		
	def sample(self, clear=False):
	
		if not self.streaming:
			raise exceptions.runtime_error("Please set stream=True in start_recording() before using sample()")
			
		if clear:
			self.tracker.flushInput()
		
		while True:
			s = self.recv()
			l = s.split()
			if len(l) > 0 and l[0] == 'ET_SPL':
				try:
					x = int(l[1])
					if len(l) == 5:
						y = int(l[3]) # Binocular
					else:
						y = int(l[2]) # One eye
					break
				except:
					pass
				
		return x, y
		
	def log(self, msg):
		
		self.send('ET_REM "%s"' % msg)
		
	def cleanup(self):
	
		"""Neatly close the tracker"""
	
		self.tracker.close()		
		
def prepare(item):

	item.experiment.tracker = LibSMI(item.experiment)
	item.experiment.cleanup_functions.append(item.experiment.tracker.cleanup)

def run(item):
	pass