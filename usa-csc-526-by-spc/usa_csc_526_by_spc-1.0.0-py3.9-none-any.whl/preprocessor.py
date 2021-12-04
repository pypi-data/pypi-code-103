import csv
import datetime
import functools
import itertools
import operator
import pathlib
import sys

DATA_DIR = pathlib.Path('nasdaq_data')
ROOT = pathlib.Path(sys.argv[0]).parent


def main():
    historical_data = tuple(get_historical_data())
    all_historical_dates = {record['Date'] for record in historical_data}
    abs_min_date = min(all_historical_dates)
    abs_max_date = max(all_historical_dates)
    print(f'{abs_min_date = }')
    print(f'{abs_max_date = }')
    # all_range_dates = set(date_range(abs_min_date, abs_max_date))
    min_dates = set()
    max_dates = set()
    not_in_2016 = set()
    for source, dates in get_dates_by_source(historical_data):
        dates = set(record['Date'] for record in dates)
        md = min(dates)
        min_dates.add(md)
        max_dates.add(max(dates))
        if md.year > 2016:
            not_in_2016.add(source)
    print(f'{max(min_dates) = }')
    print(f'{min(max_dates) = }')
    print(f'{len(not_in_2016) = }')
    print(f'{not_in_2016 = }')
    data_by_source = organize_historical_data(historical_data)
    for source in not_in_2016:
        del data_by_source[source]
    print(sorted(set(map(len, data_by_source.values()))))
    fill_data_holes(data_by_source)
    print(sorted(set(map(len, data_by_source.values()))))
    valid_dates = functools.reduce(operator.and_, ({record['Date'] for record in records} for records in data_by_source.values()))
    print(f'{len(valid_dates) = }')
    print(valid_dates)
    clean_rows = generate_cleaned_data(valid_dates, data_by_source)
    with (ROOT / 'clean_data_a.csv').open('w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(clean_rows)


def get_historical_data():
    for path in DATA_DIR.glob('*.csv'):
        symbol = path.stem.split('_', 2)[-1]
        with path.open(newline='') as file:
            for row in csv.DictReader(file):
                yield {'Source': symbol,
                       'Date': datetime.datetime.strptime(row['Date'], '%m/%d/%Y').date(),
                       'Close': float(row['Close/Last'].removeprefix('$'))}


def date_range(start, stop):
    if start > stop:
        raise ValueError('start may not be greater than stop')
    day = datetime.timedelta(days=1)
    while start <= stop:
        yield start
        start += day


def get_dates_by_source(historical_data):
    for source, dates in itertools.groupby(historical_data, key=lambda record: record['Source']):
        yield source, dates


def organize_historical_data(historical_data):
    table = {}
    for source, records in itertools.groupby(historical_data, key=lambda record: record['Source']):
        records = sorted(records, key=lambda record: record['Date'])
        table[source] = records
    return table


def fill_data_holes(data_by_source):
    for source, records in data_by_source.items():
        data_by_source[source] = tuple(replay_without_holes(records))


def replay_without_holes(records):
    last_record = None
    day = datetime.timedelta(days=1)
    for offset, record in enumerate(records):
        if offset:
            last_date = last_record['Date']
            next_date = record['Date']
            current_date = last_date + day
            while current_date < next_date:
                new_record = last_record.copy()
                new_record['Date'] = current_date
                yield new_record
                current_date += day
        yield record
        last_record = record


def generate_cleaned_data(valid_dates, data_by_source):
    columns = [sorted(valid_dates)]
    for source, records in data_by_source.items():
        columns.append(filter(lambda item: item['Date'] in valid_dates, records))
    for offset, (date, *records) in enumerate(zip(*columns)):
        if not offset:
            row = ['Date']
            for record in records:
                row.append(record['Source'])
            yield row
        row = [date]
        for record in records:
            if record['Date'] != date:
                raise ValueError('dates are not properly synchronized')
            row.append(record['Close'])
        yield row


if __name__ == '__main__':
    main()
