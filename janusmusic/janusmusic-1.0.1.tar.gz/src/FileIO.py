import sys

import mido
from mido import MidiFile

from Chord import Chord
from Control import Control
from Track import Track
from Note import Note


def read_midi_file(song, filename, print_file=False):
    """Takes a song and file name as input, clears the song data and
    overwrites it with the data from the new file. This creates a list
    of tracks, gets the metadata for the song, and created a "song" object

    Args:
        song (Song): Song object to store the MIDI file's song in
        filename (String): filename of MIDI file
        print_file (bool, optional): Whether or not to print the MIDI file
            after reading it in. Defaults to False.

    Raises:
        NotImplementedError: If a Type 2 MIDI file is read

    Returns:
        song: The Song object containing the song in the MIDI file
    """
    midi = MidiFile(filename)

    if print_file:
        print_midi(filename=filename, file=midi)

    song.clear_song_data()
    song.ticks_per_beat = midi.ticks_per_beat

    # File has multiple synchronous tracks or one track with multiple channels
    if midi.type == 1 or midi.type == 0:

        # For each mido track in the file
        for read_track in midi.tracks:

            # The name of this track
            track_name = None
            # The name of the device this track is played on
            device_name = None
            # A list of tracks to be added to the song (Will only have one element for type 1 and 2 files)
            tracks = []
            # Notes that have had their note_on message read, but don't yet have a note_off message
            current_notes = []
            # The current running time of the song (In absolute terms)
            current_time = 0
            # Keeps track of number of concurrent notes in a track or channel
            num_notes_per_channel = [0] * 16
            # Keeps track of if a chord has been detected already on a channel
            # (prevents the same chord from being counted multiple times)
            found_chord = [False] * 16
            # For each message in the mido track
            for msg in read_track:

                # This is the track currently being modified
                track = None

                # Add the delay between notes to the current time
                current_time += msg.time

                # Set the current track to the track with the same channel as the current message.
                # If this track does not yet exist, create it.
                if hasattr(msg, 'channel'):
                    track = set_current_track_by_channel(msg=msg, tracks=tracks)

                # If this message is a note and not metadata
                if hasattr(msg, 'note') and hasattr(msg, 'velocity'):
                    handle_note(msg=msg, notes=current_notes, time=current_time, track=track,
                                num_notes_per_channel=num_notes_per_channel, found_chord=found_chord)

                if msg.type == 'control_change' or msg.type == 'program_change' or msg.type == 'set_tempo':
                    if msg.type == 'set_tempo':
                        if len(tracks) > 0:
                            track = tracks[0]  # set_tempo applies to the whole song, regardless of what track it's on
                        else:
                            track = Track(channel=0)  # If there are no tracks yet, create a new one
                            tracks.append(track)

                    handle_control(msg=msg, track=track, time=current_time)

                # If this message is a program change, (tells the instrument being played on this track)
                if msg.type == 'program_change':
                    track.instrument = msg.program

                # If this message is a track name
                if msg.type == 'track_name':
                    track_name = msg.name

                # If this message is a track device
                if msg.type == 'device_name':
                    device_name = msg.name

                # In case there are notes left in the "current_notes" list when the song ends
                if msg.type == 'end_of_track':
                    conv_remaining_notes(current_notes=current_notes, current_time=current_time, tracks=tracks)

            # Add this track and its associated notes to the song (sorted by time)
            for t in tracks:
                t.track_name = str(track_name)
                t.device_name = str(device_name)
                t.notes.sort(key=lambda note: note.time)
                t.generate_tags()
                song.add_track(t)
        return song

    # File has multiple asynchronous tracks
    else:
        raise NotImplementedError("'Type 2' Midi files are not supported at this time")


def conv_remaining_notes(current_notes, current_time, tracks):
    """ In the case that a midi song has note_on messages that do not have a closing note_off message, this method
    will end those notes when the end_of_track message is read in for that particular track. This should not occur,
    but adding this method increases the program's robustness and allows us to fix malformed midi files

    Args:
        current_notes (Note[]): An array of notes for which a note_on message was received, but no note_off message was
        current_time (int): Current absolute time in the song
        tracks (Track[]): An array of track objects (generated from the current midi track being read in)
    """
    for n in current_notes:
        n.duration = current_time - n.time
        if n.duration == 0:
            n.duration = 1  # A note can't have zero duration (This breaks the file output)
        current_notes.remove(n)
        track = set_current_track_by_channel(msg=n, tracks=tracks)
        track.add_note(n)


