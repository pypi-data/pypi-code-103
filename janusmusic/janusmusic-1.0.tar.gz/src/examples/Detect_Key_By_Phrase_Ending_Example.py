from Song import Song, SongLibrary

# Create a new song object
song = Song()

# Load the desired song into the "song" object
song.load(filename=SongLibrary.MEGADETH_SYMPHONY_OF_DESTRUCTION)    # Actual Key: E Phrygian

# Run the Detect Key method on the song object, capture the returned object
key, report, confidence = song.detect_key_by_phrase_endings()

# Prints the full report
print(report)

# Prints the detected key
print(key.tonic + " " + key.mode)

# Prints confidence
print("Confidence: " + confidence)


