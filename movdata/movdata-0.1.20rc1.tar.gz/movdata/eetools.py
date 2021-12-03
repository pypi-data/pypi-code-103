import datetime as dt
import pytz

import time
import json
import shapely
import geojson
import ee
import geopandas as gpd
import pandas as pd
import dask.dataframe as dd
# from signal import signal, SIGPIPE, SIG_DFL https://docs.python.org/3/library/signal.html#note-on-sigpipe

import logging
logger = logging.getLogger(__name__)

import os

ee_is_initialized = False

ee_initialization_expires = dt.datetime(1970, 1, 1, tzinfo=pytz.utc)
ee_initialization_ttl = dt.timedelta(seconds=86400)


def initialize_earthengine(key_dict):
    '''
    This takes a JSON key as a dict.
    :param key_dict:
    :return: a credentials object that can be used to initialize the earth engine library.
    '''
    global ee_is_initialized
    global ee_initialization_expires

    try:
        if ee_is_initialized and (dt.datetime.now(tz=pytz.utc) > ee_initialization_expires):
            logger.debug('Earth Engine has already been initialized.')
            return

        sac = ee.ServiceAccountCredentials(key_dict['client_email'], key_data=json.dumps(key_dict))
        ee.Initialize(credentials=sac)

    except Exception as e:
        logger.exception('Not able to initialize EarthEngine.')
        raise
    else:
        ee_is_initialized = True
        ee_initialization_expires = dt.datetime.now(tz=pytz.utc) + ee_initialization_ttl
        logger.debug('Earth Engine has been initialized.')


# useful stylizations
colourPalettes = {'precipitation': {'palette': ['00FFFF', '0000FF']}, }


def convert_millisecs_datetime(unix_time):
    # Define the UNIX Epoch start date
    epoch = dt.datetime(1970, 1, 1, 0, 0, 0)
    t = epoch + dt.timedelta(milliseconds=unix_time)
    return t


def convert_datetime_millisecs(input_time):
    epoch = dt.datetime(1970, 1, 1, 0, 0, 0) # Define the UNIX Epoch start date
    return int((input_time - epoch).total_seconds() * 1000)


def convertUnixTimeToDateTime(unixTime):
    t = dt.datetime.utcfromtimestamp(int(unixTime/1000))
    return t


def add_img_time(img):

    """ A function to add the date range of the image as one of its
    properties and the start and end values as new bands"""

    # unable to use the band rename() function here in Python whereas works in JS playground
    img = img.addBands(img.metadata('system:time_start'))
    img = img.addBands(img.metadata('system:time_end'))
    dr = ee.DateRange(ee.Date(img.get('system:time_start')),
                      ee.Date(img.get('system:time_end')))

    return img.set({'date_range': dr})


def fixes_to_featurecollection(fixes):

    """ A function to turn a relocations object into a GEE feature collection"""

    return ee.FeatureCollection([ee.Feature(ee.Geometry.Point(p.geopoint.X, p.geopoint.Y),
                                            {'fixtime': p.fixtime.replace(tzinfo=None), 'uuid': p.uuid})
                                 for p in fixes])


def gdf_to_featurecollection(gdf):

    feats = []
    for i, row in gdf.iterrows():
        ee_feat = ee.Feature(geojson_to_ee_geometry(shapely.geometry.mapping(row.geometry)), {'pdindex': row.name})
        feats.append(ee_feat)
    return ee.FeatureCollection(feats)


def geojson_to_ee_geometry(val):
    """
    A function to convert geojson to an ee.Geometry
    :param val: can either be a geojson formatted string or dict
    :return: ee.Geometry or None
    """
    result = None
    if isinstance(val, str):
        try:
            result = ee.Geometry(geojson.loads(val))
        except:
            logger.exception('Failed to read geojson from %s', val)
    elif isinstance(val, dict):
        result = ee.Geometry(val)

    return result


