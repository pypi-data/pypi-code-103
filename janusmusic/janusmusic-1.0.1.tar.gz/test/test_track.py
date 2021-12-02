import pytest

from Control import Control
from Note import Note
from Track import Track, TagEnum


def test_track():
    notes_in = [Note(pitch=60, time=100, duration=100, velocity=100, channel=0, chord_note=False),
                Note(pitch=61, time=200, duration=100, velocity=100, channel=0, chord_note=False),
                Note(pitch=62, time=300, duration=100, velocity=100, channel=0, chord_note=False),
                Note(pitch=63, time=400, duration=100, velocity=100, channel=0, chord_note=False)]

    notes_in2 = [Note(pitch=60, time=100, duration=100, velocity=100, channel=0, chord_note=False),
                 Note(pitch=61, time=200, duration=100, velocity=100, channel=0, chord_note=False),
                 Note(pitch=62, time=300, duration=100, velocity=100, channel=0, chord_note=False),
                 Note(pitch=63, time=400, duration=100, velocity=100, channel=0, chord_note=False)]

    controls_in = [Control(msg_type='control_change', control=3, value=10, time=100),
                   Control(msg_type='program_change', instrument=20, time=200)]

    controls_in2 = [Control(msg_type='control_change', control=3, value=10, time=100),
                    Control(msg_type='program_change', instrument=20, time=200)]

    track = Track(notes=notes_in, controls=controls_in, track_name="test_track_1", device_name="test_device_1",
                  channel=0)

    track2 = Track(notes=notes_in2, controls=controls_in2, track_name="test_track_2", device_name="test_device_2",
                   channel=0)

    notes_expected = [Note(pitch=60, time=100, duration=100, velocity=100, channel=0, chord_note=False),
                      Note(pitch=61, time=200, duration=100, velocity=100, channel=0, chord_note=False),
                      Note(pitch=62, time=300, duration=100, velocity=100, channel=0, chord_note=False),
                      Note(pitch=63, time=400, duration=100, velocity=100, channel=0, chord_note=False),
                      Note(pitch=60, time=600, duration=100, velocity=100, channel=0, chord_note=False),
                      Note(pitch=61, time=700, duration=100, velocity=100, channel=0, chord_note=False),
                      Note(pitch=62, time=800, duration=100, velocity=100, channel=0, chord_note=False),
                      Note(pitch=63, time=900, duration=100, velocity=100, channel=0, chord_note=False)]

    controls_expected = [Control(msg_type='control_change', control=3, value=10, time=100),
                         Control(msg_type='program_change', instrument=20, time=200),
                         Control(msg_type='control_change', control=3, value=10, time=600),
                         Control(msg_type='program_change', instrument=20, time=700)]

    track_expected = Track(notes=notes_expected, controls=controls_expected, track_name="test_track_1",
                           device_name="test_device_1", channel=0)

    assert track.get_c_indexed_note_frequencies() == [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]

    track.generate_tags()
    assert track.tag == TagEnum.MELODY

    track_actual = track.append_track(track=track2)

    assert track_actual.equals(track_expected)



