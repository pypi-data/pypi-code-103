import logging
from logging import info
from Track import Track, TagEnum
from Key import Key, KEYS
from Scale import SCALE_TYPES
from Note import NUM_NOTES
import FileIO as FileIO

import matplotlib.pyplot as plt
import collections
import graphviz

DEFAULT_TICKS_PER_BEAT = 48


class SongLibrary:
    GARTH_BROOKS_TO_MAKE_YOU_FEEL_MY_LOVE = "../../MIDI Files/Country/Garth Brooks/26553_To-Make-You-Feel-My-Love.mid"
    JOHN_ANDERSON_I_WISH_I_COULD_HAVE_BEEN_THERE = "../../MIDI Files/Country/John Anderson/2601_I-Wish-I-Could-Have-Been-There.mid"
    TIM_MCGRAW_SOMETHING_LIKE_THAT = "../../MIDI Files/Country/Tim McGraw/2610_Something-Like-That.mid"
    AMAZING_GRACE = "../../MIDI Files/Gospel/John Newton/Amazing_Grace.mid"
    NIRVANA_LITHIUM = "../../MIDI Files/Grunge/Nirvana/Lithium.mid"
    PEARL_JAM_BETTER_MAN = "../../MIDI Files/Grunge/Pearl Jam/BetterMan.mid"
    SOUNDGARDEN_BLACK_HOLE_SUN = "../../MIDI Files/Grunge/Soundgarden/BlackHoleSun.mid"
    STONE_TEMPLE_PILOTS_CREEP = "../../MIDI Files/Grunge/Stone Temple Pilots/Creep.mid"
    SIMON_AND_GARFUNKEL_SCARBOROUGH_FAIR = "../../MIDI Files/Indie/Simon and Garfunkel/scarborough_fair.mid"
    SIMON_AND_GARFUNKEL_SOUND_OF_SILENCE = "../../MIDI Files/Indie/Simon and Garfunkel/Sound_Of_Silence.mid"
    FRANK_SINATRA_MY_WAY = "../../MIDI Files/Jazz/Frank Sinatra/my_way.mid"
    BLACK_SABBATH_IRON_MAN = "../../MIDI Files/Metal/Black Sabbath/Black Sabbath-Iron Man.mid"
    JUDAS_PRIEST_NIGHT_CRAWLER = "../../MIDI Files/Metal/Judas Priest/Judas Priest - Night Crawler.mid"
    MEGADETH_SYMPHONY_OF_DESTRUCTION = "../../MIDI Files/Metal/Megadeth/Megadeth-Symphony Of Destruction.mid"
    METALLICA_ENTER_SANDMAN = "../../MIDI Files/Metal/Metallica/EnterSandman.mid"
    ADELE_SKYFALL = "../../MIDI Files/Pop/Adele/Adele_-_Skyfall.mid"
    BILLIE_EILISH_NO_TIME_TO_DIE = "../../MIDI Files/Pop/Billie Eilish/Billie Eilish - No Time To Die (James Bond) (midi by Carlo Prato) (www.mid"
    BRUNO_MARS_THE_LAZY_SONG = "../../MIDI Files/Pop/Bruno Mars/Thelazysong.mid"
    ED_SHEERAN_SHAPE_OF_YOU = "../../MIDI Files/Pop/Ed Sheeran/Ed Sheeran - Shape of You  (midi by Carlo Prato) (www.cprato.com).mid"
    IMAGINE_DRAGONS_RADIOACTIVE = "../../MIDI Files/Pop/Imagine Dragons/Radioactive.mid"
    THE_CHAINSMOKERS_FT_HALSEY_CLOSER = "../../MIDI Files/Pop/The Chainsmokers/The Chainsmokers ft. Halsey - Closer  (midi by Carlo Prato) (www.cprato.com).mid"
    THE_WEEKND_PARTY_MONSTER = "../../MIDI Files/Pop/The Weeknd/The Weeknd - Party Monster  (midi by Carlo Prato) (www.cprato.com).mid"
    AEROSMITH_DREAM_ON = "../../MIDI Files/Rock/Aerosmith/DreamOn.mid"
    EAGLES_HOTEL_CALIFORNIA = "../../MIDI Files/Rock/Eagles/HotelCalifornia.mid"
    ELTON_JOHN_ROCKET_MAN = "../../MIDI Files/Rock/Elton John/RocketMan.mid"
    FALL_OUT_BOY_LIGHT_EM_UP = "../../MIDI Files/Rock/Fall Out Boy/LightEmUp.mid"
    GREENDAY_BOULEVARD_OF_BROKEN_DREAMS = "../../MIDI Files/Rock/Greenday/BoulevardofBrokenDreams.mid"
    ROLLING_STONES_SATISFACTION = "../../MIDI Files/Rock/Rolling Stones/Satisfaction.mid"


