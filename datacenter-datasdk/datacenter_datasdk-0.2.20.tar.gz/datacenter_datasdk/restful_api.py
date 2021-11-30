# -*-coding:utf-8 -*-

from numpy import datetime64
import requests
import json
import pandas as pd
import datetime
from datacenter_datasdk.settings import td_columns, td_type_map
import datacenter_datasdk.settings as settings
from datacenter_datasdk.verify import verify_args, format_date_param
import zlib
from io import BytesIO
import gzip
import ahttp
import aiohttp
import nest_asyncio
from ahttp import AhttpResponse


nest_asyncio.apply()


def get_int_code(code, region):
    if region == 'cn':
        if 'XSHG' in code:
            code_int = int(code.strip('.XSHG')) + 1000000
        else:
            code_int = int(code.strip('.XSHE')) + 2000000
    elif region == 'us':
        code_int = int(code)
    else:
        code_int = int(code)
    return code_int


def get_str_code(code_int, region):
    if region == 'cn':
        if 2000000 > code_int > 1000000:
            code = '{:06d}.XSHG'.format(code_int-1000000)
        else:
            code = '{:06d}.XSHE'.format(code_int-2000000)
    elif region == 'us':
        code = str(code_int)
    else:
        code = str(code_int)
    return code    


@verify_args(check={'code': (str, list),
                    'region': str,
                    'frequency': str,
                    'start_date': (datetime.datetime, datetime.date, str),
                    'end_date': (datetime.datetime, datetime.date, str)
                    }
             )
def get_price(code: str or list,
              region: str,
              frequency: str,
              start_date: datetime.datetime or datetime.date or str = datetime.datetime(2005, 1, 1),
              end_date: datetime.datetime or datetime.date or str = datetime.datetime.today(
              ).replace(hour=0, minute=0, second=0, microsecond=0)
              ):
    """
    get kline data, include daily, minute and tick

    code: str or list, single code or multi code as list
    region: str, 'cn' or 'us'
    frequency: str, represent frequency of kline, 'd1', 'm1', 'm5', 'm15', 'm30', 'm60' and 'tick'(only in cn)
    start_date, datetime.datetime or datetime.date or str, start time of data, default '2005-01-01'
    end_date, datetime.datetime or datetime.date or str, end time of data, default 0 o'clock of today 
    """
    if not settings.td_token or not settings.td_url:
        raise Exception('auth failed')
    
    if f'{region}_{frequency}' not in td_columns.keys():
        raise Exception(f'{frequency} of {region} not support')
        
    if start_date > end_date:
        raise Exception(f'start_date({start_date}) > end_date({end_date}) on code({code})')
    if isinstance(code, list):
        codes = tuple([get_int_code(c, region) for c in code])
        code_sql = f'code in {codes}'
    else:
        code_int = get_int_code(code, region)
        code_sql = f'code={code_int}'
    
    start_date = format_date_param(start_date)
    end_date = format_date_param(end_date)
    sql_list = []
    # if frequency in ['d1', 'd1_raw', 'd1_post']:
    # years = list(range(int(str(start_date)[:4]), int(str(end_date)[:4]), 1))
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    time_list = []
    while True:
        if start > end:
            time_list.append(end)
            break
        else:
            time_list.append(start)
        start += datetime.timedelta(days=100)
    
    for s, e in zip(time_list[:-1], time_list[1:]):
        if e==time_list[-1]:
            y_sql = f"select * from {region}_{frequency}.{region}_st_{frequency} where ({code_sql}) and (time >= '{s}' and time <='{e}');"
        else:
            y_sql = f"select * from {region}_{frequency}.{region}_st_{frequency} where ({code_sql}) and (time >= '{s}' and time <'{e}');"
        sql_list.append(y_sql)
    # sql_list.append(f"select * from {region}_{frequency}.{region}_st_{frequency} where ({code_sql}) and (time = '{e}');")
    rows = 0
    df_list = []
    # for sql in sql_list:
        # try:
            
        #     r = requests.post(settings.td_url,
        #                     headers={
        #                         'Authorization': f'Basic {settings.td_token}',
        #                         'Accept-Encoding': 'gzip, deflate'
        #                     },
        #                     data=sql
        #                     )
        #     res = json.loads(r.text)
        # except:
        #     contents = []
        #     resp = requests.post(
        #         url=settings.td_url, headers={
        #             'Authorization': f'Basic {settings.td_token}',
        #         },
        #         data=sql, stream=True
        #     )
        #     content = resp.raw.readline()
        #     try:
        #         while content:
        #             contents.append(content)
        #             content = resp.raw.readline()
        #     except Exception:
        #         pass
        #     res_b = b''.join(contents)
        #     # zlibobj = zlib.decompressobj()
        #     # res_str = zlibobj.decompress(res_b)
        #     res_str = zlib.decompress(
        #         res_b,
        #         16+zlib.MAX_WBITS
        #     )
        #     # buff = BytesIO(res_b)
        #     # f = gzip.GzipFile(fileobj=buff)
        #     # res_str = f.read().decode('utf-8')
        #     res = json.loads(res_str)
    sess = ahttp.Session(timeout=aiohttp.ClientTimeout(total=60*30))
    reqs = []
    for sql in sql_list:
        print(sql)
        r0 = sess.post(settings.td_url,
                        headers={
                            'Authorization': f'Basic {settings.td_token}',
                            'Accept-Encoding': 'gzip, deflate'
                        },
                        data=sql,
                        )
        reqs.append(r0)

    resps = ahttp.run(reqs, order=True)

    for r in resps:
        print(f'r: {r}')
        if not isinstance(r, AhttpResponse):
            continue
        if isinstance(r, AhttpResponse) and r.status != 200:
            continue

        res = json.loads(r.text)
        column_meta = res['column_meta']
        data = res['data']
        rows += res['rows']
        # datas.extend(data)
        columns = [i[0] for i in column_meta]
        if data:
            df0 = pd.DataFrame(data=data, columns=columns)
            df_list.append(df0)
            types = [td_type_map.get(i[1]) for i in column_meta]
    if not df_list:
        return pd.DataFrame()
    # if rows == 5000000:
    #     print('单次查询条数不能大于500W条, 此次返回仅500W条')
    df = pd.concat(df_list)
    if frequency != 'tick':
        df = df[df.open != 0]
    df['time'] = df['time'].apply(
        lambda x: datetime.datetime.fromtimestamp(x/1000))
    if frequency != 'tick':
        df['update_date'] = df['update_date'].apply(
            lambda x: datetime.datetime.fromtimestamp(x/1000))

    for t, c in zip(types, columns):
        df[c] = df[c].astype(t)
    df['code'] = df['code'].apply(lambda x: get_str_code(x, region))
    df = df[td_columns.get(f'{region}_{frequency}')]
    return df
