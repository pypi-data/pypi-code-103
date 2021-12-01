import mido
import pytest

import FileIO as FileIO
from Control import Control
from Note import Note
from Song import Song
from Track import Track


def test_read_write_midi_file():
    """
    Test FileIO read_midi_file() and write_midi_file() methods
    These are called from the song.load() and song.save() methods
    """

    type_0_orig = Song()
    type_1_orig = Song()
    # type_2_orig = Song()
    type_0_new = Song()
    type_1_new = Song()
    # type_2_new = Song()

    type_0_orig.load(filename="Resources/My-Name-Is.mid")
    type_1_orig.load(filename="Resources/GoodRiddance(TimeOfYourLife).mid")
    # type_2_orig.load(filename="Resources/")

    type_0_orig.save(filename="Resources/My-Name-Is_Output.mid", print_file=True)
    type_1_orig.save(filename="Resources/GoodRiddance(TimeOfYourLife)_Output.mid", print_file=True)

    type_0_new.load(filename="Resources/My-Name-Is_Output.mid")
    type_1_new.load(filename="Resources/GoodRiddance(TimeOfYourLife)_Output.mid")

    # Check that the two song objects are the same by using the equals method in Song
    assert type_0_orig.equals(type_0_new)
    assert type_1_orig.equals(type_1_new)

    # Check that the original song is what we expect by spot checking some notes
    # and control messages that we expect to see
    assert type_0_orig.tracks[1].notes[0].pitch == 29
    assert type_0_orig.tracks[1].notes[10].pitch == 31
    assert type_0_orig.tracks[1].controls[2].instrument == 33

    assert type_1_orig.tracks[16].notes[0].pitch == 43
    assert type_1_orig.tracks[19].notes[20].pitch == 60
    assert type_1_orig.tracks[16].controls[0].control == 7


def test_order_messages():
    """
    Test FileIO order_messages() method
    """
    track = Track()

    track.channel = 2

    track.notes.append(Note(pitch=100, time=1000, duration=100, velocity=50))
    track.notes.append(Note(pitch=101, time=2000, duration=150, velocity=50))
    track.notes.append(Note(pitch=102, time=2100, duration=100, velocity=50))
    track.notes.append(Note(pitch=103, time=3000, duration=300, velocity=50))
    track.notes.append(Note(pitch=104, time=3100, duration=100, velocity=50))

    track.controls.append(Control(msg_type="program_change", instrument=20, time=2050))

    msgs = FileIO.order_messages(track)

    assert len(msgs) == 11

    assert msgs[0] == mido.Message(type='note_on', channel=2, note=100, velocity=50, time=1000)
    assert msgs[1] == mido.Message(type='note_off', channel=2, note=100, velocity=50, time=100)
    assert msgs[2] == mido.Message(type='note_on', channel=2, note=101, velocity=50, time=900)
    assert msgs[3] == mido.Message(type='program_change', channel=2, program=20, time=50)
    assert msgs[4] == mido.Message(type='note_on', channel=2, note=102, velocity=50, time=50)
    assert msgs[5] == mido.Message(type='note_off', channel=2, note=101, velocity=50, time=50)
    assert msgs[6] == mido.Message(type='note_off', channel=2, note=102, velocity=50, time=50)
    assert msgs[7] == mido.Message(type='note_on', channel=2, note=103, velocity=50, time=800)
    assert msgs[8] == mido.Message(type='note_on', channel=2, note=104, velocity=50, time=100)
    assert msgs[9] == mido.Message(type='note_off', channel=2, note=104, velocity=50, time=100)
    assert msgs[10] == mido.Message(type='note_off', channel=2, note=103, velocity=50, time=100)


