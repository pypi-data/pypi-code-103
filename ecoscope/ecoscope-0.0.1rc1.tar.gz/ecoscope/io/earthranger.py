import pandas as pd

import asyncio
import json
import uuid
from datetime import datetime
from functools import partial
from itertools import chain

import numpy as np
import movdata
import pytz
from pydantic import ValidationError, UUID4

from ecoscope.io.client import EarthRangerClient, AsyncEarthRangerClient
from ecoscope.io.schema import Event, Location, Observation
from ecoscope.io.utils import *

logger = logging.getLogger(__name__)
logging.getLogger('backoff').setLevel(logging.ERROR)  # [backoff] Log only when a giveup event occurs.

initialize_er_client = EarthRangerClient


class EarthRangerException(Exception):
    pass


class EarthRanger:
    def __init__(self, er_client: EarthRangerClient):
        """
        Base class for all the earthranger class io.
        provide both async http and synchronous http request.
        """
        self._er_client = er_client
        self.async_erc_lient = AsyncEarthRangerClient(er_client=self._er_client)

    @staticmethod
    def to_geodataframe(df: pd.DataFrame):
        """Converts the pandas dataframe to geodataframe"""
        gdf = gp.GeoDataFrame(df, geometry=df.location.apply(geometry_point), crs=4326)
        gdf.drop(columns=['location'], inplace=True)
        return gdf


class UserIO(EarthRanger):
    def download_users(self):
        """Downloads all the users has permission to view"""
        users = self._er_client.get_users()
        df = pd.DataFrame(users)
        df = df.apply(axis=1, func=normalize_dict, colname='additional_data')
        return df


class EventIO(EarthRanger):

    @memorize
    def _map_eventtype_id(self):
        """Maps event_id to event_value"""
        eventtypes = self._er_client.get_eventtypes()
        map_et_id = {}
        for et in eventtypes:
            eventtype_id, value = et.get('id'), et.get('value')
            map_et_id[value] = eventtype_id
        return map_et_id

    def _get_eventtype_id(self, et_value=None):
        """get the event id given eventtype value"""
        map_et_id = self._map_eventtype_id()
        return map_et_id.get(str(et_value))

    @property
    def event_fieldnames(self):
        return ['id', 'location', 'time',
                'end_time', 'serial_number',
                'message', 'provenance',
                'event_type', 'priority',
                'attributes', 'comment', 'title',
                'reported_by', 'state',
                'related_subjects',
                'eventsource', 'external_event_id',
                'created_at', 'event_details',
                ]

    @staticmethod
    def _coerce_columns_dtype(df, columns: list, dtype):
        if isinstance(columns, list):
            df[columns] = df[columns].astype(dtype)
        return df

    @property
    def columns_of_dtype_list(self):
        return ['is_contained_in', 'files', 'related_subjects', 'patrols', 'patrol_segments', 'updates']

    def _event_details(self, row):
        non_er_columns = set(row.index).difference(self.event_fieldnames)
        non_er_columns.discard('latitude')
        non_er_columns.discard('longitude')
        non_er_columns.discard('reported_by_id')
        non_er_columns.discard('reported_by_content_type')
        non_er_columns.discard('notes')

        event_details = {}
        for column in non_er_columns:
            val = row.get(column)
            if not np.all(pd.isnull(val)):
                event_details[column] = val
        return event_details

    def upload_events(self, df, event_type):
        def create_event(row):
            longitude = row.get('longitude')
            latitude = row.get('latitude')
            content_type = row.get('reported_by_content_type')
            reported_by = row.get('reported_by_id')
            event_details = self._event_details(row)

            try:
                event = Event(event_details=event_details,
                              event_type=event_type,
                              location=Location(longitude=longitude, latitude=latitude),
                              reported_by=dict(id=reported_by,
                                               content_type=content_type), time=row.get('time'))
            except ValidationError as exc:
                logger.error(exc)
                return pd.Series()
            else:
                response = self._er_client.post_event(event)
                if response and row.get('notes'):
                    note_response = self._er_client.post_event_note(event_id=response.get('id'), notes=row.get('notes'))
                    response['notes'] = note_response[0].get('text')
                    response['notes_id'] = note_response[0]['id']
                return pd.Series(response)

        df = df.apply(create_event, axis=1)
        if df.empty:
            return pd.DataFrame()
        else:
            df = self._coerce_columns_dtype(df, self.columns_of_dtype_list, str)
        return self.to_geodataframe(df)

    def download_events(self, event_type: typing.Union[UUID4, str],
                        start: datetime = None,
                        end: datetime = None,
                        page_size: int = 2500):
        """To download events, one can pass eventtype value or eventtype id"""
        try:
            uuid.UUID(event_type)
        except ValueError:
            event_type = self._get_eventtype_id(event_type)

        if isinstance(start, datetime):
            start = start.isoformat()
        if isinstance(end, datetime):
            end = end.isoformat()

        _daterange = json.dumps(dict(date_range={'lower': start or '', 'upper': end or ''}))
        events = asyncio.run(self.async_erc_lient.get_events(event_type=event_type,
                                                             filter=_daterange, page_size=page_size))
        df = pd.DataFrame(chain.from_iterable(events))
        if df.empty:
            return gp.GeoDataFrame(columns=self.event_fieldnames)

        df = df.apply(axis=1, func=normalize_dict, colname='event_details')
        df = df.apply(axis=1, func=normalize_dict, colname='reported_by')
        df = self._coerce_columns_dtype(df, self.columns_of_dtype_list, str)
        return self.to_geodataframe(df)


