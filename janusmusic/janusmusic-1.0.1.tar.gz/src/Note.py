# This object represents each note in the song, and stores data about each note
NUM_NOTES = 12
MIDDLE_C = 60
MAX_VELOCITY = 127


class Note:

    def __init__(self, pitch=MIDDLE_C, time=0, duration=1, velocity=MAX_VELOCITY, channel=0, chord_note=False):
        """ Constructor for the Note class.

        Args:
            pitch (int, optional): The pitch of the note represented as an integer. Defaults to MIDDLE_C. (60)
            time (int, optional): The absolute time during the song that the note starts. Defaults to 0.
            duration (int, optional): The duration that the note is held. Defaults to 1.
            velocity (int, optional): The intensity/loudness of the note. Defaults to MAX_VELOCITY (127).
            channel (int, optional): The channel this note was read from. Defaults to 0.
            chord_note (bool, optional): If this note is part of a chord
        """        
        self.pitch = pitch
        self.time = time
        self.duration = duration
        self.velocity = velocity
        self.channel = channel
        self.chord_note = chord_note
        # The pitch class the note belongs to, stored as an int from 0-11, with
        # 0 being C. Octave information is lost in this calculation.
        self.c_indexed_pitch_class = pitch % NUM_NOTES

    def duplicate_note(self):
        return Note(pitch=self.pitch, time=self.time, duration=self.duration, velocity=self.velocity,
                    channel=self.channel, chord_note=self.chord_note)