# Stores metadata about a song, and the tracks included in the song
# <jmleeder>
class Song:

    def __init__(self, tracks=None, ticks_per_beat=DEFAULT_TICKS_PER_BEAT, key=None):
        """ Constructor for the Song class.

        Args:
            tracks (Track[], optional): List of Tracks that make up the song. Defaults to None.
            ticks_per_beat (int, optional): The amount of ticks that pass within one beat in the 
                song. Defaults to DEFAULT_TICKS_PER_BEAT (48).

        Raises:
            ValueError: For a negative ticks_per_beat value
        """
        if tracks is None:
            tracks = []
        self.tracks = tracks
        if ticks_per_beat >= 0:
            self.ticks_per_beat = ticks_per_beat
        else:
            raise ValueError
        if isinstance(key, Key):
            self.key = key
        else:
            self.key = None

    def add_track(self, t):
        """ Adds a new track to the song.

        Args:
            t (Track): Track to add to the song
        """
        assert isinstance(t, Track)
        self.tracks.append(t)

    @staticmethod
    def get_notes_array():
        """ TODO: ?

        Returns:
            String[]: List of each key possible represented as strings.
        """
        return KEYS

    def save(self, filename, print_file=False):
        """ Saves a song object to a midi file with the given name

        Args:
            filename (String): Name of file to save the song as
            print_file (bool, optional): Whether or not to print out the song. Mainly 
                used for debugging purposes. Defaults to False.
        """
        FileIO.write_midi_file(self, filename=filename, print_file=print_file)

    def load(self, filename, print_file=False):
        """ Loads a file into this song object. The new data overwrites any previous
        data stored in this song.

        Args:
            filename (String): Name of the file to load in
            print_file (bool, optional): Whether or not to print out the song. Mainly 
                used for debugging purposes. Defaults to False.
        """
        FileIO.read_midi_file(self, filename=filename, print_file=print_file)
        self.detect_key_and_scale()
        self.get_chord_names()

    def clear_song_data(self):
        """ Deletes all of the data from this song object and resets its default values
        """
        self.tracks = []
        self.ticks_per_beat = DEFAULT_TICKS_PER_BEAT

    def get_c_indexed_note_frequencies(self):
        """ Returns an array containing how many times each of the 12 notes appears in this 
        song, starting with C.

        Returns:
            int[]: note frequencies array
        """
        c_indexed_note_frequency = [0] * 12
        for track in self.tracks:
            if not track.is_percussion:
                track_frequencies = track.get_c_indexed_note_frequencies()
                for idx, val in enumerate(track_frequencies):
                    c_indexed_note_frequency[idx] += val
        return c_indexed_note_frequency

    def get_note_frequencies(self, key):
        """ Returns an array containing how many times each of the 12 notes appears in this 
        song, starting with key.

        Args:
            key (Key): Key to start the array with

        Returns:
            int[]: note frequencies array
        """
        indexed_note_frequency = [0] * 12
        for track in self.tracks:
            if not track.is_percussion:
                track_frequencies = track.get_note_frequencies(key)
                for idx, val in enumerate(track_frequencies):
                    indexed_note_frequency[idx] += val
            return indexed_note_frequency

    def get_tracks_by_tag(self, tag: TagEnum):
        """
        Returns an array of tracks in the song that have the given tag attached
        :param tag: the tag enum that will be searched for
        :return: An array of tracks that match the given tag enum
        """
        tracks = []
        for track in self.tracks:
            if track.tag == tag:
                tracks.append(track)
        return tracks

    def change_song_key_by_half_steps(self, num_half_steps):
        """ Shifts all notes in the song up the by num_half_steps half steps.
        If num_half_steps is negative, the notes will be shifted down instead
        of up.

        Args:
            num_half_steps (int): Number of half steps to move the notes in the song by

        Returns:
            Song: The newly edited song.
        """
        for track in self.tracks:
            if not track.is_percussion:
                for note in track.notes:
                    note.pitch += num_half_steps

        self.get_chord_names()
        return self

    def change_song_key(self, origin_key, destination_key, interval_begin=0, interval_end=float('inf')):
        """ Changes the key of a song for a certain time interval during it.
        TODO: this will not need origin_key once key detection is fully implemented

        Args:
            origin_key (Key): Current key of the song
            destination_key (Key): Key to change the song to
            interval_begin (int): Absolute time during the song to start the key change
            interval_end (int): Absolute time during the song to end the key change

        Raises:
            SyntaxError: If origin_key or destination_key is not a valid Key

        Returns:
            Song: the newly edited song
        """

        # Check to make sure params are the correct type
        if not isinstance(origin_key, Key) or not isinstance(destination_key, Key):
            raise SyntaxError("Parameters are not of the right type.  They must be of type 'Key'")

        # Get the index of the origin key
        origin_index = origin_key.get_c_based_index_of_key()

        # Get the index of the destination key
        destination_index = destination_key.get_c_based_index_of_key()

        # discover offset (this is the number of half steps to move each note to get to the destination key)
        offset = destination_index - origin_index

        origin_steps = []
        dest_steps = []

        # iterate over each scale and find the source and destination scales
        for scale in SCALE_TYPES.items():
            # Break the scale dict into source and destination values
            if scale[0] == str(origin_key.mode):
                origin_steps = scale[1]
            if scale[0] == str(destination_key.mode):
                dest_steps = scale[1]

        # apply the offset to each note within the time interval
        for track in self.tracks:
            if not track.is_percussion:
                for note in track.notes:
                    if interval_begin <= note.time <= interval_end:
                        note.pitch += offset

                        # Reset c_indexed_pitch_class
                        note.c_indexed_pitch_class = note.pitch % 12

                        # Shift each note to its corresponding location in the destination mode
                        origin_pitch = 0
                        dest_pitch = 0
                        for i in range(len(origin_steps)):

                            if (note.c_indexed_pitch_class - origin_key.get_c_based_index_of_key()) % 12 == origin_pitch:
                                note.pitch += (dest_pitch - origin_pitch)
                            # Deal with accidentals here? or leave them where they are?
                            origin_pitch += origin_steps[i]
                            dest_pitch += dest_steps[i]
        return self

    def get_note_velocity_graph(self, name):
        """ Shows a graph of the velocity (intensity/loudness) of all the notes in this song.
        TODO: make this return rather than 'print'
        """
        all_velocity = []
        all_time = []
        for track in self.tracks:
            for note in track.notes:
                all_velocity.append(note.velocity)
                all_time.append(note.time)

        plt.plot(all_time, all_velocity)
        plt.xlabel("Time")
        plt.ylabel("Velocity")
        # Change this to show title of song when that variable is available
        plt.title("Velocity of Notes in " + name)
        plt.show()

    def get_bar_graph(self, title, x_label, y_label, items):
        counter = collections.Counter(items)
        counter = dict(sorted(counter.items(), key=lambda item: item[1], reverse=True))
        bar = plt.bar(x=counter.keys(), height=counter.values())
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        # Change this to show title of song when that variable is available
        plt.title(title)
        return bar

    # Shows a graph of the frequency of all the notes in this song
    def get_note_frequency_graph(self, name):
        """ Shows a graph of the frequency that each note apperas in this song.
        TODO: make this return rather than 'print'
        """
        all_notes = []
        for track in self.tracks:
            for note in track.notes:
                all_notes.append(KEYS[note.pitch % 12])

        graph = self.get_bar_graph("Frequency of Notes in " + name, "Note", "Frequency", all_notes)
        plt.show()

    def to_string(self):
        """ Returns the contents of the song as a string in the format: \n
        Song metadata       \n
        Track1 metadata     \n
        notes               \n
        ...V...             \n
        control messages    \n
        ...V...             \n
        Track 2 metadata    \n
        notes               \n
        ...V...             \n
        etc

        Note: The notes and control messages are listed separately, they are not sorted together by time.
        """
        message = ""
        message += ("Ticks per beat: " + str(self.ticks_per_beat) + "\n")
        for t in self.tracks:
            message += ("  Track name: " + str(t.track_name) + "\n")
            message += ("  Device name: " + str(t.device_name) + "\n")
            for n in t.notes:
                message += ("  Pitch:" + str(n.pitch) + " Velocity: " + str(n.velocity) + " Time: " + str(n.time) +
                            " Duration: " + str(n.duration) + " Channel: " + str(n.channel) + "\n")
            for c in t.controls:
                message += (
                        "  Type: " + str(c.msg_type) + " Tempo: " + str(c.tempo) + " Control: " + str(c.control) +
                        " Value: " + str(c.value) + " Instrument: " + str(c.instrument) + " Time: " + str(c.time) +
                        "\n")
        return message

    def equals(self, song):
        """ Determines whether this song and the specified song are equivalent.

        Args:
            song (Song): Song to check this song against

        Returns:
            bool: True if the songs are equivalent, false otherwise
        """

        if self.ticks_per_beat != song.ticks_per_beat:
            logging.info(msg="These songs have different ticks_per_beat values")
            logging.info(msg="This: " + str(self.ticks_per_beat) + ", compare to: " + str(song.ticks_per_beat))
            return False

        if len(self.tracks) != len(song.tracks):
            logging.info(msg="These songs have a different number of tracks")
            logging.info(msg="This: " + str(len(self.tracks)) + ", compare to: " + str(len(song.tracks)))
            return False

        for i, track in enumerate(self.tracks):
            if not track.equals(song.tracks[i]):
                return False

        return True

    def generate_possible_keys_and_scales(self):
        """ 
        Detect the key of a song using Mr. Dehaan's algorithm.  This algorithm generates the valid notes
        for every key and for every scale and checks the occurrences of the notes in the song against the valid
        key/scale notes.  It then finds how many errors (or misses) occurred.  It then finds the key/scale with the
        lowest number of errors (or the list of key/scale with the same minimum) and returns the result.
        :return: A list of Key objects that have the minimum number of errors [0], and the minimum errors [1]
        """

        note_frequencies = self.get_c_indexed_note_frequencies()

        key_and_scale_error_record = {}

        # Iterate over each key
        for key in KEYS:
            # we have to rotate the frequency array to be 0 indexed at the key.
            # get the index of the key we want the frequencies indexed by
            key_index = Key(key).get_c_based_index_of_key()

            # rotate the array left based on the index to have the 0th index contain the frequency of the tonic or key
            key_indexed_note_frequencies = note_frequencies[key_index:] + note_frequencies[:key_index]

            # iterate over each scale and count errors for each
            for scale in SCALE_TYPES.items():

                # Break the scale dict into key and value
                scale_name = scale[0]
                scale_steps = scale[1]

                # keep an error counter to increment each time a note is not in the key/scale
                errors = 0

                # generate an array with true in the indexes that are in the key/scale and false in the
                # indexes that are notes that are out of the scale  (the array is key indexed at 0)
                accepted_notes = [False] * NUM_NOTES

                # semitones that a note in the scale is away from the key (starts at 0 because regardless of scale the
                # tonic will be in the scale)
                semitones_from_key = 0
                accepted_notes[0] = True

                # iterate through the scale semitones marking notes as valid for the key/scale
                for semitones in scale_steps:
                    semitones_from_key += semitones
                    # % number of notes (12) because some signatures will count semitones back to tonic
                    accepted_notes[semitones_from_key % NUM_NOTES] = True

                # count all of the errors that occur (notes in the song that are not accepted by key/scale)
                for idx in range(NUM_NOTES):
                    if not accepted_notes[idx]:
                        errors += key_indexed_note_frequencies[idx]

                # store errors in a record dictionary
                key_and_scale_error_record[key + ' ' + scale_name] = errors

        # find the key/scales with the minimum values in the error dictionary
        minimum_errors = min(key_and_scale_error_record.values())
        result = [k for k, v in key_and_scale_error_record.items() if v == minimum_errors]

        keys = []
        for key in result:
            keys.append(Key(key.split()[0], key.split()[1]))

        return keys, minimum_errors

    def detect_key_and_scale(self):
        """
        Uses the generate possible keys and scales method to get a list of potential keys, determines which is
        the most likely based on the most common notes in the song.

        :return: The detected key [0], the minimum errors [1], and the confidence level [2]
        """

        note_frequencies = self.get_c_indexed_note_frequencies()
        num_notes = sum(note_frequencies)
        keys, minimum_errors = self.generate_possible_keys_and_scales()


        # now we have the relative major and minors, we can use the note frequencies to differentiate
        # between the two based on the assumption that for most cases the tonic will be played more than
        # other notes.  This lets us differentiate scales with the same notes such as D major and B Minor.

        # get the resulting keys/scales
        relative_major_key_scale = None
        relative_minor_key_scale = None
        for key in keys:
            if key.mode == "major":
                relative_major_key_scale = key
            elif key.mode == "minor":
                relative_minor_key_scale = key

        # get the index of the key in order to find its frequency in the frequency array
        idx_of_major_key = relative_major_key_scale.get_c_based_index_of_key()
        idx_of_minor_key = relative_minor_key_scale.get_c_based_index_of_key()

        # get the frequency of each tonic
        major_frequency = note_frequencies[idx_of_major_key]
        minor_frequency = note_frequencies[idx_of_minor_key]

        # compare and return the most common key scale
        if major_frequency >= minor_frequency:
            detected_return_key = relative_major_key_scale
        else:
            detected_return_key = relative_minor_key_scale

        # determine confidence based on number of 1 - number of errors/ number of notes
        confidence = 0
        if num_notes != 0:
            confidence = 1 - minimum_errors / num_notes

        # set the key of the song
        self.key = detected_return_key

        # return the tuple
        return detected_return_key, minimum_errors, confidence

    def detect_key_by_phrase_endings(self):
        """
        Takes the song object and looks at the notes in the melody and bass tracks, and finds the notes with the longest
        pauses after them (likely the ends of melodic phrases). These notes are narrowed down until the set number of
        notes (as a percentage) are found.
        :return: Three objects in the format [key: Key, message: String, confidence: String]. The message contains
        lots of diagnostic information that explains what's going on behind the scenes, and shows a confidence value.
        Note: If the detected tonic is not a note in the detected scale,
        """
        TIME_INTERVAL_INCREASE = 20
        PERCENTAGE_TO_FIND = 0.01

        total_song_notes = 0
        time_interval = 0
        detected_tonic = ""
        message = ""
        confidence = ""

        for track in self.tracks:
            total_song_notes += len(track.notes)

        total_found_notes = total_song_notes
        # total_found_notes = 0

        # Until you find less than the percentage in PERCENTAGE_TO_FIND
        while total_found_notes > PERCENTAGE_TO_FIND * total_song_notes and total_found_notes > len(self.tracks):

            total_found_notes = 0
            time_interval += TIME_INTERVAL_INCREASE

            c_indexed_total_note_frequency = [0] * NUM_NOTES
            for track in self.tracks:
                if track.tag == TagEnum.MELODY or track.tag == TagEnum.BASS:
                    c_indexed_track_note_frequency = [0] * NUM_NOTES
                    for idx, note in enumerate(track.notes):
                        if idx != len(track.notes):
                            # If this note is the last note of the song, or has a long pause after

                            # if idx == len(track.notes) - 1 \
                            #         or (track.notes[idx].time + track.notes[idx].duration) % \
                            #         (4 * self.ticks_per_beat) < time_interval:
                            if idx == len(track.notes) - 1 or track.notes[idx+1].time - note.time > time_interval:

                                total_found_notes += 1
                                c_indexed_track_note_frequency[note.c_indexed_pitch_class] += 1
                                # print(track.track_name + " time: " + str(track.notes[idx-1].time) + " pitch: " +
                                #       str(track.notes[idx-1].c_indexed_pitch_class) + " ch: " + str(track.channel))
                            # if idx == len(track.notes) - 1:
                                # print("Last note: " + str(note.c_indexed_pitch_class))
                    message += (str(c_indexed_track_note_frequency) + ": " + str(track.tag) + " - " +
                                str(track.track_name) + "\n")
                    for i in range(12):
                        c_indexed_total_note_frequency[i] += c_indexed_track_note_frequency[i]

            message += (str(c_indexed_total_note_frequency) + ": totals"  + "\n")

            max_val = 0
            max_idx = -1
            for i in range(len(c_indexed_total_note_frequency)):
                if max_val < c_indexed_total_note_frequency[i]:
                    max_val = c_indexed_total_note_frequency[i]
                    max_idx = i

            if total_found_notes == 0:
                confidence = 0
            else:
                confidence = str(c_indexed_total_note_frequency[max_idx] / total_found_notes)

            message += ("Detected key: " + KEYS[max_idx] + "\n")
            message += ("Time interval: " + str(time_interval) + "\n")
            message += ("Found notes: " + str(total_found_notes) + "\n")
            message += ("Confidence: " + confidence + "\n")
            message += ("ticks per beat: " + str(self.ticks_per_beat) + "\n\n")

            # The detected tonic of the song (NOT a Key object yet)
            detected_tonic = KEYS[max_idx]

        # Convert detected_key into a Key object with the correct scale
        possible_keys = self.generate_possible_keys_and_scales()[0]
        detected_key = None
        for key in possible_keys:
            if key.tonic == detected_tonic:
                detected_key = key

        # If the detected tonic is not in the list of possible keys, choose the major mode of the detected scale.
        if detected_key is None:
            for key in possible_keys:
                if key.mode == 'major':
                    detected_key = key

        # set the key of the song
        self.key = detected_key

        return [detected_key, message, confidence]

    def get_chord_names(self):
        """
        Sets the name field inside chord based on the notes in the chord.
        """
        # It would be helpful for us here to have an accidental field on a key to know if its sharp or flat
        # That's because then you know whether to use the keys or equivalent keys array
        # I think this should work for all natural keys though
        # This also doesn't account for diminished chords
        major = [1, 4, 5]
        minor = [2, 3, 6]
        # Gets the key of the song, as an integer
        key = self.key.get_c_based_index_of_key()
        # Iterate over every chord in every track
        for track in self.tracks:
            for chord in track.chords:
                # Get the name of the first note in the chord which will
                # commonly be the name of the chord.
                first_note_index = chord.notes[0].c_indexed_pitch_class
                first_note_name = KEYS[chord.notes[0].pitch % NUM_NOTES]
                # The distance between our first note and the key will tell
                # us if its major or minor.
                distance_between_notes = first_note_index - key + 1
                if distance_between_notes in major:
                    if distance_between_notes == 5 and len(chord.notes) == 4:
                        chord.name = first_note_name + " Dominant"
                    else:
                        chord.name = first_note_name + " Major"
                else:
                    chord.name = first_note_name + " Minor"
                if len(chord.notes) == 4:
                    chord.name = chord.name + " Seventh"

    def get_transition_graph(self, name):
        # TODO: Change the way it iterates through tracks so the chords are always connected by the time
        # they occur in the song.
        # Create a directed graph object and set dimensions
        graph = graphviz.Digraph(comment="Chord transitions in Song")
        graph.attr(ranksep='0.01', nodesep='0.1', label=name + " Chord Transitions", labelloc="t")
        chord_set = set()
        edges = []
        all_chords = []
        # Iterate over every track in song
        for track in self.tracks:
            if not track.chords:
                continue
            all_chords += track.chords

        all_chords.sort(key=lambda chord: chord.time)
        # Hold the previous chord
        prev_chord = all_chords[0]
        graph.node(prev_chord.name)
        chord_set.add(prev_chord.name)
        # Iterate over every chord in track
        for i in range(1, len(all_chords)):
            curr = all_chords[i]
            # Only add chords that are not already on graph
            if curr.name not in chord_set:
                graph.node(curr.name)
                chord_set.add(curr.name)
            edges.append([prev_chord.name, curr.name])
            print(prev_chord.name + " -> " + curr.name)
            prev_chord = curr

        counter = collections.Counter(tuple(edge) for edge in edges)
        for edge, count in counter.items():
            # print(str(edge[0]), count)
            graph.edge(str(edge[0]), str(edge[1]), label=str(count))
        graph.view()

    def get_notes_at_time(self, time):
        """ Returns all the notes in a song that are playing at a given time

        Args:
            time (int): Time to check

        Returns:
            Note[]: array of notes that occur at the given time
        """        
        notes = []
        for track in self.tracks:
            for note in track.notes:
                if note.time >= time and note.time + note.duration <= time:
                    notes.append(note)

        return notes