def geofile_to_gdf(geofile=''):
    """ Read a geofile into a geopandas dataframe. Supports formats used by fiona"""
    """ Note that there is an issue with Fiona such that if the encoding is not UTF-8 (e.g.,ANSI 1252)
    then the import will fail. The encoding is usually listed in a cpg file. If this happens simply delete
     the cpg file. The default for ArcGIS generated shapefiles is UTF-8"""
    return gpd.GeoDataFrame.from_file(geofile)


# Define a function that will extract image values from GEE.
def example_extract_ndvi_and_slope_data_function(feat):

    # NDVI
    ndvi_img = ee.ImageCollection('MODIS/MCD43A4_NDVI').select('NDVI').mean()  # get the mean NDVI value
    ndvi_reduce = ndvi_img.toArray().reduceRegion(ee.Reducer.toList(), feat.geometry(), 500.0)

    # Slope
    slope_reduce = ee.Algorithms.Terrain(ee.Image("USGS/SRTMGL1_003")). \
        select(['slope']).reduceRegion(ee.Reducer.toList(), feat.geometry(), 30.0)

    return {
        'Slope': slope_reduce,
        'NDVI': ndvi_reduce,
    }


def example_regional_albedo_anomaly_extract_function(feat):
    """
    :param feat: an earth engine feature
    :return: earth engine compute object
    """

    historical_start = '2010-01-01'
    start = '2015-01-01'
    end = '2020-11-01'
    scale = 5000

    img_coll = ee.ImageCollection('MODIS/006/MCD43C3').select('Albedo_BSA_vis')
    reference = img_coll.filterDate(historical_start, start).sort('system:time_start', False)
    ref_mean = reference.mean()

    '''
    Compute anomalies by subtracting the 2001-2010 mean from each image in a collection of 2011-2020 images.
    Copy the date metadata over to the computed anomaly images in the new collection.
    '''
    def tmp1(image):
        return image.subtract(ref_mean).set('system:time_start', image.get('system:time_start'))
        #reduceRegion(ee.Reducer.mean(), feat.geometry(), scale). \

    series = img_coll.filterDate(start, end).map(tmp1)

    series_reduce = series.toArray().reduceRegion(ee.Reducer.toList(), feat.geometry(), scale)

    # anomalySumImg = series.sum()

    # time0 = reference.first().get('system:time_start')
    # first = ee.List([ee.Image(0).set('system:time_start', time0).select([0], ['Albedo'])])
    #
    # '''This is a function to pass to Iterate(). As anomaly images are computed, add them to the list.'''
    #
    # def accumulate(image, inlist):
    #
    #     # Get the  latest cumulative anomaly image from the end of the list
    #     # with get(-1).Since the type of the list argument to the function is unknown, it needs to be cast to a List.
    #     # Since the return type of get() is unknown, cast it to Image.
    #     previous = ee.Image(ee.List(inlist).get(-1))
    #
    #     # Add the current anomaly to make a new cumulative anomaly image.
    #     added = image. \
    #         add(previous).set('system:time_start', image.get('system:time_start'))
    #
    #     # Return the list with the cumulative anomaly inserted.
    #     return ee.List(inlist).add(added)
    #
    # cumulative = ee.ImageCollection(ee.List(series.iterate(accumulate, first)))
    #
    # cumulative_reduce = cumulative.toArray().reduceRegion(ee.Reducer.mean(), feat.geometry(), scale)

    return feat.set({'img_vals': series_reduce})


