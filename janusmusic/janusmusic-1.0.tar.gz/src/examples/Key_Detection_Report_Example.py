from BatchReporting import generate_batch_key_detection_report

# Using this method you can generate a CSV file which will run key detection on an
# entire file directory formatted with sub directories as genre/artist/song.mid
# This CSV file will be created in a new directory (under the same PWD as the calling
# script)
generate_batch_key_detection_report(top_directory_path="../../MIDI Files")
