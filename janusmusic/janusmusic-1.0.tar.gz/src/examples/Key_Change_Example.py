from Song import Song, SongLibrary
from Key import Key, Mode

# Create an empty song object
song = Song()

# Load the MIDI file into the song object
song.load(filename=SongLibrary.AMAZING_GRACE)

# Manually enter the key to change from/to
song.change_song_key(Key("G", Mode.MAJOR), Key("G", Mode.MINOR))

# Use the auto-detected key of the song
# song.change_song_key(song.key, Key("G", Mode.MINOR))


song.save(filename="../../MIDI Files/Demo Output/Amazing_Grace_Major.mid")
