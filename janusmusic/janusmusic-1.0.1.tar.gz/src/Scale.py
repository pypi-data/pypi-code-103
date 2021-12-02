"""
    These array values are semitone differences from the previous note. This is formatted this way because
    notes in the scale change based on the tonic.

    If this is confusing here is an example:

    For the Major scale, the notes in the scale include the tonic (or Key).
    Then, how you know what other notes are in the scale you need to make hops of a specified amount of semitones
    (half steps [1], whole steps [2], minor third [3], etc.) away from the previous note in the scale. So,
    C Major is defined as C (tonic), D (a whole step away from previous), E (a whole steep away from D),
    F (only a half step away from E) and so on...
"""

SCALE_TYPES = dict(
    major=[2, 2, 1, 2, 2, 2, 1],
    dorian=[2, 1, 2, 2, 2, 1, 2],
    phrygian=[1, 2, 2, 2, 1, 2, 2],
    lydian=[2, 2, 2, 1, 2, 2, 1],
    mixolydian=[2, 2, 1, 2, 2, 1, 2],
    minor=[2, 1, 2, 2, 1, 2, 2],
    locrian=[1, 2, 2, 1, 2, 2, 2],
)

"""
    other potential scales/modes that may be useful later
    
    pentatonic=[2, 2, 3, 2],
    pentatonic_minor=[3, 2, 2, 3],
    blues=[3, 2, 1, 1, 3, 2],
    dorian=[2, 1, 2, 2, 2, 1, 2],
    phrygian=[1, 2, 2, 2, 1, 2, 2],
    lydian=[2, 2, 2, 1, 2, 2, 1],
    mixolydian=[2, 2, 1, 2, 2, 1, 2],
    aeolian=[2, 1, 2, 2, 1, 2, 2],
    locrian=[1, 2, 2, 1, 2, 2, 2],
    harmonic_major=[2, 2, 1, 2, 1, 3, 1],
    harmonic_minor=[2, 1, 2, 2, 1, 3, 1],
    super_locrian=[1, 2, 1, 2, 2, 2, 2],
    japanese=[1, 4, 2, 3, 2],
    akebono=[2, 1, 4, 2, 3],
"""
