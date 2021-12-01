from __future__ import division
from enum import Enum
import sys

from Track import Track
from Note import Note
import numpy as py


class MarkovChain:

    def __init__(self, name, type):
        """Constructor for Markov Chains

        Args:
            name (String): Name of the chain
            type (String): Type of chain (TODO: to be replaced with an enumeration)
        """        
        assert isinstance(type, Type)
        self.name = name
        self.type = type
        self.totalCt = None
        self.totals = None
        self.probabilities = None

    def add_track(self, track):
        """Ingests a track and adds to the 2d totals array. When all note changes are added,
        divides all elements in the 2d array by the total amount of note changes recorded and
        stores this in self.probabilities, which will give the probability matrix.

        Args:
            track (Track): Track to ingest and generate probabiliites from

        Returns:
            int[][]: Matrix of probabiliites
        """        
        assert isinstance(track, Track)
        if self.type == Type.NOTE_LENGTH:
            if self.probabilities == None:
                self.totalCt = {}
                self.totals = {}
                self.probabilities = {}
            # Go through song and calculate probabilities of each note length based on the previous note length
            for i in range(0, len(track.notes) - 1):
                if self.totalCt.get(track.notes[i].duration) != None:
                    self.totalCt[track.notes[i].duration] += 1
                else:
                    self.totalCt[track.notes[i].duration] = 1
                # Add an occurance for track.note[i] -> track.note[i+1]
                if self.totals.get([track.notes[i].duration, track.notes[i + 1].duration]) != None:
                    self.totals[track.notes[i].duration, track.notes[i + 1].duration] += 1
                else:
                    self.totals[track.notes[i].duration, track.notes[i + 1].duration] = 1
            # self.probabilities = self.totals / totalCt
            for key, val in self.totals: # Probably not workings 
                self.probabilities[key] = val / max(self.totalCt.get(key), 1)
            return self.probabilities
        elif self.type == Type.NOTE_TONE:
            if self.probabilities is None:
                self.totalCt = py.zeros(12)
                self.totals = py.zeros((12, 12))
                self.probabilities = py.zeros((12, 12))
            # Go through song and calculate probabilities of each note tonic based on the previous note tonic
            # Make 2D array of length 12 x 12 for each note
            for i in range(0, len(track.notes) - 1):
                self.totalCt[track.notes[i].c_indexed_pitch_class] += 1
                # Add an occurance for track.note[i] -> track.note[i+1]
                self.totals[track.notes[i].c_indexed_pitch_class, track.notes[i + 1].c_indexed_pitch_class] += 1
            # self.probabilities = self.totals / totalCt
            for idx in range(0, 12):
                if self.totalCt[idx] == 0:
                    self.totalCt[idx] = 1
                self.probabilities[idx] = self.totals[idx] / self.totalCt[idx]
            return self.probabilities
        elif self.type == Type.CHORD_TONE:
            return "Not yet implemented"
        elif self.type == Type.CHORD_LENGTH:
            return "Not yet implemented"

    def generate_next_note(self, current_note):
        if self.type == Type.NOTE_TONE:
            next_note = py.random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 1, p=self.probabilities[current_note])
            return next_note[0]
        if self.type == Type.NOTE_LENGTH:
            raise NotImplementedError

class Type(Enum):
    NOTE_TONE = 0
    NOTE_LENGTH = 1
    CHORD_TONE = 2
    CHORD_LENGTH = 3