def example_tracking_data_extract_data_function(feat):

    '''
     before_win: the amount of time in seconds to select before the fix's fixtime. Set to 0 for the fixtime only
     after_win: the amount of time in seconds to select after the fix's fixtime set to 0 for the fixtime
     limit: the number of images to select that are temporally close to the fixtime. Use zero for all images
     scale: analysis scale in meters
     img_coll: the image collection to use for the extraction
    '''

    before_win = 16 * 24 * 60 * 60
    after_win = 0
    limit = 1
    scale = 500.
    img_coll = ee.ImageCollection('MODIS/MCD43A4_NDVI').select('NDVI');


    fixtime = ee.Date(feat.get('fixtime'))
    t1 = fixtime.advance(-1 * before_win, 'second')
    t2 = fixtime.advance(after_win, 'second')

    # filter the image collection by geometry
    tmpColl = img_coll.filterDate(t1, t2)  # .filterBounds(feat.geometry())

    # calculate how far away in time the image time_start value is from the current fix's fixtime
    def temporal_proximity(img):
        # positive means img is before, negative means img is after
        temporal_dist = ee.Date(feat.get('fixtime')).difference(img.date(), 'second').abs()
        img = img.set({'temporal_dist': temporal_dist,})
        return img

    # Attempt 1 to filter based on date range
    # Only include images whose date range intersects the date range of the feature
    # tmpColl = ee.ImageCollection(ee.Algorithms.If(temporal_intersect,
    #                                               tmpColl.filter(ee.Filter.eq('temporal_intersects', True)),
    #                                               tmpColl))

    # Attempt 2 to filter based on date range
    # tmpColl = ee.ImageCollection(ee.Algorithms.If(temporal_intersect,
    #                                               tmpColl.filter(
    #                                               ee.Filter.dateRangeContains('date_range', fixtime)), tmpColl))

    tmpColl = tmpColl.map(temporal_proximity).sort('temporal_dist', True).limit(limit)

    # Reduce
    tmp_reduce = tmpColl.toArray().reduceRegion(ee.Reducer.toList(), feat.geometry(), scale)

    return feat.set({'img_vals': tmp_reduce})


def parallelize_dataframe(df, func, n_cores=4):
    """ Input needs to be a plain pandas dataframe with a lat and lon column since Dask  
    can't interpret the Geometry column """

    # Using dask
    def dask_func(df1):
        gdf = gpd.GeoDataFrame(df1, geometry=gpd.points_from_xy(df1.lon, df1.lat), crs="EPSG:4326")
        return extract_img_values(gdf=gdf, img_calc=func, chunk_size=2000)

    ddf = dd.from_pandas(df, npartitions=n_cores)
    result = ddf.map_partitions(dask_func).compute()

    return result


def extract_img_values(gdf=None, img_calc=None, chunk_size=2000):
    """
    A function to run an image extraction function for each spatial geometry available in a geopandas dataframe

    :param gdf: a geopandas dataframe. The 'geometry' column can be any type pf geometry (point/line/polygon)
    :param img_calc: a function that will be used to extract image values intersecting the spatial geometry
    """

    def map_features(feat):
        return feat.set({img_calc.__name__: img_calc(feat)})

    results = dict()

    for i in range(0, len(gdf.index), chunk_size):
        try:
            success = False
            logger.info('Analyzing features: ' + str(i) + ' to ' + str(i + chunk_size - 1))
            chunk = gdf[i:i + chunk_size]

            # Build the relocations into a GEE feature collection
            feat_coll = gdf_to_featurecollection(chunk)
            while not success:
                try:
                    # Run the map function over all features
                    result = feat_coll.map(map_features, True).getInfo()

                    # Get the results for each image calculation
                    for f in result.get('features'):
                        results[f.get('properties').get('pdindex')] = \
                            f.get('properties').get(img_calc.__name__, None)
                    success = True

                except Exception as ex:
                    logger.error(str(ex))
                    logger.info('Re-trying in 5 seconds...')
                    time.sleep(5)  # Pause for 5 seconds before trying again
        except Exception as ex:
            logger.error(str(ex))

    if results:
        # Convert the results into a dataframe
        results = pd.DataFrame.from_dict(data=results, orient='index')
    else:
        results = None

    return results


# ------------------------- todo: eventually deprecate everything below ----------------------------------------------------------


