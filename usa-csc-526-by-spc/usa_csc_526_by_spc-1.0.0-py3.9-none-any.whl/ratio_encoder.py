import csv
import datetime
import operator
import pathlib
import sys

TIMEFRAME_DAYS = 7
_ROOT = pathlib.Path(sys.argv[0]).parent
DATA_SOURCE = _ROOT / 'clean_data_a.csv'
DATA_SINK = _ROOT / 'ratio_data_a.csv'
FIELDNAMES = []


def main():
    table = list(read_data_source(DATA_SOURCE))
    table.sort(key=operator.itemgetter('Date'), reverse=True)
    table_size = len(table)
    time_diff = datetime.timedelta(days=TIMEFRAME_DAYS)
    new_table = []
    non_ratio_columns = set()
    for offset, record in enumerate(table):
        history = offset + TIMEFRAME_DAYS
        if history >= table_size:
            # history is out of bounds
            break
        past_record = table[history]
        if past_record['Date'] + time_diff != record['Date']:
            raise ValueError('incorrect record was accessed')
        new_record = record.copy()
        for key, value in new_record.items():
            if key != 'Date':
                try:
                    new_record[key] = value / past_record[key]
                except ZeroDivisionError:
                    non_ratio_columns.add(key)
        new_table.append(new_record)
    for column in non_ratio_columns:
        for record in new_table:
            del record[column]
        FIELDNAMES.remove(column)
    new_table.sort(key=operator.itemgetter('Date'))
    with DATA_SINK.open('w', newline='') as file:
        data_writer = csv.DictWriter(file, FIELDNAMES)
        data_writer.writeheader()
        data_writer.writerows(new_table)


def read_data_source(data_source):
    with data_source.open(newline='') as file:
        file_reader = csv.DictReader(file)
        FIELDNAMES.extend(file_reader.fieldnames)
        for row in file_reader:
            for key, value in row.items():
                if key == 'Date':
                    row[key] = datetime.datetime.strptime(value, '%Y-%m-%d').date()
                else:
                    row[key] = float(value)
            yield row


if __name__ == '__main__':
    main()
