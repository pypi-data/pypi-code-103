if __name__ == '__main__':

    from hbshare.quant.stk import index_win, load_index, load_stk_local
    import pandas as pd
    from db_cons import sql_write_path_work
    from datetime import datetime, timedelta

    index_list = [
        '000300',
        '000905',
        '000852'
    ]

    freq_list = [
        'D',
        'W',
        'M',
    ]

    end_date = datetime.now().date()
    # end_date = datetime(2018, 1, 1).date()

    table_index_win = 'index_win'

    for i in freq_list:
        last_date = pd.read_sql_query(
            'select TDATE from ' + table_index_win
            + ' where FREQ=\'' + i + '\' order by TDATE desc limit 1',
            sql_write_path_work['daily']
        )

        if len(last_date) == 0:
            last_date = datetime(2010, 1, 1).date()
        else:
            last_date = last_date['TDATE'][0] + timedelta(days=1)

        index_data = load_index(index_list=index_list, start_date=last_date, end_date=end_date)
        stk_data = load_stk_local(
            start_date=last_date, end_date=end_date, sql_path=sql_write_path_work['daily']
        ).rename(columns={'SYMBOL': 'CODE'})

        index_win_data = index_win(
            index_list=index_list,
            freq=i,
            index_data=index_data,
            stk_data=stk_data
        )
        if len(index_win_data) > 0 or index_win_data is None:
            index_win_data['FREQ'] = i
            index_win_data.to_sql(table_index_win, sql_write_path_work['daily'], if_exists='append', index=False)
        print(i + ' ' + end_date.strftime('%Y/%m/%d') + ' done, ' + str(len(index_win_data)))
