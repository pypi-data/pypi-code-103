from __future__ import division
from enum import Enum
import sys

from Track import Track, TagEnum
from Note import Note, NUM_NOTES
import numpy as py
from Control import Control


class chainType(Enum):
    NOTE = 0
    CHORD = 1


class DynamicMarkovChain:

    def __init__(self, name, chain_type=chainType.NOTE, token_length=1):
        """Constructor for Markov Chains

        Args:
            name (String): Name of the chain
            type (String): Type of chain (TODO: to be replaced with an enumeration)
        """
        self.name = name
        self.token_length = token_length
        self.chain_type = chain_type
        self.probabilities = {}

    def add_song(self, song):
        """Ingests a song and adds to the total dictionary. When all note changes are added,
        divides all elements in the dictionary by the total amount of note changes recorded and
        stores this in self.probabilities, which will give the probability matrix.

        Args:
            song (Song): Song to ingest and generate probabilities from
            num_tokens (int): Tells the amount of tokens for each pattern

        Returns:
            dict(string:[(int, int)]): Dictionary of note tokens as keys and lists of tuples with a note
            and percentage of occurrences
        """
        if self.chain_type is chainType.NOTE:
            return self.add_notes(song)
        else:
            return self.add_chords(song)

    def generate_next_note(self, current_note_token):
        """Given a token of previous notes, this will randomly generate a new note given the percetanges from
            the markov chain object.

            Args:
                current_note_token (String): A string of 'token_length' notes in C-index

            Returns:
                int, String: An int of the next note and a string of the new pattern token.
        """
        orig_token = current_note_token
        # If this token is the end of the song, we need to begin in a new position
        if self.probabilities.get(current_note_token) is None:
            # Let's check if there are any other similar patterns in the song
            for i in range(NUM_NOTES):
                new_pattern = current_note_token[:len(current_note_token) - 2] + str(i)
                if new_pattern in list(self.probabilities.keys()):
                    current_note_token = new_pattern
                    break
            # If not, let's just randomly pick a new position to continue in the chain
            if orig_token == current_note_token:
                current_note_token = py.random.choice(list(self.probabilities.keys()))
        note_follow = self.probabilities.get(current_note_token)
        percentage = []
        # print(note_follow)
        # Create a 1-D array of the percentage of a given note with this pattern token
        for i in range(NUM_NOTES):
            found = False
            for note in note_follow:
                if i == note[0]:
                    percentage.append(note[1])
                    found = True
            if not found:
                percentage.append(0)
        # Pick a random new note with the percentages and return the note and new pattern
        print(percentage)
        next_note = py.random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 1, p=percentage)
        return next_note[0], current_note_token

    def generate_next_chord(self, current_chord_token):
        if self.probabilities.get(current_chord_token) is None:
            # Let's just randomly pick a new position to continue in the chain
            current_chord_token = py.random.choice(list(self.probabilities.keys()))
        # Get all the chords that have followed our current token in a list
        chord_follow = self.probabilities.get(current_chord_token)
        percentage = []
        available_chords = []
        # Store the total chords and the percentage chance that they occur
        for chord in chord_follow:
            available_chords.append(chord[0])
            percentage.append(chord[1])
        # Choose a chord with the given percentages and return it
        next_chord = py.random.choice(available_chords, 1, p=percentage)
        return next_chord[0], current_chord_token

    def generate_pattern(self, song, num_notes, instrument=0, arpeggio=False, octave=3):
        """ Given a new song object and the number of notes to generate, this method will load that
            amount of new notes into a new track using the existing markov chain.

            Args:
                song (Song): A brand new Song object
                num_notes (int): The number of notes to generate
                instrument (int): the number you want for instrument

            Returns:
                Track: The generated track
        """
        # We are currently making every note an eighth note
        # and every chord a half not for easier testing
        eighth_note = int(song.ticks_per_beat / 2)
        half_note = int(song.ticks_per_beat * 2)
        t = Track()
        # Start at a random place in the markov chain
        current_token = py.random.choice(list(self.probabilities.keys()))
        if self.chain_type is chainType.NOTE:
            current_token_array = current_token.split()
            # Add the beginning notes
            for i in range(self.token_length):
                t.add_note(Note(pitch=int(current_token_array[i]) + (octave * 12), time=i * eighth_note, duration=eighth_note))
            # Iterate through the rest of the song
            for i in range(self.token_length, num_notes):
                # Keep generating a new note until it is not dissonant with the current notes being played
                while True:
                    new_note_needed = False
                    # Generate new note for song
                    next_note_rtn = self.generate_next_note(current_token)
                    next_note_tone, current_token = next_note_rtn[0], next_note_rtn[1]
                    # Get all the notes that occur at this time to see if there is dissonance
                    curr_notes = song.get_notes_at_time(time=i * eighth_note)
                    for note in curr_notes:
                        if abs(next_note_tone - note.c_indexed_pitch_class) <= 1:
                            # Then the note will be dissonant
                            new_note_needed = True
                            if len(self.probabilities.get(current_token)) == 1:
                                current_token = py.random.choice(list(self.probabilities.keys()))

                    if not new_note_needed:
                        break
                print(next_note_tone)
                # Create the new pattern with the new note
                if self.token_length == 1:
                    current_token = str(next_note_tone)
                else:
                    # We need to change the pattern token by adding the new note
                    previous_pattern = current_token.split()
                    current_token = previous_pattern[1]
                    for j in range(2, self.token_length):
                        current_token += " " + previous_pattern[j]
                    current_token += " " + str(next_note_tone)
                # Adding the specified octave is a way to bump the notes up (default 3) octaves so it sounds better
                next_note_tone += (octave * 12)  # Bump up three octave
                new_note = Note(pitch=next_note_tone, time=i * eighth_note, duration=eighth_note)
                # There is a one in seven chance that we have a rest
                if not py.random.randint(0, 7):
                    new_note.velocity = 0
                t.add_note(new_note)
        # Here we are doing the same thing but for chords
        else:
            # We split the token to get all the individual chords
            current_token_array = current_token.split(',')
            # We add all the initial notes to the track before iterating
            for i in range(self.token_length):
                current_chord = current_token_array[i].split()
                for j in range(len(current_chord)):
                    t.add_note(Note(pitch=int(current_chord[j]) + (octave * 12), time=i * half_note, duration=half_note))
            # Now we can iterate until we have made enough notes
            for i in range(self.token_length, num_notes):
                # Check if there is dissonance in the new chord
                while True:
                    # Get new chord and token
                    new_note_needed = False
                    next_chord_rtn = self.generate_next_chord(current_token)
                    next_chord, current_token = next_chord_rtn[0], next_chord_rtn[1]
                    # Get all notes that occur at this time to see if there is dissonance
                    curr_notes = song.get_notes_at_time(time=i * eighth_note)
                    for note in curr_notes:
                        curr_chord = next_chord.split()
                        for chord_note in curr_chord:
                            if abs(chord_note - note.c_indexed_pitch_class) <= 1:
                                # The chord is dissonant
                                new_note_needed = True
                                if len(self.probabilities.get(current_token_array)) == 1:
                                    current_token_array = py.random.choice(list(self.probabilities.keys()))

                    if not new_note_needed:
                        break
                print(next_chord)
                if self.token_length == 1:
                    current_token = next_chord
                else:
                    # We need to change the token so it has the new chord in it
                    current_token = current_token_array[1]
                    for j in range(2, self.token_length):
                        current_token += "," + current_token_array[j]
                    current_token += "," + next_chord
                next_chord_array = next_chord.split()
                # If the user wants arpeggio then split the chord up by 32nd notes
                offset = int(eighth_note / 4)
                for j in range(len(next_chord_array)):
                    if not arpeggio:
                        t.add_note(Note(pitch=int(next_chord_array[j]) + (octave * 12), time=i * half_note, duration=half_note))
                    else:
                        t.add_note(Note(pitch=int(next_chord_array[j]) + (octave * 12), time=(i * half_note) + offset,
                                        duration=half_note))
                        offset += int(eighth_note / 4)

        t.controls.append(Control(msg_type='program_change', instrument=instrument, time=0))
        return t

    def add_chords(self, song):
        """Given a song object, this will add all the chords to our probability dictionary AKA
        markov chain and create the percentages for them.

        Args:
            song (Song): Song to ingest and generate probabilities from
            num_tokens (int): Tells the amount of tokens for each pattern

        Returns:
            dict(string:[(int, int)]): Dictionary of note tokens as keys and lists of tuples with a note
            and percentage of occurrences
        """
        # Get all notes from song in one list
        all_chords = []
        for track in song.tracks:
            if not track.chords or track.tag == TagEnum.PERCUSSION:
                continue
            all_chords += track.chords

        if not all_chords:
            raise AttributeError('There are no chords in this song.')
        # Get first x notes of song
        previous_pattern = all_chords[0].to_string()
        previous_pattern += ","
        for i in range(1, self.token_length):
            previous_pattern += all_chords[i].to_string()
            previous_pattern += ","
        previous_pattern = previous_pattern[:len(previous_pattern) - 2]
        print(previous_pattern)

        # Create dictionary
        pattern_dict = self.probabilities
        # for the rest of the song, look at next chord
        for i in range(self.token_length, len(all_chords)):
            next_chord = all_chords[i].to_string()
            # Add that and the new note as a key/value entry.
            if pattern_dict.get(previous_pattern) is None:

                pattern_dict[previous_pattern] = [[next_chord, 1]]
            # We need to check if the pattern and chord combo exists already
            else:
                found = False
                for chord in pattern_dict.get(previous_pattern):
                    if chord[0] == next_chord:
                        chord[1] = chord[1] + 1
                        found = True
                        break
                if not found:
                    pattern_dict.get(previous_pattern).append([next_chord, 1])
            # Finally, we create the new token to continue
            previous_pattern = all_chords[i - self.token_length].to_string()
            previous_pattern += ","
            for j in range(i - self.token_length + 1, i):
                previous_pattern += " " + all_chords[j].to_string()
                previous_pattern += ","
            previous_pattern = previous_pattern[:len(previous_pattern) - 2]

        # Value would be a list of lists with note and count [(0, 1), (1, 2)]
        # If the key/value pair already exists, add one to count
        for value in pattern_dict.values():
            total = 0.0
            for chord in value:
                total += chord[1]
            for chord in value:
                chord[1] = (chord[1] / total)

        self.probabilities = pattern_dict
        print(pattern_dict)
        return pattern_dict
        # Key is the same pattern, value is a list of all the percentages. [0, 0.5, 0.05, 0.25, ...]

    def add_notes(self, song):
        """Ingests a song and adds to the total dictionary. When all note changes are added,
        divides all elements in the dictionary by the total amount of note changes recorded and
        stores this in self.probabilities, which will give the probability matrix.

        Args:
            song (Song): Song to ingest and generate probabilities from
            num_tokens (int): Tells the amount of tokens for each pattern

        Returns:
            dict(string:[(int, int)]): Dictionary of note tokens as keys and lists of tuples with a note
            and percentage of occurrences
        """
        # Get all notes from song in one list
        all_notes = []
        for track in song.tracks:
            if not track.notes or track.tag == TagEnum.PERCUSSION:
                continue
            for note in track.notes:
                if note.chord_note is True:
                    continue
                all_notes.append(note)
        all_notes.sort(key=lambda notes: notes.time)
        # Get first x notes of song
        previous_pattern = str(all_notes[0].c_indexed_pitch_class)
        for i in range(1, self.token_length):
            note = all_notes[i]
            previous_pattern += " " + str(note.c_indexed_pitch_class)

        # Create dictionary
        pattern_dict = self.probabilities
        # for the rest of the song, look at next note
        for i in range(self.token_length, len(all_notes)):
            next_note = all_notes[i].c_indexed_pitch_class
            # Add that and the new note as a key/value entry.
            if pattern_dict.get(previous_pattern) is None:

                pattern_dict[previous_pattern] = [[next_note, 1]]
            else:
                found = False
                for note in pattern_dict.get(previous_pattern):
                    if note[0] == next_note:
                        note[1] = note[1] + 1
                        found = True
                        break
                if not found:
                    pattern_dict.get(previous_pattern).append([next_note, 1])

            previous_pattern = str(all_notes[i - self.token_length].c_indexed_pitch_class)
            for j in range(i - self.token_length + 1, i):
                note = all_notes[j]
                previous_pattern += " " + str(note.c_indexed_pitch_class)

        # Value would be a list of lists with note and count [(0, 1), (1, 2)]
        # If the key/value pair already exists, add one to count
        for value in pattern_dict.values():
            total = 0.0
            for note in value:
                total += note[1]
            for note in value:
                note[1] = (note[1] / total)

        self.probabilities = pattern_dict
        print(pattern_dict)
        return pattern_dict
        # Key is the same pattern, value is a list of all the percentages. [0, 0.5, 0.05, 0.25, ...]
