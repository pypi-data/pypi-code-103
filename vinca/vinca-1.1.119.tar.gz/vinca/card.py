import subprocess
import json
import datetime
TODAY = datetime.date.today()
DAY = datetime.timedelta(days=1)
from pathlib import Path
from shutil import copytree

from vinca import reviewers, editors, schedulers 
from vinca.tag_caching import tags_cache
from vinca.config import config
from vinca.lib.vinput import VimEditor
from vinca.lib.random_id import random_id
from vinca.history import History, HistoryEntry

class Card:
	# Card class can load without 
	default_metadata = {'editor': 'base', 'reviewer':'base', 'scheduler':'base',
			    'tags': [], 'history': History([HistoryEntry(TODAY, 0, 'create')]), 'deleted': False,
			    'due_date': TODAY, 'string': ''}

	def __init__(self, path=None, create=False):
		assert (path is not None) ^ create
		if path:
			self.init_loaded_card(path)
		elif create:
			self.init_new_card()
		self._hotkeys = {'e': self.edit,
				'E': self.edit_metadata,
				'M': self.print_metadata,
				't': self.edit_tags,
				'd': self.delete,
				's': self.summarize,
				'r': self.review,
				'+': self.postpone}
		self._confirm_exit_commands = [self.print_metadata, self.summarize]

	def init_loaded_card(self, path):
		self.path = path
		self.metadata_is_loaded = False

	def init_new_card(self):
		# create card location
		self.path = self.new_path()
		self.path.mkdir()
		# initialize metadata
		self.metadata = Card.default_metadata
		self.metadata_is_loaded = True
		self.save_metadata()
		# easy access to the last created card
		config.last_card_path = self.path

	def summarize(self):
		s  = f'due	{self.due_date}\n'
		s += f'seen	{len(self.history)}x\n'
		s += f'time	{self.history.time}s\n'
		print(s)

	@property
	def metadata_path(self):
		return self.path / 'metadata.json'

	def load_metadata(self):
		self.metadata = json.load(self.metadata_path.open())
		# dates must be serialized into strings for json
		# I unpack them here
		self.metadata['history'] = History.from_json_list(self.metadata['history'])
		assert self.metadata['history'], f'empty history metadata for {self.path}'
		self.metadata['due_date'] = datetime.date.fromisoformat(self.metadata['due_date'])
		self.metadata_is_loaded = True

	def save_metadata(self):
		json.dump(self.metadata, self.metadata_path.open('w'), default=str, indent=2)

	for m in default_metadata.keys():
		# create getter and setter methods for everything in the metadata dictionary
		exec(f'''
@property
def {m}(self):
	if not self.metadata_is_loaded:
		self.load_metadata()
	return self.metadata["{m}"]''')
		exec(f'''
@{m}.setter
def {m}(self, new_val):
	if not self.metadata_is_loaded:
		self.load_metadata()
	self.metadata["{m}"] = new_val
	self.save_metadata()''')	

	# overwrite the tags setter with one modification
	# we want to update the tags_cache
	@tags.setter
	def tags(self, tags):
		if not self.metadata_is_loaded:
			self.load_metadata()
		self.metadata['tags'] = tags
		self.save_metadata()
		tags_cache.add_tags(tags)

	def __str__(self):
		return self.string

	def review(self):
		reviewers.review(self)
		self.save_metadata() # we have probably appended a history entry
		self.schedule()

	def make_string(self):
		self.string = reviewers.make_string(self)

	def edit(self):
		editors.edit(self) 
		self.make_string()
		self.save_metadata() # we have probably modified history

	def edit_metadata(self):
		subprocess.run(['vim',self.path/'metadata.json'])
		self.load_metadata()
		self.make_string()

	def print_metadata(self):
		for k,v in self.metadata.items():
			history_newline = '\n' if k=='history' else ''
			print(f'{k:20}', history_newline, v, sep='', end='\n\n')

	def schedule(self):
		if dd := schedulers.schedule(name=self.scheduler, history=self.history):
			self.due_date = dd

	def copy(self, new_path):
		new_path.mkdir()
		copytree(self.path, new_path)

	def new_path(self):
		return config.cards_path / ('card-' + random_id())

	def delete(self, toggle=True):
		if toggle:
			self.deleted = not self.deleted
		elif not toggle:
			self.deleted = True

	def due_as_of(self, date):
		return self.due_date <= date

	@property
	def is_due(self):
		return self.due_as_of(TODAY)

	def edit_tags(self):
		self.tags = VimEditor(prompt = 'tags: ', text = ' '.join(self.tags), completions = tags_cache).run().split()

	def postpone(self):
		tomorrow = TODAY + DAY
		self.due_date = tomorrow

	@property
	def create_date(self):
		return self.history.create_date

	@property
	def seen_date(self):
		return self.history.last_date

	@property
	def new(self):
		return self.history.new


	@property
	def time(self):
		return self.history.time
