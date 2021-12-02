from Song import Song
from math import floor
from random import randrange

WHOLE = 1
HALF = WHOLE / 2
QUARTER = HALF / 2
EIGHTH = QUARTER / 2
SIXTEENTH = EIGHTH / 2
THIRTY_SECOND = SIXTEENTH / 2
HALF_TRIPLET = WHOLE / 3
QUARTER_TRIPLET = HALF / 3
EIGHTH_TRIPLET = QUARTER / 3
SIXTEENTH_TRIPLET = EIGHTH / 3
THIRTY_SECOND_TRIPLET = SIXTEENTH / 3
DOTTED_WHOLE = WHOLE + WHOLE / 2
DOTTED_HALF = HALF + HALF / 2
DOTTED_QUARTER = QUARTER + QUARTER / 2
DOTTED_EIGHTH = EIGHTH + EIGHTH / 2
DOTTED_SIXTEENTH = SIXTEENTH + SIXTEENTH/2
DOTTED_THIRTY_SECOND = THIRTY_SECOND + THIRTY_SECOND/2
WHOLE_REST = -WHOLE
HALF_REST = -HALF
QUARTER_REST = -QUARTER
EIGHTH_REST = -EIGHTH
SIXTEENTH_REST = -SIXTEENTH
THIRTY_SECOND_REST = -THIRTY_SECOND


def apply_rhythm_pattern(song=None, track=None, pattern_array=None):
    current_abs_time = track.notes[0].time
    whole_length = floor(song.ticks_per_beat * 4)
    j = 0

    for i, note in enumerate(track.notes):

        pattern_idx = j % len(pattern_array)
        # check for rest
        if pattern_array[pattern_idx] >= 0:
            if i + 1 < len(track.notes):
                next_note_time = track.notes[i + 1].time
            #check for chords
            if note.time != next_note_time:
                note.duration = floor(pattern_array[pattern_idx] * whole_length)
                note.time = floor(current_abs_time)
                current_abs_time += note.duration
                j += 1
            else:
                note.duration = floor(pattern_array[pattern_idx] * whole_length)
                note.time = floor(current_abs_time)
        # Handle rests
        else:
            current_abs_time += -(floor(pattern_array[pattern_idx] * whole_length))
            j += 1
            pattern_idx = j % len(pattern_array)
            if note.time != next_note_time:
                note.duration = floor(pattern_array[pattern_idx] * whole_length)
                note.time = floor(current_abs_time)
                current_abs_time += note.duration
                j += 1
            else:
                note.duration = floor(pattern_array[pattern_idx] * whole_length)
                note.time = floor(current_abs_time)





def humanify_rhythm(song=None, track=None, humanify_percent=0.5):

    max_error = 0.12
    if song is None or track is None or humanify_percent > 1 or humanify_percent < 0:
        raise SyntaxError("Song and track must not be None. and humanify_percent needs to be"
                          "between 0.0 and 1.0")

    max_time_offset = floor(song.ticks_per_beat * max_error * humanify_percent)
    for i, note in enumerate(track.notes):
        #check for chord
        if i + 1 < len(track.notes):
            next_note_time = track.notes[i + 1].time

            new_time_offset = note.time + randrange(-max_time_offset, max_time_offset)
            new_duration_offset = note.duration + randrange(-max_time_offset, max_time_offset, 1)

            if new_time_offset >= 0 and new_duration_offset >= 0:
                note.time = new_time_offset
                note.duration = new_duration_offset

