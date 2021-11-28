import csv


def load_symbol(path):
    file = open(path)
    csvreader = csv.reader(file)
    d = {}
    for r in csvreader:
        d[r[0].upper()] = r[1]
    return d