def extract_temporal_img_values(fixes=None, img_coll=None, calc_name='gee_calc',
                                before_win=16*24*60*60, after_win=0, limit=1,  # temporal_intersect=True,
                                scale=500.0, chunk_size=20):

    """
    A function to filter the image collection to just those images that either intersect
    the fixtime daterange, or are the closest temporally, and intersect the geometry of the
     feature and then extract the image pixel values.

    fixes: a list of fix objects
    img_coll: the GEE image collection
    calc_name: the name to give this particular calculation. It will be the key to use to look up results in the
    fix's gee_result dictionary
    before_win: the amount of time in seconds to select before the fix's fixtime. Set to 0 for the fixtime only
    after_win: the amount of time in seconds to select after the fix's fixtime set to 0 for the fixtime
    nearest: the number of images to select that are temporally close to the fixtime. Use zero for all images
    temporal_intersect: require that the image's daterange intersects with the fixe's daterange
    scale: the pixel size in meters at which to resample the imagery
    chunk_size: the number of features that should be processed at once within GEE. This helps limiting memory errors
    """

    # Exit if the fixes list are null or empty
    if (fixes is None) or (fixes == []):
        return

    # Add date ranges to all the images in the collection
    img_coll = img_coll.map(add_img_time)

    # Define the function to map over each feature
    def map_features(feat):

        fixtime = ee.Date(feat.get('fixtime'))
        t1 = fixtime.advance(-1 * before_win, 'second')
        t2 = fixtime.advance(after_win, 'second')
        feat_dr = ee.DateRange(t1, t2)

        # filter the image collection by geometry
        # tmpColl = img_coll.filterBounds(feat.geometry())
        tmpColl = img_coll.filterDate(t1, t2)  # .filterBounds(feat.geometry())


        # calculate how far away in time the image time_start value is from the current fix's fixtime
        # and whether the image timespan intersects the fix's designated time window
        def temporal_proximity(img):
            # positive means img is before, negative means img is after
            temporal_dist = ee.Date(feat.get('fixtime')).difference(img.date(), 'second').abs()
            # temporal_intersects = feat_dr.intersects(img.get('date_range'))
            # intersects_val = ee.Algorithms.If(temporal_intersects, ee.Number(1), ee.Number(0))
            img = img.set({'temporal_dist': temporal_dist,
                           # 'temporal_intersects': temporal_intersects
                           })
            # img = img.addBands([img.metadata('temporal_dist'), img.metadata('intersects_val')])
            return img

        # Attempt 1 to filter based on date range
        # Only include images whose date range intersects the date range of the feature
        # tmpColl = ee.ImageCollection(ee.Algorithms.If(temporal_intersect,
        #                                               tmpColl.filter(ee.Filter.eq('temporal_intersects', True)),
        #                                               tmpColl))

        # Attempt 2 to filter based on date range
        # tmpColl = ee.ImageCollection(ee.Algorithms.If(temporal_intersect,
        #                                               tmpColl.filter(
        #                                               ee.Filter.dateRangeContains('date_range', fixtime)), tmpColl))

        tmpColl = tmpColl.map(temporal_proximity).sort('temporal_dist', True).limit(limit)

        # Reduce
        tmp_reduce = tmpColl.toArray().reduceRegion(ee.Reducer.toList(), feat.geometry(), scale)

        return feat.set({'img_vals': tmp_reduce})

    for i in range(0, len(fixes), chunk_size):
        try:
            print('Analyzing features: ', str(i), ' to ', str(i + chunk_size-1))
            chunk = fixes[i:i + chunk_size]

            # Build the relocations object into a GEE feature collection
            feat_coll = fixes_to_featurecollection(chunk)

            # success = False
            # while success is False:
            #     # The while loop lets us try over if the GEE servers didn't respond and we get a server timeout error.
            #     # Because of lazy execution the servers may not be finished running a calc but the next time you
            #     # try the result is ready.
            #     # ToDo: figure out how to discern between a result not ready error and some other error type


            # Run the map function over all features
            result = feat_coll.map(map_features).getInfo()
            # success = True

            # print(result.get('features'))

            # Create a dictionary using the fix ID values as the key:
            tmp_results = dict()

            for feat in result.get('features'):
                img_array = feat.get('properties').get('img_vals').get('array', None)
                if img_array:
                    tmp_results[feat.get('properties').get('uuid')] = img_array[0]

            # Set the results for each input fix
            for fix in chunk:
                fix.additional_data[calc_name] = tmp_results.get(fix.uuid)
                # print(fix.uuid, fix.properties[calc_name])

        except Exception as ex:
            print(ex)
            # print('Re-trying in 5 seconds...')
            # time.sleep(5)  # Pause for 5 seconds before trying again


