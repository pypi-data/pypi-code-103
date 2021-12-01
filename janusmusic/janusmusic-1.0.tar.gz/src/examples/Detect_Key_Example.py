"""
    This is the example for how to use the key detection functionality in Song.  Feel free to edit the
    song which is loaded in on line #12 to try detecting keys/scales for other songs.
"""

from Song import Song, SongLibrary

# Create an empty song object
song = Song()

# Load the MIDI file into the song object
song.load(filename=SongLibrary.SIMON_AND_GARFUNKEL_SCARBOROUGH_FAIR)

# Run the key detection algorithm which returns a key object, the number of errors, and percent confidence as a tuple
detected_key, number_of_errors, percent_confidence = song.detect_key_and_scale()

# Print the result
print(detected_key.tonic, detected_key.mode, number_of_errors, percent_confidence)

# or alternatively song.detect_key returns the resulting keys/scales so if you don't care about the inner
# workings of the detection algorithm just print the result (or use it as a list) as such:
#
# print(detect_key)

