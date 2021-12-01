from Genre import Genre
from Song import Song
import os
from Track import TagEnum
from Key import Key
from markov_chain import MarkovChain, Type
from markov_library import MarkovLibrary
from dynamic_markov_chain import DynamicMarkovChain, chainType

if __name__ == '__main__':

    directory = "C:\\Users\\Eli\\Documents\\GitHub\\2021FallTeam17-DeHaan\\MIDI Files\\Rock"
    genre = Genre()
    for artist in os.listdir(directory):
        artist_directory = directory + '\\' + artist.title()
        for song in os.listdir(artist_directory):
            song_object = Song()
            print(song)
            try:
                song_object.load(filename=artist_directory + '\\' + song.title())
            except (IOError, AttributeError) as e:
                continue
            current_key = song_object.detect_key_and_scale()[0]
    #         # print(current_key.tonic)
    #         # song_object.change_song_key(current_key, Key())
            genre.add_song(song_object)

    chord_chain = DynamicMarkovChain("chord chain", token_length=3, chain_type=chainType.CHORD)
    note_chain = DynamicMarkovChain("note chain", token_length=3, chain_type=chainType.NOTE)
    for song in genre.songs:
        try:
            chord_chain.add_song(song)
        except AttributeError as e:
            continue
        note_chain.add_song(song)

    song2 = Song()
    chord_track = chord_chain.generate_pattern(song2, 25, 46)
    melody_track = note_chain.generate_pattern(song2, 100, 25)

    song2.add_track(chord_track)
    song2.add_track(melody_track)

    song2.save('generated_song.mid', True)
    #
    # genre.get_notes_frequency_graph()
    # genre.print_songs()

    # song = Song()
    # song.load(filename="../MIDI Files/Rock/Elton John/TinyDancer.mid", print_file=False)
    # chord_chain = DynamicMarkovChain("chord chain", token_length=3, chain_type=chainType.CHORD)
    # note_chain = DynamicMarkovChain("note chain", token_length=3, chain_type=chainType.NOTE)
    # chord_chain.add_song(song)
    # note_chain.add_song(song)
    # song2 = Song()
    # chord_chain.generate_pattern(song2, 25, 46)
    # note_chain.generate_pattern(song2, 100, 25)
    # song2.save('generated_song.mid', True)


    # song.load(filename="../MIDI Files/Hip-Hop/Kanye West/24851_Gold-Digger.mid", print_file=True)
    # song.load(filename="../test/test MIDI/C_major_chords.mid")
    # song.load(filename="../MIDI Files/Utility/C_Major_Pentatonic.mid", print_file=False)
    # song.load(filename="../MIDI Files/Pop/Adele/Someone_Like_You_easy_piano.mid", print_file=False)
    # song.change_song_key(Key(tonic=song.detect_key_and_scale()[0:1]), Key())
    # song.get_transition_graph(name="Someone Like You")
    # song.load(filename="../MIDI Files/Rock/Elton John/TinyDancer.mid", print_file=False)
    # song.change_song_key(Key(tonic=song.detect_key_and_scale()[0:1]), Key())
    # song.get_transition_graph(name="Tiny Dancer")
    # song.get_transition_graph(name="Skyfall")
    # song.change_song_key(Key(tonic=song.detect_key_and_scale()[0:1]), Key())
    # song.get_transition_graph(name="Your Song")

    # for track in song.tracks:
    #     print("track: " + track.track_name)
    #     for chord in track.chords:
    #         print("  Chord: ")
    #         for note in chord.notes:
    #             print("    " + str(note.pitch) + " Time: " + str(note.time) + " channel: " + str(note.channel))

    # print(song.to_string())

    # song.print_song()

    # song.load(filename="../MIDI Files/Hip-Hop/Kanye West/24851_Gold-Digger.mid", print_file=False)
    # song.get_note_frequency_graph("Gold Digger by Kanye West")
    # song.get_note_velocity_graph("Gold Digger by Kanye West")
    # song.load(filename="music samples/Mii Channel.mid", print_file=True)
    # song.load(filename="music samples/Megadeth-Symphony Of Destruction.mid", print_file=True)

    # print(song.to_string())

    # print(song.detect_key())

    # for track in song.tracks:
    #     print(track.track_name + " -- " + str(track.tag))

    # song.detect_key_by_phrase_endings()

    # for track in song.tracks:

    # song.change_song_key(origin_key=Key('F#', 'major'), destination_key=Key('C', 'major'))
    # song.save(filename="music samples/Megadeth-Tornado of Souls.mid", print_file=True)

    # song.save(filename="music samples/Mii Channel Output.mid", print_file=True)
