import re
import datetime
from shutil import copytree, rmtree
from vinca. browser import Browser
from vinca.lib import ansi
from vinca.lib.vinput import VimEditor
from vinca.lib.readkey import readkey
from vinca.lib import casting
from vinca.config import config
from vinca.tag_caching import tags_cache
TODAY = datetime.date.today()

class Cardlist:
	''' this is a collection of cards. most of the user interface takes place through the browser '''


	def __init__(self, _cards):
		# we do not subclass list so that
		# the fire help is not littered
		# with inherited methods
		self._cards = _cards
		self._hotkeys = {'D': self.delete,
				 'T': self.edit_tags,
				 'C': self.count}
		self._confirm_exit_commands = [self.count]

	def __iter__(self):
		return iter(self._cards)

	def __len__(self):
		return len(self._cards)

	def __getitem__(self, slice):
		return self._cards[slice]

	def _insert_card(self, idx, card):
		self._cards.insert(idx, card)

	def __str__(self):
		s = ''
		l = len(self)
		if l == 0:
			return 'No cards.'
		if l > 10:
			s += f'10 of {l}\n'
		s += ansi.codes['line_wrap_off']
		for card in self[:10]:
			if card.due_as_of(TODAY):
				s += ansi.codes['bold']
				s += ansi.codes['blue']
			if card.deleted:
				s += ansi.codes['crossout']
				s += ansi.codes['red']
			s += f'{card}\n'
			s += ansi.codes['reset']
		s += ansi.codes['line_wrap_on']
		return s

	def browse(self):
		''' scroll through your collection with j and k '''
		Browser(self).browse()
	b = browse

	def review(self):
		''' review all cards '''
		Browser(self).review()
	r = review
				
	def add_tag(self, tag):
		for card in self:
			card.tags += [tag]

	def remove_tag(self, tag):
		for card in self:
			if tag in card.tags:
				card.tags.remove(tag)
			# TODO do this with set removal
			card.save_metadata()  # metadata ops should be internal TODO

	def count(self):
		''' simple summary statistics '''
		total_count = len(self)
		due_count = len(self.filter(due_only=True))
		print(f'total	{total_count}')
		print(f'due	{due_count}')

	def edit_tags(self):
		''' add or remove tags from all cards '''
		tags_add = VimEditor(prompt = 'tags to add: ', completions = tags_cache).run().split()
		tags_remove = VimEditor(prompt = 'tags to remove: ', completions = tags_cache).run().split()
		for tag in tags_add:
			self.add_tag(tag)
		for tag in tags_remove:
			self.remove_tag(tag)

	def save(self, save_path):
		''' backup your cards '''
		save_path = casting.to_path(save_path)
		for card in self:
			copytree(card.path, save_path / card.path.name)

	@staticmethod
	def load(load_path, overwrite = False):
		''' load cards from another folder into your collection '''
		load_path = casting.to_path(load_path)
		if overwrite:
			print(f'Overwrite {len(self)} cards? (y/n)')
			if readkey == 'y':
				rmtree(config.cards_path)
				copytree(load_path, config.cards_path)
			return
		for card_path in load_path.iterdir():
			copytree(card_path, config.cards_path / card_path.name)


	def purge(self):
		''' Permanently delete all cards marked for deletion. '''
		deleted_cards = self.filter(deleted_only = True)
		if not deleted_cards:
			print('no cards are marked for deletion.')
			return
		print(f'delete {len(deleted_cards)} cards? (y/n)')
		if readkey() == 'y':
			for card in deleted_cards:
				rmtree(card.path)

	def delete(self):
		for card in self:
			card.delete(toggle = True)



	def filter(self, *,
		   tag = None,
		   create_date_min=None, create_date_max=None,
		   seen_date_min=None, seen_date_max=None,
		   due_date_min=None, due_date_max=None,
		   editor=None, reviewer=None, scheduler=None,
		   deleted_only=False, 
		   due_only=False,
		   new_only=False,
		   invert=False):
		''' filter the collection by a wide array of predicates '''
		
		# cast dates to dates
		create_date_min = casting.to_date(create_date_min)
		create_date_max = casting.to_date(create_date_max)
		seen_date_min = casting.to_date(seen_date_min)
		seen_date_max = casting.to_date(seen_date_max)
		due_date_min = casting.to_date(due_date_min)
		due_date_max = casting.to_date(due_date_max)

		if due_only: due_date_max = TODAY
		# compile the regex pattern for faster searching

		f = lambda card: (((not tag or tag in card.tags) and
				(not create_date_min or create_date_min <= card.create_date) and
				(not create_date_max or create_date_max >= card.create_date) and 
				(not seen_date_min or seen_date_min <= card.seen_date) and
				(not seen_date_max or seen_date_max >= card.seen_date) and 
				(not due_date_min or due_date_min <= card.due_date) and
				(not due_date_max or due_date_max >= card.due_date) and 
				(not editor or editor == card.editor) and
				(not reviewer or reviewer == card.reviewer) and
				(not scheduler or scheduler == card.scheduler) and
				(not deleted_only or card.deleted ) and
				(not new_only or card.new)) ^
				invert)
		
		# matches.sort(key=lambda card: card.seen_date, reverse=True)
		return self.__class__([c for c in self if f(c)])
	f = filter

	def find(self, pattern):
		''' return the first card containing a search pattern '''
		matches = self.findall(pattern)
		matches.sort(criterion = 'seen-date')
		return matches[0] if matches else 'no match found'

	def findall(self, pattern):
		''' return all cards containing a search-pattern '''
		p = re.compile(f'({pattern})')  # wrap in parens to create regex group \1
		contains_pattern = lambda card: p.search(card.string)
		return self.__class__([c for c in self if contains_pattern(c)])

	def sort(self, criterion, *, reverse=False):
		''' sort the collection. criterion
		should be (due-date | seen-date | create-date | time) '''
		crit_dict = {
			'due-date': lambda card: card.create_date,
			'seen-date': lambda card: card.seen_date, 
			'create-date': lambda card: card.create_date,
			'time': lambda card: card.time}
		reverse_crits = ('create-date', 'seen-date', 'time')
		if criterion not in crit_dict:
			print('supply a criterion: create_date | seen_date | due_date')
		reverse = reverse ^ (criterion in reverse_crits)
		self._cards.sort(key = crit_dict[criterion], reverse = reverse)
		return self
	s = sort

	def time(self):
		''' return the total time spend studying these cards '''
		return sum([card.history.time for card in self], start=datetime.timedelta(0))

	def range(self):
		''' useful for writing shell functions '''
		for i, card in enumerate(self):
			print(i)

	def cut(self, idx):
		self._cards[idx:] = []
		return self
	