# In use by DAS_analyzers
# ToDO: have changed this from relocs to fixes in the params - need to update DAS
# ToDo: have updated from calculating the mean to returning the raw output from EE - need to update DAS
def extract_point_values_from_image(fixes, img_name='', band_name='b1', scale=500.0):
    """ A function to extract values from an image at relocations """

    # Exit if the relocs object is null
    if fixes is None:
        return

    # Build the relocations into a GEE feature collection
    feat_coll = fixes_to_featurecollection(fixes)

    try:
        img = ee.Image(img_name)

        # dictionary result of the reduction
        result = img.reduceRegion(ee.Reducer.toList(), feat_coll.geometry(), scale).getInfo()
        # ToDO: how to link back to original feature ID?
        return result

        # if result is not None:
        #     raw_vals = result.get(band_name)
        #     if raw_vals is not None:
        #         return np.mean(raw_vals)
    except Exception as ex:
        print(ex)
        return


def extract_point_values_from_image2(fixes=None, ee_img=None, calc_name='gee_calc', scale=500.0, chunk_size=500):
    """ A function to extract values from an image at relocations """

    # Exit if the relocs object is null
    if fixes is None:
        return

    # Build the relocations into a GEE feature collection
    feat_coll = fixes_to_featurecollection(fixes)

    def map_features(feat):

        # Reduce
        tmp_reduce = ee_img.reduceRegion(ee.Reducer.toList(), feat.geometry(), scale)
        return feat.set({'img_val': tmp_reduce})


    for i in range(0, len(fixes), chunk_size):
        try:
            print('Analyzing features: ', str(i), ' to ', str(i + chunk_size-1))
            chunk = fixes[i:i + chunk_size]

            # Build the relocations object into a GEE feature collection
            feat_coll = fixes_to_featurecollection(chunk)

            # Run the map function over all features
            result = feat_coll.map(map_features).getInfo()
            # success = True

            # print(result.get('features'))

            # Create a dictionary using the fix ID values as the key:
            tmp_results = dict()

            for feat in result.get('features'):
                img_val = feat.get('properties').get('img_val')
                if img_val:
                    tmp_results[feat.get('properties').get('uuid')] = img_val

            # Set the results for each input fix
            for fix in chunk:
                fix.additional_data[calc_name] = tmp_results.get(fix.uuid)

        except Exception as ex:
            print(ex)
            return


def ReduceRegionByDatetimes(image_stack,
                            region,
                            region_scale,
                            ee_region_reducer_type,
                            ee_stack_reducer_type,
                            band_name,
                            datetimes=[]):

    """A function to perform a series of image stack reductions on the chosen band
     within the given region and for the given datetime tuples"""

    # Get the GPM dataset
    imgColl = ee.ImageCollection(image_stack).select(band_name).sort('system:time_start', False)

    # Convert the datetime tuples into a feature collection
    featColl = ee.FeatureCollection([ee.Feature(None, {'startDate': x[0], 'endDate': x[1]}) for x in datetimes])

    def mapFunc(feat):
        reduc = imgColl.filterDate(feat.get('startDate'), feat.get('endDate')).reduce(
            ee_stack_reducer_type).reduceRegion(ee_region_reducer_type, region.geometry(), region_scale)
        return feat.set({'reduceVal': reduc})

    return [(convert_millisecs_datetime(x.get('properties').get('startDate').get('value')),
             x.get('properties').get('reduceVal').get(band_name + '_' + ee_stack_reducer_type))
            for x in featColl.map(mapFunc).getInfo()['features']]
