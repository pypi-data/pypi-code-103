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

# Create a chord and melody track
chords = chord_chain.generate_pattern(output_song, num_notes=16, instrument=46, octave=4)
melody = note_chain.generate_pattern(output_song, num_notes=64, instrument=72, octave=5)

# Add the generated tracks to a new song
output_song.add_track(chords)
output_song.add_track(melody)

# Save the new written song
output_song.save(filename='../../MIDI Files/Demo Output/Basic_Markov.mid')