class SubjectIO(EarthRanger):

    def download_subjects(self,
                          subjectgroup_name: str = None,
                          include_inactive: bool = False,
                          include_hidden: bool = True,
                          isvisible: bool = True,
                          flat: bool = True
                          ) -> pd.DataFrame:
        """Download subject in a group"""

        def to_hex(val):
            if val and not pd.isnull(val):
                return '#{:02X}{:02X}{:02X}'.format(*[int(i) for i in val.split(',')])
            return np.NaN

        if subjectgroup_name is None:
            subjects = self._er_client.get_subjects(include_inactive=include_inactive)
            df = pd.DataFrame(subjects)
        else:
            subjectgroups = self._er_client.get_subjectgroups(group_name=subjectgroup_name,
                                                              include_inactive=include_inactive,
                                                              include_hidden=include_hidden,
                                                              isvisible=isvisible,
                                                              flat=flat)
            arr = []
            for sg in subjectgroups:
                sg_df = pd.DataFrame([s for s in sg.get('subjects')])
                sg_df['subjectgroup_name'] = sg.get('name')
                arr.append(sg_df)
            df = pd.concat(arr)

        df = df.rename(columns={'id': 'subject_id', 'name': 'subject_name'})
        df = df.drop('content_type', axis=1)
        df.set_index('subject_id', inplace=True)
        df = df.apply(axis=1, func=normalize_dict, colname='additional')
        df['hex'] = df['rgb'].map(to_hex)
        return df

    def download_subject_sources(self, subject_id: UUID4):
        subject_source = self._er_client.get_subject_sources(subject_id)
        return pd.DataFrame(subject_source)

    def download_subject_observations(self,
                                      subject_id: UUID4,
                                      start: datetime = None,
                                      end: datetime = None,
                                      filter_flag: int = 0,
                                      include_details: bool = True,
                                      page_size: int = 2500):
        observations = self._er_client.get_subject_observations(subject_id=subject_id,
                                                                start=start,
                                                                end=end,
                                                                filter_flag=filter_flag,
                                                                include_details=include_details,
                                                                page_size=page_size)
        return pd.DataFrame(observations)


class SourceIO(EarthRanger):

    def download_sources(self, sources=None):
        if sources is not None:
            sources = asyncio.run(self.async_erc_lient.get_sources(sources))
            df = pd.DataFrame(chain.from_iterable(sources))
        else:
            sources = self._er_client._get('sources')
            df = pd.DataFrame(sources.get('results'))

        df = df.rename(columns={'id': 'source_id'})
        df.set_index('source_id', inplace=True)
        return df

    def download_subjectsources(self,
                                subjects: typing.List[str] = None,
                                sources: typing.List[str] = None,
                                page_size: int = 250) -> pd.DataFrame:
        """
        Download SubjectSourceAssignment.

        Parameters
        ----------
        subjects: list[str], optional
            List of subjects ids (UUID)
        sources: list[str], optional
            List of sources ids (UUID)
        page_size: int, default 250
            Integer representing number of results from HTTP request.
        """

        if sources is None:
            sources = []
        if subjects is None:
            subjects = []

        subjects = ','.join(subjects)
        sources = ','.join(sources)

        subject_sources = asyncio.run(self.async_erc_lient.get_subjectsources(subjects=subjects,
                                                                              sources=sources,
                                                                              page_size=page_size))
        df = pd.DataFrame(chain.from_iterable(subject_sources))
        df = df.apply(axis=1, func=normalize_dict, colname='assigned_range')

        if not df.empty:
            df['subject_source_start'] = pd.to_datetime(df['lower'], errors='coerce')
            df['subject_source_end'] = pd.to_datetime(df['upper'], errors='coerce')
            df = df.rename(columns={'id': 'subject_source_id',
                                    'source': 'source_id',
                                    'subject': 'subject_id',
                                    'additional': 'subject_source_additional'})
            df.set_index('subject_source_id', inplace=True)

            # safely drop unwanted columns
            un = df.columns[df.columns.str.startswith('assigned_range_')]
            df.drop(un, axis=1, inplace=True)
        return df


