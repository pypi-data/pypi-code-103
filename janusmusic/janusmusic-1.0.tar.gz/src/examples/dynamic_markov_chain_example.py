from Song import Song, SongLibrary
from Track import Track
from dynamic_markov_chain import DynamicMarkovChain, chainType

# Create a new song object and read in the desired training song
training_song = Song()
training_song.load(filename=SongLibrary.NIRVANA_LITHIUM)

# Create a chord and note markov chain with the given attributes
chord_chain = DynamicMarkovChain("chord chain", token_length=3, chain_type=chainType.CHORD)
note_chain = DynamicMarkovChain("note chain", token_length=4, chain_type=chainType.NOTE)

# Train the new markov chains with the desired song
chord_chain.add_song(training_song)
note_chain.add_song(training_song)

# Create a new song to write to
output_song = Song()

# Create verse sections from the chord and note chains
chd_verse = chord_chain.generate_pattern(output_song, 4, 46, octave=4)
mel_verse = note_chain.generate_pattern(output_song, 16, 72, octave=5)

# Create chorus sections from the chord and note chains
chd_chorus = chord_chain.generate_pattern(output_song, 4, 46, octave=4)
mel_chorus = note_chain.generate_pattern(output_song, 8, 24, octave=5)
mel_chorus2 = note_chain.generate_pattern(output_song, 8, 24, octave=5)

# Create an optional counter melody with the note chain
# bass_mel = note_chain.generate_pattern(output_song, 16, 18, octave=4)

# Create output tracks (different to the individual sections created earlier)
chord_track = Track(channel=2)
melody_track = Track(channel=0)
melody_track_2 = Track(channel=1)

# "Write" the song by stitching together the individual sections into a complete track
chord_track = chord_track.append_tracks([0, 0, 1, 1, 0, 0, 1, 1, 0, 0], [chd_verse, chd_chorus])
melody_track = melody_track.append_tracks([0, 0, 1, 1, 2, 1, 0, 0, 1, 2, 1, 2, 0, 0], [mel_verse, mel_chorus, mel_chorus2])
# melody_track_2 = melody_track_2.append_tracks([0, 0, 0, 0, 0, 0, 0, 0], [bass_mel])

# Add these tracks to the song object
output_song.add_track(chord_track)
output_song.add_track(melody_track)
output_song.add_track(melody_track_2)

# Save the new written song
output_song.save(filename='../../MIDI Files/Demo Output/Structured Song8.mid')