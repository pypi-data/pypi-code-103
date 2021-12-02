import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/Users/erinlitty/Desktop/CSC492/2021FallTeam17-DeHaan/src')

from Track import Track
from Key import Key, KEYS
from Scale import SCALE_TYPES
from Note import Note, NUM_NOTES
import FileIO as FileIO


class Chord:

    # Constructor, takes all fields as inputs
    def __init__(self, notes=None, name=None, time=0):
        if notes is None:
            notes = []
        self.notes = notes
        notes.sort(key=lambda x: x.pitch)
        self.name = name
        self.time = time

    def to_string(self):
        new_string = str(self.notes[0].c_indexed_pitch_class)
        for i in range(1, len(self.notes)):
            new_string += " " + str(self.notes[i].c_indexed_pitch_class)
        return new_string

    def duplicate_chord(self):
        notes = []
        for note in self.notes:
            notes.append(note.duplicate_note())
        return Chord(notes=notes, name=self.name, time=self.time)