def test_handle_note():
    """
        Tests the handle_note() method
    """    
    track = Track()
    current_notes = []
    num_notes_per_channel = [0] * 16
    found_chord = [False] * 16

    note_on_ch0_30 = mido.Message(type='note_on', channel=0, note=30, velocity=100, time=200)
    note_on_ch1_30 = mido.Message(type='note_on', channel=1, note=30, velocity=100, time=200)
    note_on_ch0_40 = mido.Message(type='note_on', channel=0, note=40, velocity=100, time=200)

    note_on_ch0_30_vel0 = mido.Message(type='note_on', channel=0, note=30, velocity=0, time=200)
    note_on_ch1_30_vel0 = mido.Message(type='note_on', channel=1, note=30, velocity=0, time=200)
    note_on_ch0_40_vel0 = mido.Message(type='note_on', channel=0, note=40, velocity=0, time=200)

    note_off_ch0_30 = mido.Message(type='note_off', channel=0, note=30, time=200)
    note_off_ch1_30 = mido.Message(type='note_off', channel=1, note=30, time=200)
    note_off_ch0_40 = mido.Message(type='note_off', channel=0, note=40, time=200)

    # Test two notes starting on the same channel, then ending on the same channel
    FileIO.handle_note(track=track, notes=current_notes, msg=note_on_ch0_30, time=1000,
                       num_notes_per_channel=num_notes_per_channel, found_chord=found_chord)
    FileIO.handle_note(track=track, notes=current_notes, msg=note_on_ch0_40, time=1200,
                       num_notes_per_channel=num_notes_per_channel, found_chord=found_chord)
    assert len(track.notes) == 0
    assert len(current_notes) == 2
    assert num_notes_per_channel[0] == 2

    FileIO.handle_note(track=track, notes=current_notes, msg=note_off_ch0_30, time=1400,
                       num_notes_per_channel=num_notes_per_channel, found_chord=found_chord)
    FileIO.handle_note(track=track, notes=current_notes, msg=note_off_ch0_40, time=1600,
                       num_notes_per_channel=num_notes_per_channel, found_chord=found_chord)
    assert len(track.notes) == 2
    assert len(current_notes) == 0
    assert num_notes_per_channel[0] == 0

    # Same as above, but using note_on_velocity_0 messages instead of note_off messages
    FileIO.handle_note(track=track, notes=current_notes, msg=note_on_ch0_40, time=1800,
                       num_notes_per_channel=num_notes_per_channel, found_chord=found_chord)
    FileIO.handle_note(track=track, notes=current_notes, msg=note_on_ch0_30, time=2000,
                       num_notes_per_channel=num_notes_per_channel, found_chord=found_chord)
    assert len(track.notes) == 2
    assert len(current_notes) == 2
    assert num_notes_per_channel[0] == 2

    FileIO.handle_note(track=track, notes=current_notes, msg=note_on_ch0_30_vel0, time=2200,
                       num_notes_per_channel=num_notes_per_channel, found_chord=found_chord)
    FileIO.handle_note(track=track, notes=current_notes, msg=note_on_ch0_40_vel0, time=2400,
                       num_notes_per_channel=num_notes_per_channel, found_chord=found_chord)
    assert len(track.notes) == 4
    assert len(current_notes) == 0
    assert num_notes_per_channel[0] == 0

    # Test two of the same notes starting on different channels, then ending on different channels
    FileIO.handle_note(track=track, notes=current_notes, msg=note_on_ch1_30, time=2600,
                       num_notes_per_channel=num_notes_per_channel, found_chord=found_chord)
    FileIO.handle_note(track=track, notes=current_notes, msg=note_on_ch0_30, time=2800,
                       num_notes_per_channel=num_notes_per_channel, found_chord=found_chord)
    assert len(track.notes) == 4
    assert len(current_notes) == 2
    assert num_notes_per_channel[0] == 1
    assert num_notes_per_channel[1] == 1

    FileIO.handle_note(track=track, notes=current_notes, msg=note_off_ch1_30, time=2700,
                       num_notes_per_channel=num_notes_per_channel, found_chord=found_chord)
    FileIO.handle_note(track=track, notes=current_notes, msg=note_off_ch0_30, time=2900,
                       num_notes_per_channel=num_notes_per_channel, found_chord=found_chord)
    assert len(track.notes) == 6
    assert len(current_notes) == 0
    assert num_notes_per_channel[0] == 0
    assert num_notes_per_channel[1] == 0

    assert track.notes[0].time == 1000
    assert track.notes[1].time == 1200
    assert track.notes[2].time == 2000
    assert track.notes[3].time == 1800
    assert track.notes[4].time == 2600
    assert track.notes[5].time == 2800

    assert track.notes[0].duration == 400
    assert track.notes[1].duration == 400
    assert track.notes[2].duration == 200
    assert track.notes[3].duration == 600
    assert track.notes[4].duration == 100
    assert track.notes[5].duration == 100


