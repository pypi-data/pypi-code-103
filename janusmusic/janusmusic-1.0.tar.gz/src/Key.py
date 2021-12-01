import string

MAJOR = "major"
IONIAN = "ionian"
DORIAN = "dorian"
PHRYGIAN = "phrygian"
LYDIAN = "lydian"
MIXOLYDIAN = "mixolydian"
MINOR = "minor"
AOLIAN = "aolian"
LOCRIAN = "locrian"

KEYS = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
EQUIVALENT_KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
MODES = [MAJOR, DORIAN, PHRYGIAN, LYDIAN, MIXOLYDIAN, MINOR, LOCRIAN]
EQUIVALENT_MODES = [IONIAN, DORIAN, PHRYGIAN, LYDIAN, MIXOLYDIAN, AOLIAN, LOCRIAN]


class Mode:
    MAJOR = "major"
    IONIAN = "ionian"
    DORIAN = "dorian"
    PHRYGIAN = "phrygian"
    LYDIAN = "lydian"
    MIXOLYDIAN = "mixolydian"
    MINOR = "minor"
    AOLIAN = "aolian"
    LOCRIAN = "locrian"


class Key:

    def __init__(self, tonic='C', mode='major'):
        """ Constructor for the Key class.

        Args:
            tonic (str): Value for the tonic of the key of the song. Defaults to 'C'.
            type (str): Type of key the song is in. Defaults to 'major'.

        Raises:
            SyntaxError: If the key is not within the list of keys and their equivalents
        """        
        if tonic not in KEYS and tonic not in EQUIVALENT_KEYS:
            raise SyntaxError("Key '" + str(tonic) +
                              "' needs to be the key and #/b if necessary. Examples: 'C#', 'Db', 'F' etc")
        elif mode.lower() not in MODES and mode.lower() not in EQUIVALENT_MODES:
            raise SyntaxError("Mode " + str(mode) + " needs to be a valid mode. Examples: major, minor, dorian, etc" )
        else:
            self.tonic = tonic
            self.mode = mode.lower()

    def get_c_based_index_of_key(self):
        """ Takes a key (as a string) and converts it to the index of this key based on the NOTES and EQUIVALENCE
        arrays specified at the top of this file

        Raises:
            SyntaxError: The key is not a valid key within the list of keys and equivalents

        Returns:
            int: index of this key in the list of notes
        """        
        if self.tonic in KEYS:
            index = KEYS.index(self.tonic)
        elif self.tonic in EQUIVALENT_KEYS:
            index = EQUIVALENT_KEYS.index(self.tonic)
        else:
            raise SyntaxError("Key '" + str(self.tonic) +
                              "' needs to be the key and #/b if necessary. Examples: 'C#', 'Db', 'F' etc")
        return index

