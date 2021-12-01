from markov_chain import MarkovChain
import numpy as py
from Track import Track
from Note import Note

class MarkovLibrary:

    def __init__(self):
        self.chains = {}
    
    def add_markov_chain(self, chain):
        self.chains[chain.name] = chain

    def generate_pattern(self, song, num_notes, note_tone_chain=None, note_length_chain=None):
        t = Track()
        song.add_track(t)
        current_note = py.random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 1)[0]
        t.add_note(Note(pitch=current_note+35, time=0, duration=100))
        for i in range (1, num_notes):
            if note_tone_chain != None:
                next_note_tone = note_tone_chain.generate_next_note(current_note)
                current_note = next_note_tone
            else:
                next_note_tone = py.random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 1)[0]
            next_note_tone += 35 # Bump up three octaves
            if note_length_chain != None:
                next_note_length = note_length_chain.generate_next_note(current_note)
                current_note = next_note_tone
            else:
                next_note_length = py.random.choice([1, 2, 3], 1)[0]*100
            time = i*(py.random.choice([75, 100, 125, 150], 1)[0])
            t.add_note(Note(pitch=next_note_tone, time=time, duration=next_note_length))