def test_handle_control():
    """
        Tests the handle_control() method
    """    

    track = Track()

    control_control_all_fields = mido.Message(type='control_change', control=3, value=10)
    control_control_min_fields = mido.Message(type='control_change')
    control_tempo_all_fields = mido.MetaMessage(type='set_tempo', tempo=2000)
    control_tempo_min_fields = mido.MetaMessage(type='set_tempo')
    control_program_all_fields = mido.Message(type='program_change', program=20)
    control_program_min_fields = mido.Message(type='program_change')
    control_invalid_type = mido.MetaMessage(type='time_signature')

    FileIO.handle_control(track=track, msg=control_control_all_fields, time=1000)
    FileIO.handle_control(track=track, msg=control_control_min_fields, time=1000)
    FileIO.handle_control(track=track, msg=control_tempo_all_fields, time=1000)
    FileIO.handle_control(track=track, msg=control_tempo_min_fields, time=1000)
    FileIO.handle_control(track=track, msg=control_program_all_fields, time=1000)
    FileIO.handle_control(track=track, msg=control_program_min_fields, time=1000)

    with pytest.raises(TypeError):
        FileIO.handle_control(track=track, msg=control_invalid_type, time=1000)
    with pytest.raises(AttributeError):
        FileIO.handle_control(track=track, msg=control_tempo_all_fields, time=None)
    with pytest.raises(AttributeError):
        FileIO.handle_control(track=track, msg=None, time=0)
    with pytest.raises(AttributeError):
        FileIO.handle_control(track=None, msg=control_tempo_all_fields, time=0)

    ctrl = track.controls[0]
    assert(ctrl.msg_type == 'control_change' and ctrl.tempo is None and ctrl.control == 3 and ctrl.value == 10
           and ctrl.instrument is None and ctrl.time == 1000)

    ctrl = track.controls[1]
    assert (ctrl.msg_type == 'control_change' and ctrl.tempo is None and ctrl.control == 0 and ctrl.value == 0
            and ctrl.instrument is None and ctrl.time == 1000)

    ctrl = track.controls[2]
    assert (ctrl.msg_type == 'set_tempo' and ctrl.tempo == 2000 and ctrl.control is None and ctrl.value is None
            and ctrl.instrument is None and ctrl.time == 1000)

    ctrl = track.controls[3]
    assert (ctrl.msg_type == 'set_tempo' and ctrl.tempo == 500000 and ctrl.control is None and ctrl.value is None
            and ctrl.instrument is None and ctrl.time == 1000)

    ctrl = track.controls[4]
    assert (ctrl.msg_type == 'program_change' and ctrl.tempo is None and ctrl.control is None and ctrl.value is None
            and ctrl.instrument == 20 and ctrl.time == 1000)

    ctrl = track.controls[5]
    assert (ctrl.msg_type == 'program_change' and ctrl.tempo is None and ctrl.control is None and ctrl.value is None
            and ctrl.instrument == 0 and ctrl.time == 1000)

    assert len(track.controls) == 6
