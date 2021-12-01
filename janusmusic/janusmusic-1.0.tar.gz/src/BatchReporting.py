from os import walk, path, makedirs
from Song import Song
import csv


def generate_batch_key_detection_report(top_directory_path=None):
    '''
    This method will generate a CSV report showing the genre, artist, song and detected key
    of each song, as well as number of notes that did not fit the scale of the detected key/scale.

    :param top_directory_path: This is the path containing your tree of midi files.
            it should have a sub structure that looks like: genre/artist/song
    :return: No return, but there should be a reports folder in teh directory
            this method was called from which contains the new CSV report
    '''

    if top_directory_path is None:
        raise SyntaxError("You need to provide the top level directory path.")

    # Generate reports directory if it doesn't already exist
    if not path.exists(path.relpath("reports")):
        makedirs("reports")

    # open the key detection report so that we are able to add rows to it
    with open(path.relpath("reports/key_detection_report.csv"), "w+", newline="") as outputFile:
        writer = csv.writer(outputFile)
        writer.writerow(["Genre", "Artist", "Song", "Detected Tonic", "Detected Mode", "Errors", "% Confidence",
                         "Detected Tonic by Endings", "Detected Mode by Endings", "% Confidence"])

        # Iterate through the file structure converting to songs and adding to csv file
        for (dirpath, dirnames, filenames) in walk(top_directory_path):
            if filenames.__len__() != 0:
                for file in filenames:
                    (fileName, fileExtension) = path.splitext(file)
                    if fileExtension == ".mid" and file is not None:
                        file_path = dirpath + "//" + file
                        song = Song()
                        song.load(file_path)
                        detected_tuple = song.detect_key_and_scale()
                        detect_by_phrase_endings = song.detect_key_by_phrase_endings()
                        detected_key_by_endings = detect_by_phrase_endings[0]
                        confidence = detect_by_phrase_endings[2]
                        (pwd, genre, artist) = dirpath.split("\\")
                        writer.writerow([genre, artist, fileName, detected_tuple[0].tonic, detected_tuple[0].mode,
                                         detected_tuple[1], str(detected_tuple[2] * 100) + "%",
                                         detected_key_by_endings.tonic, detected_key_by_endings.mode, confidence])