class ObservationsIO(EarthRanger):

    # @exception_handler
    # def _post_observation(self, payload, sensor_type):
    #     self._er_client.post_sensor_observation(observation=payload, sensor_type=sensor_type)

    @property
    def observation_fieldnames(self):
        return ['id', 'location', 'recorded_at', 'additional', 'manufacturer_id']

    def _additional_data(self, row):
        non_er_columns = set(row.index).difference(self.observation_fieldnames)
        non_er_columns.discard('X')
        non_er_columns.discard('Y')

        obs_additional = {}
        for column in non_er_columns:
            val = row.get(column)
            if not np.all(pd.isnull(val)):
                obs_additional[column] = val

        obs_additional['externalguid'] = str(row.name)
        return obs_additional

    def upload_observations(self, df=None, sensor_type='generic', source_type='tracking-device'):
        def create_observation(row):
            longitude = row.get('X')
            latitude = row.get('Y')
            recorded_at = row.get('recorded_at')
            manufacturer_id = row.get('manufacturer_id')
            additiona = self._additional_data(row)

            try:
                observation = Observation(manufacturer_id=manufacturer_id,
                                          source_type=source_type,
                                          recorded_at=recorded_at,
                                          additional=additiona,
                                          location=Location(x=longitude, y=latitude)
                                          )

            except ValidationError as exc:
                logger.exception(exc)
            else:
                self._er_client.post_sensor_observation(observation=observation, sensor_type=sensor_type)
                return pd.Series(observation)

        return df.apply(create_observation, axis=1)

    def _get_subject_observations(self,
                                  subject,
                                  start, end,
                                  filter_flag,
                                  include_additional,
                                  include_subject_details,
                                  chunk_size,
                                  limit,
                                  timezone,
                                  count=None,
                                  ):
        try:
            logger.info(f"Querying observations for subject: {subject.get('subject_name')}")

            result = asyncio.run(self.async_erc_lient.get_subject_observations(
                subject_id=subject['subject_id'],
                start=start,
                end=end,
                filter_flag=filter_flag,
                include_details=include_additional,
                page_size=chunk_size,
                count=count,
                limit=limit
            ))
            result = chain.from_iterable(result)
            df = pd.DataFrame(result)

            if df.empty:
                return df

            df = df.rename(columns={'source': 'source_id', 'id': 'observation_id', 'recorded_at': 'fixtime'})

            # Parse the fixtime and created_at columns as datetime
            df['fixtime'] = pd.to_datetime(df['fixtime'], utc=timezone)
            df['created_at'] = pd.to_datetime(df['created_at'], utc=timezone)
            df = df.astype({'observation_details': str}, errors='ignore')

            # default subject column in observation df
            df['subject_id'] = subject.get('subject_id')

            if include_subject_details:
                # Add subject related info
                df['subject_name'] = subject.get('subject_name')
                df['subject_sex'] = subject.get('sex')
                df['subject_type'] = subject.get('subject_type')
                df['subject_subtype'] = subject.get('subject_subtype')
                df['region'] = subject.get('region')
                df['country'] = subject.get('country')

                primary_cols = ['observation_id', 'source_id', 'subject_id',
                                'subject_name', 'subject_type', 'subject_subtype',
                                'subject_sex', 'region', 'country', 'fixtime',
                                'created_at', 'location']
            else:
                primary_cols = ['observation_id', 'source_id', 'subject_id', 'fixtime', 'created_at', 'location']

            if include_additional:
                df = df.rename(columns={'observation_details': 'additional'})

            # re-order columns
            other_cols = [col for col in df.columns if col not in primary_cols]
            return df[primary_cols + other_cols]
        except AttributeError as exc:
            logger.exception(exc)

    def download_observations(self,
                              subjectgroup_name='',
                              include_inactive=True,
                              start=None,
                              end=None,
                              filter_flag=0,
                              include_additional=True,
                              include_subject_details=False,
                              include_source_details=False,
                              include_subject_source_details=False,
                              chunk_size=500,
                              timezone=pytz.UTC,
                              limit=100,
                              processes=None
                              ):
        """
             Passing None, returns everything
             Passing 0, filters out everything but rows with exclusion flag 0 (i.e, clean data)
             Passing 1, filters out everything but rows with exclusion flag 1 (i.e., manually filtered data)
             Passing 2, filters out everything but rows with exclusion flag 2 (i.e., automatically filtered data)
             Passing 3, filters out everything but rows with exclusion flag 2 or 1 (i.e., both manual and automatic filtered data)

             Maximum page_size per request is 4000 according to observation api.

             Arg: limit - limit amount of simultaneously opened connections; default to 100 &
             If you explicitly want not to have limits, pass 0.

             Arg: processes - number of worker processes to use.
             If processes is None then the number returned by os.cpu_count() is used.
        """
        subject_io = SubjectIO(self._er_client)
        subjects = subject_io.download_subjects(subjectgroup_name=subjectgroup_name, include_inactive=include_inactive)

        if subjects is None:
            raise EarthRangerException(f'The subjects dataframe for {subjectgroup_name} is null')

        # Assume UTC if no timezone is given
        if start is not None and tz_naive(start):
            start = start.replace(tzinfo=pytz.UTC)
        if end is not None and tz_naive(end):
            end = end.replace(tzinfo=pytz.UTC)

        frames = [sub for _, sub in subjects.reset_index().iterrows()]

        with multiprocessing.Manager() as manager:
            # Manager controls a server process which holds Python objects allows other processes to manipulate them.
            count = manager.list()
            obs_df = parallelize_df(frames, func=partial(self._get_subject_observations,
                                                         start=start, end=end,
                                                         filter_flag=filter_flag,
                                                         include_additional=include_additional,
                                                         include_subject_details=include_subject_details,
                                                         chunk_size=chunk_size,
                                                         count=count,
                                                         timezone=timezone,
                                                         limit=limit
                                                         ), processes=processes)

            count = sum(count)
            if count != obs_df.shape[0]:
                logger.warning(f"Partial Success: Only {obs_df.shape[0]} out of {count} were successfully downloaded.")

        if obs_df.empty:
            return gp.GeoDataFrame()

        obs_df.sort_values(by=['fixtime'], axis=0)

        if include_subject_source_details:
            source_io = SourceIO(self._er_client)
            subject_source_df = source_io.download_subjectsources(sources=obs_df.source_id.unique()).reset_index()
            subject_source_df = subject_source_df[['subject_source_id',
                                                   'source_id',
                                                   'subject_source_start',
                                                   'subject_source_end',
                                                   'subject_source_additional']]

            obs_df = pd.merge(subject_source_df, obs_df, on='source_id')

        if include_source_details:
            source_io = SourceIO(self._er_client)
            source_df = source_io.download_sources(obs_df.source_id.unique())
            source_df = source_df[['manufacturer_id',
                                   'model_name',
                                   'provider',
                                   'source_type']]
            obs_df = pd.merge(source_df, obs_df, left_index=True, right_on='source_id')

        obs_df = set_index_column(obs_df, 'observation_id')
        return self.to_geodataframe(obs_df)

    @staticmethod
    def multi_relocations(obs_df, filter_point_coords=None, max_speed_kmhr=7.0):
        if filter_point_coords is None:
            filter_point_coords = [[180, 90]]

        multi_relocs = movdata.base.MultiRelocations.from_observations(obs_df)

        junk_pnts_filter = movdata.base.RelocsCoordinateFilter(filter_point_coords=filter_point_coords)
        multi_relocs.apply_fix_filter(junk_pnts_filter)

        # and let's apply a speed filter to get rid of any point where the animal had to move faster than X to get
        # there from the previous position
        speed_filter = movdata.base.RelocsSpeedFilter(max_speed_kmhr=max_speed_kmhr)
        multi_relocs.apply_fix_filter(speed_filter)

        return multi_relocs

    def multi_trajectory(self, obs_df, filter_point_coords=None, max_speed_kmhr=8.0, max_time_secs=14400):
        multi_relocs = self.multi_relocations(obs_df, filter_point_coords, max_speed_kmhr)

        multi_trajs = movdata.base.MultiTrajectory(multi_relocs)
        traj_seg_filter = movdata.base.TrajSegFilter(max_speed_kmhr=max_speed_kmhr, max_time_secs=max_time_secs)
        multi_trajs = multi_trajs.apply_traj_filter(traj_seg_filter)
        return multi_trajs

    def relocation(self, obs_df, subject_id, filter_point_coords=None, max_speed_kmhr=7.0):
        obs_df = obs_df.loc[obs_df.subject_id == str(subject_id)]
        return self.multi_relocations(obs_df, filter_point_coords, max_speed_kmhr)

    def trajectory(self, obs_df, subject_id, filter_point_coords=None, max_speed_kmhr=7.0, max_time_secs=14400):
        obs_df = obs_df.loc[obs_df.subject_id == str(subject_id)]
        return self.multi_trajectory(obs_df, filter_point_coords, max_speed_kmhr, max_time_secs)
