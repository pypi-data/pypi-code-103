import movdata.eetools as eetools
import ee
import sklearn.mixture as gauss
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import datetime as dt
import logging
from scipy.stats import norm
import numpy as np

logger = logging.getLogger(__name__)


class Seasons:

    def __init__(self, start=None, end=None,
                 season_n=2, season_labels=None,
                 img_col='MODIS/MCD43A4_006_NDVI', band='NDVI',
                 analysis_scale_m=500, analysis_geo=None, analysis_date_chunks=3,
                 calibration_func=None):
        self._start = start
        self._end = end
        self._season_n = season_n
        self._season_labels = season_labels
        self._img_col = img_col
        self._band = band
        self._analysis_scale_m = analysis_scale_m
        self._analysis_geo = analysis_geo
        self._seasonal_cuts = None
        self._vals = None
        self._analysis_date_chunks = analysis_date_chunks  # ~ 2500 image collection limit in GEE
        self._calibration_func = calibration_func

    # ToDo: rewrite this function using a geopands DF as an input to handle multi-regions. And also write it using the
    # eetools.extract_img_values paradigm where the function 'extract_seasonal_values' is provided as input to the
    # eetools.extract_img_values function

    def extract_seasonal_vals(self, ee_geo=None, scale=500):

        """
        :param ee_geo: ee_geo is an EE Geometry type
        :param scale:
        :return:
        """

        # To-Do: define an identity calibration function if none exists
        # img_coll = ee.ImageCollection(self._img_coll).select(self._band).map(self.unityfunc).toArray()

        secs = self._end.timestamp() - self._start.timestamp()
        chunk_size = secs // self._analysis_date_chunks
        date_slices = []
        cur_timestamp = self._start.timestamp()
        while cur_timestamp < self._end.timestamp():
            date_slices.append(cur_timestamp)
            cur_timestamp += chunk_size
        date_slices.append(self._end.timestamp() + 1)

        result_df = []

        for i in range(len(date_slices) - 1):

            start = dt.datetime.fromtimestamp(date_slices[i])
            end = dt.datetime.fromtimestamp(date_slices[i + 1] - 1)
            print('Processing date range: ', start, end)

            # get the image stack
            img_coll = ee.ImageCollection(self._img_col).select(self._band). \
                filterBounds(self._analysis_geo).filter(ee.Filter.date(start, end)). \
                sort('system:time_start', False)

            # add time info
            tmpColl = img_coll.map(eetools.add_img_time).toArray()

            # extract the pixel values falling within the region and for the given dates
            ee_result = tmpColl.reduceRegion(ee.Reducer.toList(), self._analysis_geo, self._analysis_scale_m).getInfo()

            vals = pd.DataFrame([[x[0], eetools.convertUnixTimeToDateTime(x[1])] for y in ee_result.get('array')
                                 for x in y], columns=['val', 'datetime'])

            if vals is not None:
                if self._calibration_func is not None:
                    vals['val'].apply(self._calibration_func)
                result_df.append(vals)

        self._vals = pd.concat(result_df, axis=0).sort_values(by='datetime')

        return self._vals

    def determine_seasonal_cut_values(self):

        try:
            if self._vals is not None:
                distr = gauss.GaussianMixture(n_components=self._season_n, max_iter=500)
                vals = self._vals['val'].values.reshape(-1, 1)
                distr.fit(vals)
                mu_vars = np.array(sorted(zip(distr.means_.flatten(),
                                              distr.covariances_.flatten()), key=lambda x: x[0]))
                print('mu_vars', mu_vars)
                cuts = []
                x = np.linspace(0, 1.0, 1000)
                for i in range(1, len(mu_vars)):
                    cuts.append(np.max(x[tuple([norm.sf(x, loc=mu_vars[tuple([i - 1, 0])],
                                                  scale=np.sqrt(mu_vars[tuple([i - 1, 1])])) >
                                          norm.cdf(x, loc=mu_vars[tuple([i, 0])],
                                                   scale=np.sqrt(mu_vars[tuple([i, 1])]))])]))
                cuts.append(float("inf"))
                cuts.append(float("-inf"))
                self._seasonal_cuts = sorted(cuts)

            else:
                logger.exception('Could not run EM algorithm on null vals array.')
        finally:
            return self._seasonal_cuts

    def determine_seasonal_windows(self, reducer_func=np.mean):

        result = None

        try:
            self.extract_seasonal_vals()
            self.determine_seasonal_cut_values()

            if self._seasonal_cuts is None:
                logger.exception('Could not determine_seasonal_windows on null cut values array.')

            if self._vals is None:
                logger.exception('Could not determine_seasonal_windows on null values array.')

            def g(group):
                group['reduce_val'] = group['val'].agg(reducer_func)
                return group.iloc[0]  # return first row only

            df = self._vals.groupby('datetime').apply(g)
            df.drop(labels=['val'], axis=1, inplace=True)

            season_labels = self._season_labels
            if season_labels is None:
                season_labels = ['season_' + str(x) for x in range(len(self._seasonal_cuts))]

            df['season'] = pd.cut(df['reduce_val'], bins=self._seasonal_cuts, labels=season_labels)

            enc = LabelEncoder()
            df['season_code'] = enc.fit_transform(df['season'])

            '''Adapted from https://stackoverflow.com/questions/26911851/
            how-to-use-pandas-to-find-consecutive-same-data-in-time-series'''
            df['Unique Season'] = (df['season_code'].diff(1) != 0).astype('int').cumsum()
            df['end'] = df['datetime'].shift(-1)

            # data = OrderedDict([('start', df.groupby('Unique Season')['datetime'].first()),
            #                     ('end', df.groupby('Unique Season')['end'].last()),
            #                     ('season', df.groupby('Unique Season')['season'].first())])
            #
            # result = pd.DataFrame(data, columns=data.keys())

            result = pd.concat([pd.Series([grp['datetime'][0] for name, grp in df.groupby('Unique Season')]),
                                pd.Series([grp['datetime'][-1] for name, grp in df.groupby('Unique Season')]),
                                pd.Series([name for name, _ in df.groupby('Unique Season')]),
                                pd.Series(grp['season'][0] for name, grp in df.groupby('Unique Season'))], axis=1)
            result.columns = ['start', 'end', 'unique_season', 'season']
            result.set_index('unique_season', inplace=True)

        except Exception as e:
            print(e)

        finally:
            return result
