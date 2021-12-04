import csv
import datetime
import operator

from ratio_encoder import TIMEFRAME_DAYS, read_data_source, DATA_SINK, FIELDNAMES, _ROOT

GOLD = 'gc_cmx'
TRAINING_DATA = _ROOT / 'gold_training_data_a.csv'
WINDOW_SIZE = 28


def main():
    table = list(read_data_source(DATA_SINK))
    table.sort(key=operator.itemgetter('Date'), reverse=True)
    table_size = len(table)
    print(f'{table_size = }')
    time_diff = datetime.timedelta(days=TIMEFRAME_DAYS)
    new_table = []
    for offset, record in enumerate(table):
        history = offset + TIMEFRAME_DAYS
        if history >= table_size:
            # history is out of bounds
            break
        past_record = table[history]
        if past_record['Date'] + time_diff != record['Date']:
            raise ValueError('incorrect record was accessed')
        new_record = past_record.copy()
        new_record['TARGET'] = record[GOLD]
        new_table.append(new_record)
    print(f'{len(new_table) = }')
    if WINDOW_SIZE > 0:
        wide_table = create_wide_table(new_table)
        new_table = wide_table
    new_table.sort(key=operator.itemgetter('Date'))
    for record in new_table:
        del record['Date']
    FIELDNAMES.append('TARGET')
    FIELDNAMES.remove('Date')
    print(f'{len(new_table) = }')
    with TRAINING_DATA.open('w', newline='') as file:
        data_writer = csv.DictWriter(file, FIELDNAMES)
        # data_writer.writeheader()
        data_writer.writerows(new_table)


def create_wide_table(new_table):
    new_table_size = len(new_table)
    wide_table = []
    new_columns = []
    for offset in range(1, WINDOW_SIZE):
        for fn in FIELDNAMES:
            if fn != 'Date':
                new_columns.append(f'{fn}_h{offset}')
    for offset, record in enumerate(new_table):
        last_offset = offset + WINDOW_SIZE - 1
        if last_offset >= new_table_size:
            print(f'{offset = }')
            break
        wide_record = record.copy()
        nc_names = iter(new_columns)
        for index in range(1, WINDOW_SIZE):
            h_offset = offset + index
            h_record = new_table[h_offset]
            for fn in FIELDNAMES:
                if fn != 'Date':
                    wide_record[next(nc_names)] = h_record[fn]
        try:
            print(f'{next(nc_names)}')
        except StopIteration:
            pass
        else:
            raise ValueError('there is something wrong with the columns')
        wide_table.append(wide_record)
    print(f'{len(wide_table) = }')
    FIELDNAMES.extend(new_columns)
    return wide_table


if __name__ == '__main__':
    main()