def set_current_track_by_channel(msg, tracks):
    """ Returns the track that is assigned to the same channel as the given message/note. If this track does not
    exist, create a new track and set it to this channel.

    Args:
        msg (Message or Note): A Mido Message object, or a Note object for which the associated track needs to be found
        tracks (Track[]): An array of possible tracks that could match the channel of the message or note
    """
    track = None
    for t in tracks:
        if t.channel == msg.channel:
            track = t
    if track is None:
        track = Track(channel=msg.channel)
        tracks.append(track)
    return track


def write_midi_file(song, filename, print_file=False):
    """ Takes a file name and a song as input, recreates a midi file
    using the tracks and metadata included in the song object, and
    exports it to a file with the given name

    Args:
        song (Song): Song object containing the song to be output
        filename (String): Name of the file to write to
        print_file (bool, optional): Whether or not to print the midi
            file. Defaults to False.
    """
    # Generate new type 1 midi file with the original song's metadata
    midi = MidiFile(type=1)
    midi.ticks_per_beat = song.ticks_per_beat

    # For each track in the song
    for i, t in enumerate(song.tracks):
        # Get an ordered list of messages
        msgs = order_messages(t)
        # Create a new midi track and add these messages to the track
        midi.add_track(name=None)

        # Set the name, device, and instrument for the new track
        name_msg = mido.MetaMessage(type='track_name', name=str(t.track_name), time=0)
        midi.tracks[i].append(name_msg)
        device_msg = mido.MetaMessage(type='device_name', name=str(t.device_name), time=0)
        midi.tracks[i].append(device_msg)

        for m in msgs:
            midi.tracks[i].append(m)

        # TODO: This change is temporary for instrument change
        # midi.tracks[i].append(mido.Message(type='program_change', channel=0, program=46, time=0))
        # Add an End of Track message. Time is 500 to allow a small buffer zone from the last note
        eot_msg = mido.MetaMessage(type='end_of_track', time=500)
        midi.tracks[i].append(eot_msg)

    # midi.tracks[0].append(mido.Message(type='program_change', channel=0, program=46, time=0))
    # Save this midi file
    midi.save(filename)

    if print_file:
        print_midi(filename, midi)


def order_messages(track):
    """ Takes a track as input and returns an ordered list of midi messages.
    These messages consist of note_on, note_off, and control messages, and will have
    their attributes (channel, pitch, velocity, time, etc) set correctly based
    on the values stored in each note or control object.

    Args:
        track (Track): Track to order the messages of

    Returns:
        String[]: Array of all messages in order
    """
    note_on = []
    note_off = []
    controls = []
    msgs = []
    time = 0

    track.notes.sort(key=lambda x: x.time)

    # Generate three lists (control messages, note_on and note_off) that store the absolute
    # times when each midi event occurs. These lists consist of tuples,
    # [message, int] that stores a message and it's corresponding time (either
    # starting or ending time in the case of notes)
    for n in track.notes:
        note_on.append([n, n.time])
        note_off.append([n, n.time + n.duration])

    for c in track.controls:
        controls.append([c, c.time])

    # Sort note on and off messages so they're in chronological order
    note_on.sort(key=lambda note: note[1])
    note_off.sort(key=lambda note: note[1])
    controls.sort(key=lambda control: control[1])

    # Compare the first element of the three lists. Write which ever one comes
    # first to a midi message, and remove it from its list.
    while len(note_on) > 0 or len(note_off) > 0 or len(controls) > 0:
        # print("on " + str(len(note_on)) + " off " + str(len(note_off)) + " ctrl " + str(len(controls)))
        if len(note_on) > 0:
            next_note_on = note_on[0][0]
            next_note_on_time = note_on[0][1]
        else:
            next_note_on = None
            next_note_on_time = None

        if len(note_off) > 0:
            next_note_off = note_off[0][0]
            next_note_off_time = note_off[0][1]
        else:
            next_note_off = None
            next_note_off_time = None

        if len(controls) > 0:
            next_control = controls[0][0]
            next_control_time = controls[0][1]
        else:
            next_control = None
            next_control_time = None

        # If the next event is a control change
        if next_control_time is not None and \
                (next_note_off_time is None or next_control_time <= next_note_off_time) and \
                (next_note_on_time is None or next_control_time <= next_note_on_time):

            c = next_control
            msg_time = c.time
            msg_type = 'control'

            if c.msg_type == 'set_tempo':
                msgs.append(mido.MetaMessage(type=c.msg_type, tempo=c.tempo,
                                             time=msg_time - time))
            elif c.msg_type == 'control_change':
                msgs.append(mido.Message(type=c.msg_type, channel=track.channel, control=c.control, value=c.value,
                                         time=msg_time - time))
            else:  # implies this message is a program change
                msgs.append(mido.Message(type=c.msg_type, channel=track.channel, program=c.instrument,
                                         time=msg_time - time))

            controls.remove(controls[0])

        # If the next event is a note_on event
        elif len(note_on) > 0 and next_note_on_time < next_note_off_time:
            n = next_note_on
            msg_type = 'note_on'
            msg_time = next_note_on_time
            note_on.remove(note_on[0])
            msgs.append(mido.Message(type=msg_type, channel=track.channel, note=n.pitch, velocity=n.velocity,
                                     time=msg_time - time))

        # If the next event is a note_off event
        else:
            n = next_note_off
            msg_type = 'note_off'
            msg_time = next_note_off_time
            note_off.remove(note_off[0])
            msgs.append(mido.Message(type=msg_type, channel=track.channel, note=n.pitch, velocity=n.velocity,
                                     time=msg_time - time))

        time = msg_time

    return msgs


