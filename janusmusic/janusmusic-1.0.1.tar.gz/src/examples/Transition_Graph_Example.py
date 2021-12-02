"""
    This is the example for how to use the chord transition graph functionality. It creates a directed
    cyclical graph with all the chords in the song and the transition that occurs between them. The edges
    depict the number of times that transition occured in the song.

"""

from Song import Song

# Create an empty song object
song = Song()

# Load the MIDI file into the song object
song.load(filename="../../MIDI Files/Rock/Elton John/RocketMan.mid")

# Run the method to get the transition graph and view it
song.get_transition_graph(name="Rocket Man")

# The graph will be viewable in a pdf file in the file directory.
