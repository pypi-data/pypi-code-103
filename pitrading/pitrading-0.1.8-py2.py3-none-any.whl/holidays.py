#! /usr/bin/python3

from datetime import date, datetime, timedelta
import warnings
import pandas as pd

# https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

class Holidays:
    @classmethod
    def to_datetime(self, datestr:str) -> datetime:
        """
        Convert date strings like "20210506" to datetime type.

        Parameters
        ----------
        datestr : str (in '%Y%m%d' format), or valid datetime object.

        Raises
        ------
        ValueError
            * If datestr argument is invalid

        Examples
        --------
        >>> yyyymmdd = "20210530"
        >>> dt = Holidays.to_datetime(yyyymmdd)
        """
        if type(datestr) == type(datetime.now()):
            return datestr

        try:
            return datetime(
                    year=int(datestr[0:4]),
                    month=int(datestr[4:6]),
                    day=int(datestr[6:8]),
                )
        except:
            raise ValueError ("Wrong datestr argument, should be like: '20210526'.")

    @classmethod
    def tradingday(self, tm: datetime) -> bool:
        """
        Return True if given date is a tradingday, or False otherwise

        Parameters
        ----------
        tm : datetime object, or valid date string like "20210530".

        Raises
        ------
        ValueError
            * If tm argument is invalid

        Examples
        --------
        >>> dt = datetime.now()
        >>> is_tradingday = tradingday(dt)
        """
        if type(tm) != type(datetime.now()):
            tm = self.to_datetime(tm)

        if int(tm.strftime("%w")) in [6,0]:
            return False

        tm_str = tm.strftime('%m/%d/%Y')

        if tm_str in self.SSEHolidays:
            return False

        return True

    @classmethod
    def prev_tradingday(self, tm:datetime) -> datetime:
        """
        Return the previous tradingday of a given date

        Parameters
        ----------
        tm : datetime object, or valid date string like "20210530".

        Raises
        ------
        ValueError
            * If tm argument is invalid

        Examples
        --------
        >>> dt = datetime.now()
        >>> prev_td = prev_tradingday(dt)
        """
        if type(tm) != type(datetime.now()):
            tm = self.to_datetime(tm)
        ret = tm + timedelta(days=-1)
        while not (self.tradingday(ret)):
            ret = ret + timedelta(days=-1)
        return ret

    @classmethod
    def next_tradingday(self, tm: datetime) -> datetime:
        """
        Return the next tradingday of a given date.

        Parameters
        ----------
        tm : datetime object, or valid date string like "20210530".

        Raises
        ------
        ValueError
            * If tm argument is invalid

        Examples
        --------
        >>> dt = datetime.now()
        >>> next_td = next_tradingday(dt)
        """
        if type(tm) != type(datetime.now()):
            tm = self.to_datetime(tm)
        ret = tm + timedelta(days=1)
        while not (self.tradingday(ret)):
            ret = ret + timedelta(days=1)
        return ret

    @classmethod
    def get_holidays(self) -> pd.DataFrame:
        """
        Return a pandas.DataFrame object with only one column
        named 'Dates' containing all the holidays.

        Examples
        --------
        >>> h_days = get_holidays()
        """
        ret = pd.DataFrame()
        ret['Dates'] = [datetime.strptime(dt, "%m/%d/%Y") for dt in self.SSEHolidays]
        return ret

    @classmethod
    def range_exp(self, start: str, end: str) -> pd.DataFrame:
        """
        Return a pandas.DataFrame object with only one column named
        'exp' containing all the expirations between start and end.

        Parameters
        ----------
        start : valid date string like "20180101"
        end   : valid date string like "20221231"

        Raises
        ------
        ValueError
            * If start argument is invalid
            * If end argument is invalid
            * If year gap of end and now is over 1
            * If year of start is before 2015

        Examples
        --------
        >>> exps = range_exp("20180101", "20221231")
        >>> exps = range_exp("20221231", "20180101")
        """
        if len(start) != 8 or len(end) != 8:
            raise ValueError("Invalid input arg")
        dts = min(start, end)
        dte = max(start, end)
        ds = self.to_datetime(dts)
        de = self.to_datetime(dte)
        if ds.year < 2015:
            S = f"History caveat: year of range start ({ds.year}) before 2015 is not supported"
            raise ValueError(S)
        if de.year - datetime.now().year > 1:
            S = f"Future caveat: year gap between now ({datetime.now().year}) and range end ({de.year}) is over 1 year"
            raise ValueError(S)
        di = ds
        L = []
        while di <= de:
            while di.weekday() != 4:
                di = di + timedelta(days=1)
            if 15 <= di.day <= 21:
                if self.tradingday(di):
                    L.append(di)
                else:
                    L.append(self.next_tradingday(di))
            di = di + timedelta(days=7)
        ret = pd.DataFrame()
        ret['exp'] = L
        # print(ret)
        return ret

    @classmethod
    def get_exp(self, code: str) -> str:
        """
        Return the expiration date of a contract code

        Parameters
        ----------
        code : valid code string like "IF2201"

        Raises
        ------
        ValueError
            * If code is invalid
            * If code is not found

        Examples
        --------
        >>> exp = get_exp("IF2201")
        """
        if len(code) != 6:
            raise ValueError("Invalid input arg")
        ym = "20" + code[2:]
        dt = datetime.strptime(ym, '%Y%m')
        start = dt.strftime('%Y%m%d')
        end = (dt + timedelta(days=30)).strftime('%Y%m%d')
        exps = self.range_exp(start, end)
        if len(exps['exp']) == 0:
            raise ValueError(f"Exp for {code} not found")
        ret = (pd.to_datetime(exps['exp'].values[0])).strftime('%Y-%m-%d')
        # print(ret, type(ret))
        return ret

    SSEHolidays = [
    '01/01/2015', '01/02/2015', '01/03/2015',
    '02/18/2015', '02/19/2015', '02/20/2015', '02/21/2015', '02/22/2015', '02/23/2015', '02/24/2015',
    '04/06/2015', '05/01/2015', '06/20/2015', '06/21/2015', '06/22/2015',
    '09/03/2015', '09/04/2015', '09/05/2015',
    '10/01/2015', '10/02/2015', '10/03/2015', '10/04/2015', '10/05/2015', '10/06/2015', '10/07/2015' ] + \
    [
    '01/01/2016',
    '02/07/2016', '02/08/2016', '02/09/2016', '02/10/2016', '02/11/2016', '02/12/2016', '02/13/2016',
    '04/04/2016', '05/02/2016', '06/09/2016', '06/10/2016', '06/11/2016',
    '09/15/2016', '09/16/2016', '09/17/2016',
    '10/01/2016', '10/02/2016', '10/03/2016', '10/04/2016', '10/05/2016', '10/06/2016', '10/07/2016' ] + \
    [
    '01/01/2017', '01/02/2017', '01/27/2017', '01/28/2017', '01/29/2017', '01/30/2017', '01/31/2017',
    '02/01/2017', '02/02/2017', '04/02/2017', '04/03/2017', '04/04/2017', '05/01/2017', '05/02/2017',
    '05/03/2017', '05/28/2017', '05/29/2017', '05/30/2017', '10/01/2017', '10/02/2017', '10/03/2017',
    '10/04/2017', '10/05/2017', '10/06/2017', '10/07/2017', '10/08/2017' ] + \
    [
    '01/01/2018', '02/15/2018', '02/16/2018', '02/17/2018', '02/18/2018', '02/19/2018' ,'02/20/2018',
    '02/21/2018', '04/05/2018', '04/06/2018', '04/07/2018', '04/29/2018', '04/30/2018', '05/01/2018',
    '06/16/2018', '06/17/2018', '06/18/2018', '10/01/2018', '10/02/2018', '10/03/2018',
    '10/04/2018', '10/05/2018', '10/06/2018', '10/07/2018', '02/04/2019', '02/05/2019', '02/06/2019',
    '02/07/2019', '02/08/2019', '02/09/2019', '02/10/2019', '04/05/2019', '04/06/2019', '04/07/2019',
    '05/01/2019', '05/02/2019', '05/03/2019', '05/04/2019', '06/07/2019', '06/08/2019', '06/09/2019',
    '09/13/2019', '09/14/2019', '09/15/2019', '10/01/2019', '10/02/2019', '10/03/2019',
    '10/04/2019', '10/05/2019', '10/06/2019', '10/07/2019', '01/01/2020', '01/24/2020',
    '01/25/2020', '01/26/2020', '01/27/2020', '01/28/2020', '01/29/2020', '01/30/2020',
    '01/31/2020', '02/01/2020', '02/02/2020', '04/04/2020', '04/05/2020', '04/06/2020', '05/01/2020',
    '05/02/2020', '05/03/2020', '05/04/2020', '05/05/2020', '06/25/2020', '06/26/2020', '06/27/2020',
    '10/01/2020', '10/02/2020', '10/03/2020', '10/04/2020', '10/05/2020', '10/06/2020',
    '10/07/2020', '10/08/2020', '01/01/2021', '01/02/2021', '01/03/2021', '02/11/2021', '02/12/2021',
    '02/13/2021', '02/14/2021', '02/15/2021', '02/16/2021', '02/17/2021', '04/03/2021', '04/04/2021',
    '04/05/2021', '05/01/2021', '05/02/2021', '05/03/2021', '05/04/2021', '05/05/2021',
    '06/12/2021', '06/13/2021', '06/14/2021',
    '09/19/2021', '09/20/2021', '09/21/2021', '10/01/2021', '10/02/2021', '10/03/2021', '10/04/2021',
    '10/05/2021', '10/06/2021', '10/07/2021' ] + \
    [
    '01/01/2022', '01/02/2022', '01/03/2022',
    '01/31/2022', '02/01/2022', '02/02/2022', '02/03/2022', '02/04/2022', '02/05/2022', '02/06/2022',
    '04/03/2022', '04/04/2022', '04/05/2022',
    '05/01/2022', '05/02/2022', '05/03/2022', '05/04/2022', '05/05/2022',
    '06/03/2022', '06/04/2022', '06/05/2022',
    '09/09/2022', '09/10/2022', '09/11/2022',
    '10/01/2022', '10/02/2022', '10/03/2022', '10/04/2022', '10/05/2022', '10/06/2022', '10/07/2022' ]




if '__main__' == __name__:
    dt1 = datetime(2021,5,6)
    tm1 = "20210506"
    print(type(dt1), Holidays.to_datetime(dt1), Holidays.tradingday(dt1), Holidays.prev_tradingday(dt1), Holidays.next_tradingday(dt1))
    print(type(tm1), Holidays.to_datetime(tm1), Holidays.tradingday(tm1), Holidays.prev_tradingday(tm1), Holidays.next_tradingday(tm1))
    dt2 = datetime(2021,9,30)
    tm2 = "20210930"
    print(type(dt2), Holidays.to_datetime(dt2), Holidays.tradingday(dt2), Holidays.prev_tradingday(dt2), Holidays.next_tradingday(dt2))
    print(type(tm2), Holidays.to_datetime(tm2), Holidays.tradingday(tm2), Holidays.prev_tradingday(tm2), Holidays.next_tradingday(tm2))

    print(Holidays.get_holidays())