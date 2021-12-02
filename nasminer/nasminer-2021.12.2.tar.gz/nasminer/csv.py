from csv import DictReader


def estimateDelimiters(filepath):
    with open(filepath, 'r', encoding='latin1') as csvfile:
        try:
            line1 = next(csvfile)
            line2 = next(csvfile)
        except StopIteration:
            raise ValueError('No data to read')
    if ';' in line1:
        seperator = ';'
        if '.' in line2:
            decimal = '.'
        else:
            decimal = ','
    else:
        seperator = ','
        decimal = '.'
    return (seperator, decimal)


def readColnames(csvfilepath, sep):
    reader = DictReader(csvfilepath, delimiter=sep)
    try:
        sample = next(reader)
    except StopIteration:
        raise ValueError('No data')
    colnames = list(sample.keys())
    return colnames
