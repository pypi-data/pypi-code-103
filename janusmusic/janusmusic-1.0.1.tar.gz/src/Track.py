import logging

import Note
from enum import Enum

# The channel percussion information will be on
PERCUSSION_CHANNEL = 9
# The average note pitch on a track must be below this number to be considered a bass track
BASS_AVERAGE = 45
# The chord to note ratio required to classify a track as "chords"
CHORD_PERCENTAGE = 0.15


class Track:

    def __init__(self, notes=None, controls=None, track_name=None, device_name=None, chords=None, channel=0):
        """ Constructor for the Track object

        Args:
            notes (Note[], optional): List of Notes within this track. Defaults to None.
            controls (Control[], optional): List of Control messages within this track. Defaults to None.
            track_name (String, optional): Name of this track. Defaults to None.
            device_name (String, optional): Instrument used on this track. Defaults to None.
            channel (int, optional): Channel of this track. Defaults to 0.
        """        
        if notes is None:
            notes = []
        if chords is None:
            chords = []
        # Control messages (and program change messages) store data about how the track should be played back,
        # but are not necessarily "events" in the file. These can occur at any point during a song
        if controls is None:
            controls = []
        self.notes = notes
        self.controls = controls
        self.track_name = track_name
        self.device_name = device_name
        self.channel = channel
        self.chords = chords
        self.tag = TagEnum.NONE

        if channel is PERCUSSION_CHANNEL:
            self.is_percussion = True
        else:
            self.is_percussion = False

    def add_note(self, note=None):
        """ Adds a note to the end of this track

        Args:
            note (Note): Note to append to the song. Defaults to None.
        """        
        self.notes.append(note)

    def add_chord(self, chord=None):
        """ Adds a chord to the track array

        Args:
            chord (Chord): Note to append to the song. Defaults to None.
        """
        self.chords.append(chord)

    def get_c_indexed_note_frequencies(self):
        """ Returns an array representing each note's number of appearances in this track, starting
        with C.

        Returns:
            int[]: Note frequencies array
        """        
        c_indexed_frequencies = [0] * Note.NUM_NOTES

        for note in self.notes:
            c_indexed_frequencies[note.c_indexed_pitch_class] += 1

        return c_indexed_frequencies

    def generate_tags(self):
        """ Sets 'tag' field in the song to the appropriate tag based on its attributes
        This method assumes a track is only used for one section of a song and does not
        dramatically change roles during the song (ex, switch from guitar track to vocal
        track)

        """
        if len(self.notes) == 0:
            self.tag = TagEnum.NONE

        elif self.channel is PERCUSSION_CHANNEL:
            self.tag = TagEnum.PERCUSSION

        else:
            pitch_total = 0
            for note in self.notes:
                pitch_total += note.pitch
            if pitch_total / len(self.notes) < BASS_AVERAGE:
                self.tag = TagEnum.BASS      # If the average note pitch is lower than BASS_AVERAGE
            elif len(self.chords) > CHORD_PERCENTAGE * len(self.notes):
                self.tag = TagEnum.CHORDS
            else:
                self.tag = TagEnum.MELODY    # If nothing else fits, this is likely a melody track

    def get_all_chords(self):
        return self.chords

    def get_unique_chords(self):
        chord_set = set()
        return [x for x in self.chords if x not in chord_set and not chord_set.add(x)]

    def append_track(self, track):
        """
        "Glues" two tracks together. Returns a new track with the contents of the two given tracks. Does not modify
        either track.

        :param track: The track to attach to the end of this track
        :return: A new track with the contents of the two tracks played consecutively.
        """

        if track is None:
            raise AttributeError("Track must not be None")

        last_event_time = 0
        for note in self.notes:
            if note.time + note.duration > last_event_time:
                last_event_time = note.time + note.duration
        for control in self.controls:
            if control.time > last_event_time:
                last_event_time = control.time

        new_self = self.duplicate_track()
        new_track = track.duplicate_track()

        for note in new_track.notes:
            if not note.chord_note:
                note.time += last_event_time
                new_self.notes.append(note)

        for control in new_track.controls:
            control.time += last_event_time
            new_self.controls.append(control)

        for chord in new_track.chords:
            chord.time += last_event_time
            new_self.chords.append(chord)

            for note in chord.notes:
                note.time += last_event_time
                new_self.notes.append(note)

        return new_self

    def append_tracks(self, pattern=None, sections=None):
        """Takes a pattern as an array of ints (Ex. [0, 0, 1, 1, 2, 1, 0]) and strings together
        tracks (supplied in sections) in the pattern given. For example, if the given pattern is [0, 1, 2, 1, 0] and
        the given sections are in the format [a, b, c], this will return a new track with the structure (a b c b a).

        Params:
        pattern: An array of ints used to dictate the pattern of tracks to return. The highest value must be less
            than the length of "sections"
        sections: A list of tracks that will be glued together in this method. The order given will determine how
            the pattern is constructed (ie. the index of each section in the list corresponds to the int value in
            "pattern" that will be used to represent it)

        Returns:
            A new track with the given sections attached to it in the given pattern.
        """
        new_track = self.duplicate_track()
        for i in range(len(pattern)):
            new_track = new_track.append_track(sections[pattern[i]])

        return new_track

    def duplicate_track(self):
        """
        Returns a new track with identical contents to the given track. Does not modify the given track.
        :return: a new track with identical contents to the given track.
        """
        notes = []
        controls = []
        chords = []

        for note in self.notes:
            if not note.chord_note:
                notes.append(note.duplicate_note())

        for control in self.controls:
            controls.append(control.duplicate_control())

        for chord in self.chords:
            chords.append(chord.duplicate_chord())
            for note in chord.notes:
                notes.append(note.duplicate_note())

        return Track(notes=notes, controls=controls, track_name=self.track_name, device_name=self.device_name,
                     chords=chords, channel=self.channel)

    def equals(self, track):
        """
        Returns true if these two tracks are equal. If they are not equal, prints an info log message with more details
        and return false
        :param track: The track to compare this track to
        :return: True, if the contents of the track are equal. False otherwise.
        """
        if self.channel != track.channel:
            logging.info(msg="tracks " + track.track_name + " have different channel values")
            logging.info(msg="This: " + self.channel + ", compare to: " + track.channel)
            return False

        if self.track_name != track.track_name:
            logging.info(msg="tracks " + track.track_name + " have different track names :")
            logging.info(msg="This: '" + self.track_name + "', compare to: '" + track.track_name + "'")
            return False

        if self.device_name != track.device_name:
            logging.info(msg="tracks " + track.track_name + " have different device names")
            logging.info(msg="This: '" + self.device_name + "', compare to: '" + track.device_name + "'")
            return False

        if len(self.controls) != len(track.controls):
            logging.info(msg="tracks " + track.track_name + " have different numbers of control messages")
            logging.info(msg="This: " + str(len(self.controls)) + ", compare to: "
                             + str(len(track.controls)))
            return False

        for j, control in enumerate(self.controls):
            if control.msg_type != track.controls[j].msg_type:
                logging.info(msg="tracks " + track.track_name + " control " + str(j) + " have different message types")
                logging.info(msg="This: '" + control.msg_type + "', compare to: '"
                                 + track.controls[j].msg_type + "'")
                return False

            if control.control != track.controls[j].control:
                logging.info(msg="tracks " + track.track_name + " control " + str(j) + " have different control numbers")
                logging.info(msg="This: " + str(control.control) + ", compare to: "
                                 + str(track.controls[j].control))
                return False

            if control.value != track.controls[j].value:
                logging.info(msg="tracks " + track.track_name + " control " + str(j) + " have different values")
                logging.info(msg="This: " + str(control.value) + ", compare to: "
                                 + str(track.controls[j].value))
                return False

            if control.tempo != track.controls[j].tempo:
                logging.info(msg="tracks " + track.track_name + " control " + str(j) + " have different tempos")
                logging.info(msg="This: " + str(control.tempo) + ", compare to: "
                                 + str(track.controls[j].tempo))
                return False

            if control.instrument != track.controls[j].instrument:
                logging.info(msg="tracks " + track.track_name + " control " + str(j) + " have different instruments")
                logging.info(msg="This: " + str(control.instrument) + ", compare to: " + str(
                    track.controls[j].instrument))
                return False

            if control.time != track.controls[j].time:
                logging.info(msg="tracks " + track.track_name + " control " + str(j) + " have different times")
                logging.info(msg="This: " + str(control.time) + ", compare to: "
                                 + str(track.controls[j].time))
                return False

        if len(self.notes) != len(track.notes):
            logging.info(msg="tracks " + track.track_name + " have different numbers of notes")
            logging.info(msg="This: " + str(len(track.notes)) + ", compare to: " + str(len(track.notes)))
            return False

        for j, note in enumerate(self.notes):
            if note.pitch != track.notes[j].pitch:
                logging.info(msg="tracks " + track.track_name + " note " + str(j) + " have different pitches")
                logging.info(msg="This: " + str(note.pitch) + ", compare to: " + str(track.notes[j].pitch))
                return False

            if note.time != track.notes[j].time:
                logging.info(msg="tracks " + track.track_name + " note " + str(j) + " have different times")
                logging.info(msg="This: " + str(note.time) + ", compare to: " + str(track.notes[j].time))
                return False

            if note.duration != track.notes[j].duration:
                logging.info(msg="tracks " + track.track_name + " note " + str(j) + " have different durations")
                logging.info(msg="This: " + str(note.duration) + ", compare to: "
                                 + str(track.notes[j].duration))
                return False

            if note.velocity != track.notes[j].velocity:
                logging.info(msg="tracks " + track.track_name + " note " + str(j) + " have different velocities")
                logging.info(msg="This: " + str(note.velocity) + ", compare to: "
                                 + str(track.notes[j].velocity))
                return False

            if note.channel != track.notes[j].channel:
                logging.info(msg="tracks " + track.track_name + " note " + str(j) + " have different channels")
                logging.info(msg="This: " + str(note.channel) + ", compare to: "
                                 + str(track.notes[j].channel))
                return False
        return True


class TagEnum(Enum):
    NONE = 0
    MELODY = 1
    CHORDS = 2
    BASS = 3
    PERCUSSION = 4