def handle_note(msg, notes, time, track, num_notes_per_channel, found_chord):
    """ Handles the case where a note message is read in from a midi file
    If this is a note_on message, create a new Note object and store it
    in the notes[] array (for now)
    If this is a note_off message, find the corresponding Note object in
    the notes[] array, set the duration, and add this Note object to the
    track being edited. Remove this note from notes[].

    Args:
        msg (mido.Message): Message being read in
        notes (Note[]): List of notes that have been started but not ended
        time (int): Current timestamp where this note occurs
        track (Track): Track this note will be added to
        num_notes_per_channel (Int[]): An array noting how many notes are currently
            playing on each channel, for chord detection.
        found_chord (Boolean[]): Flags (for each channel) if a chord was found with the current notes
            that are playing to avoid marking duplicates. Resets when a new note starts
    """

    # If this message is the start of a note
    if msg.type == 'note_on' and msg.velocity > 0:
        # Create a new Note object and add it to the array of currently playing notes

        notes.append(Note(pitch=msg.note, time=time, duration=0, velocity=msg.velocity, channel=msg.channel))
        num_notes_per_channel[msg.channel] += 1
        found_chord[msg.channel] = False

    # If this message is the end of a note
    elif msg.type == 'note_off' or msg.velocity == 0:
        # Find a possible chord in this channel first
        if num_notes_per_channel[msg.channel] >= 3 and not found_chord[msg.channel]:
            chord = []
            for n in notes:
                # Add every current playing note to chord object
                if n.channel == msg.channel:
                    chord.append(n)
                    n.chord_note = True
            # Create new chord object and add it to the track list
            track.add_chord(Chord(notes=chord, time=time))
            found_chord[n.channel] = True

        # For each note that is currently playing
        for n in notes:
            # Check if the pitch and channel are the same (locate the correct note)
            if n.pitch == msg.note and n.channel == msg.channel:
                # Set the duration of this note based on current_time - start time, add it to the track
                n.duration = time - n.time
                notes.remove(n)
                num_notes_per_channel[n.channel] -= 1
                track.add_note(n)
                break


def handle_control(msg, track, time):
    """ Handles control messages (control_change/program_change). These
    can occur at any time in a track, but have to be treated slightly
    differently to normal notes

    Args:
        msg (mido.Message or mido.MetaMessage): Message being read in
        track (Track): Track being modified
        time (int): Current time into the song this message appears

    Raises:
        AttributeError: If time is None
        AttributeError: If msg is None
        AttributeError: If track is None
        TypeError: If message type is not control, program, or tempo
    """

    if time is None:
        raise AttributeError("Time cannot be None")
    if msg is None:
        raise AttributeError("msg cannot be None")
    if track is None:
        raise AttributeError("Track cannot be None")

    if msg.type == 'control_change':
        control = Control(msg_type=msg.type, control=msg.control, value=msg.value, time=time)
    elif msg.type == 'program_change':
        control = Control(msg_type=msg.type, instrument=msg.program, time=time)
    elif msg.type == 'set_tempo':
        control = Control(msg_type=msg.type, tempo=msg.tempo, time=time)
    else:
        raise TypeError("message " + str(msg) + "is not a valid control message")

    track.controls.append(control)


def print_midi(filename='output.txt', file=None):
    """ Prints a MIDI file in a readable format to standard output.
    Mainly used for debugging.

    Args:
        filename (str, optional): Name of file to write to. Defaults to 'output.txt'.
        file (MidiFile): The MidiFile you wish to print (mido object). Defaults to None.
    """
    original_stdout = sys.stdout  # Save a reference to the original standard output

    with open(filename + '.txt', 'w') as f:
        sys.stdout = f  # Change the standard output to the file we created.
        print(file)
    sys.stdout = original_stdout  # Reset the standard output to its original value
