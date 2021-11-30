import pandas as pd
import numpy as np
import datetime


class ImuDataSource:

    def __init__(self, filename: str, offset_sec: int = 0):
        converters = {'timestamp': lambda x: datetime.datetime.fromtimestamp(float(x))}
        df = pd.read_csv(filename, converters=converters, sep=';')
        df.timestamp -= df.timestamp[0] + pd.Timedelta(offset_sec, 's')
        df['timestamp_diff'] = df.timestamp.diff().dt.total_seconds() * 1e6
        df = df.set_index('timestamp')
        df['seconds'] = df.index / np.timedelta64(1, 's')
        self.df = df

    def _get_data(self, regex, rename_cols=True):
        data = self.df.filter(regex=regex).copy()
        if rename_cols:
            data.columns = ['x', 'y', 'z']
        return data

    def _set_data(self, regex, data: np.ndarray):
        slice = self.df.filter(regex=regex)
        self.df.loc[:, slice.columns] = data

    def merge(self, other):
        otherdf = other.df.copy().drop(['window_us', 'seconds', 'timestamp_diff'], axis=1)
        self.df = pd.merge(self.df, otherdf, how='outer', left_index=True, right_index=True)
        self.df.fillna(method='ffill', inplace=True)

    def to_csv(self, filename: str):
        self.df.rename(columns={'seconds': 'timestamp'}, inplace=True)
        self.df.index = self.df.timestamp
        self.df.to_csv(filename, sep=';')

    def get_hpca_gyro(self, nodeid=0):
        return self._get_data(regex=f'^hg[xyz]{nodeid}$')

    def set_hpca_gyro(self, nodeid, data):
        return self._set_data(f'^hg[xyz]{nodeid}$', data)

    def get_hpca_accel(self, nodeid=0):
        return self._get_data(regex=f'^ha[xyz]{nodeid}$')

    def set_hpca_accel(self, nodeid, data):
        return self._set_data(f'^ha[xyz]{nodeid}$', data)

    def get_bmx_gyro(self, nodeid=0):
        return self._get_data(regex=f'^bg[xyz]{nodeid}$')

    def set_bmx_gyro(self, nodeid, data):
        return self._set_data(f'^bg[xyz]{nodeid}$', data)

    def get_bmx_accel(self, nodeid=0):
        return self._get_data(regex=f'^ba[xyz]{nodeid}$')

    def set_bmx_accel(self, nodeid, data):
        return self._set_data(f'^ba[xyz]{nodeid}$', data)

    def get_scl_accel(self, nodeid=0):
        return self._get_data(regex=f'^pa[xyz]{nodeid}$')

    def get_pi48_gyro(self):
        return self._get_data(regex=r'^pi48g[xyz]\d*?$')

    def get_pi48_accel(self):
        return self._get_data(regex=r'^pi48a[xyz]\d*?$')

    def get_imu_data(self, nodeid=None):
        nodeid_regex = r'\d*?' if not nodeid else nodeid
        gyro = self.df.filter(regex=f'^(pi48|h|b)g[xyz]{nodeid_regex}$')
        gyro.index = self.df.seconds
        accelerometer = self.df.filter(regex=f'^(pi48|h|b|p)a[xyz]{nodeid_regex}$')
        accelerometer.index = self.df.seconds
        return gyro, accelerometer

    def get_timestamped_imu_data(self, nodeid=None):
        nodeid_regex = r'\d*?' if not nodeid else nodeid
        gyro = self.df.filter(regex=f'^(pi48|h|b)g[xyz]{nodeid_regex}$')
        accelerometer = self.df.filter(regex=f'^(pi48|h|b|p)a[xyz]{nodeid_regex}$')
        temps = self.df.filter(regex=f'^(h)t{nodeid_regex}$')
        return gyro, accelerometer, temps

    def get_ekf_data(self, nodeid=None):
        nodeid_regex = r'\d*?' if not nodeid else nodeid
        dcm = self.df.filter(regex=f'^dcm3[123]{nodeid_regex}$')
        inno = self.df.filter(regex=f'inno[xyz]{nodeid_regex}$')
        pos = self.df.filter(regex=f'^pos[xyz]{nodeid_regex}$')
        vel = self.df.filter(regex=f'^vel[xyz]{nodeid_regex}$')
        gbias = self.df.filter(regex=f'^gbias[xyz]{nodeid_regex}$')
        ascale = self.df.filter(regex=f'^ascale[xyz]{nodeid_regex}$')
        status = self.df.filter(regex=f'^ekf_update_mode{nodeid_regex}$')
        return dcm, inno, pos, vel, gbias, ascale, status

    def get_euler_angles(self, nodeid=None):
        nodeid_regex = r'\d*?' if not nodeid else nodeid
        rpy = self.df.filter(regex=f'^(roll|pitch|yaw){nodeid_regex}$')
        return rpy

    def get_gps_data(self, nodeid=None):
        nodeid_regex = r'\d*?' if not nodeid else nodeid
        rpy = self.df.filter(regex=f'^gps.*{nodeid_regex}$')
        return rpy


class AngleDataSource:

    def __init__(self, filename, offset_sec=0):
        converters = {'timestamp': lambda x: datetime.datetime.fromtimestamp(float(x))}
        df = pd.read_csv(filename, converters=converters, sep=',')
        print(df)
        df.timestamp -= df.timestamp[0] + pd.Timedelta(offset_sec, 's')
        df['timestamp_diff'] = df.timestamp.diff().dt.total_seconds() * 1e6
        df = df.set_index('timestamp')
        df['seconds'] = df.index / np.timedelta64(1, 's')
        self.df = df

    def _get_data(self, regex, rename_cols=True):
        return self.df.filter(regex=regex).copy()

    def get_pitch_roll(self, nodeid=0):
        return self._get_data(regex=r'^(pitch|roll)$')

    def get_status(self):
        return self._get_data(regex=r'^status\d$')

    def get_angles(self):
        return self._get_data(regex=r'^angle\d$')


def load_data(file1: str, file2: str = None, file2_offset_sec: float = 0):
    src1 = ImuDataSource(file1)
    if file2:
        src2 = ImuDataSource(file2, pd.Timedelta(file2_offset_sec, 's'))
        src1.merge(src2)
    return src1
