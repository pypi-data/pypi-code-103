import chardet
from chardet.universaldetector import UniversalDetector

def detect_file_encode(pth):
    """Guess file content encode by chardet

    :param str pth: file path
    :return: {'encoding': 'UTF-8', 'confidence': 0.99}
    :rtype: list
    """
    detector = UniversalDetector()
    detector.reset()
    for line in open(pth, 'rb'):
        detector.feed(line)
        if detector.done: break
    detector.close()
    return detector.result

def detect_data_encode(rawdata):
    """Guess rawdata encode by chardet

    :param bytes rawdata: file path
    :return: {'encoding': 'UTF-8', 'confidence': 0.99}
    :rtype: list
    """
    return chardet.detect(rawdata)