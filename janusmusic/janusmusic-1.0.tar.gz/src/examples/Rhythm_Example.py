from Rhythm import *
from Song import Song
from Track import TagEnum


song = Song()

# Load the MIDI file into the song object
song.load(filename="../music samples/Mii Channel.mid")

# Rhythm pattern to apply to the song
pattern = [HALF, DOTTED_SIXTEENTH, EIGHTH, SIXTEENTH, QUARTER_REST]

# Apply the rhythm pattern
apply_rhythm_pattern(song=song, track=song.tracks[1], pattern_array=pattern)

# Adds human aspect to rhythm by slightly offsetting rhythm timings
humanify_rhythm(song=song, track=song.tracks[1], humanify_percent=0.1)

#save to midi file
song.save('../../MIDI Files/Demo Output/rhythm.mid')