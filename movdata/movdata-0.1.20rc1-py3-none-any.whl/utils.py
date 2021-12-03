import math
import os
from osgeo import ogr
from osgeo import osr
import random
import rasterio
from rasterio.mask import mask
import geopandas as gpd
import pyproj
from shapely.ops import transform
from shapely.geometry import LineString, Point



def km_to_degrees(km):
    """Quick and dirty conversion from kilometers to degrees"""
    rads = km / 6371.0
    return rads*180.0/math.pi
    #return math.degrees(rads)



def degrees_to_km(degrees):
    rads = math.radians(degrees)
    return rads * 6371.0


def rect_coord_geometry(center=None, side_len_km=1.0, srs=None):

    if srs is None:
        # create the spatial reference, WGS84
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)

    def rect_from_center(xc, yc, length_km):
        """ Generate rectangle corner coordinates based on the side length and center point """
        s = km_to_degrees(length_km / 2)
        p1 = (xc - s, yc + s)
        p2 = (xc - s, yc - s)
        p3 = (xc + s, yc - s)
        p4 = (xc + s, yc + s)
        return p1, p2, p3, p4

    # Create ring
    ring = ogr.Geometry(ogr.wkbLinearRing)

    for pt in rect_from_center(xc=center[0], yc=center[1], length_km=side_len_km):
        ring.AddPoint(pt[0], pt[1])

    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AssignSpatialReference(srs)
    poly.AddGeometry(ring)

    return poly


def generate_AOI_shapefile(AOI_center_coords=None, side_len_km=1.0,
                           output_location='', output_name='AOI_sites.shp'):
    """Create an output shapefile with equal sized AOI rectangle polyons
     based on the input AOI_center_coords.
    AOI_center_coords are lon/lat pairs"""

    # set up the shapefile driver
    driver = ogr.GetDriverByName("ESRI Shapefile")

    # create the data source
    data_source = driver.CreateDataSource(os.path.join(output_location, output_name))

    # create the spatial reference, WGS84
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    # create the layer
    layer = data_source.CreateLayer("sites", srs, ogr.wkbPolygon)

    # Create fields
    field_name = ogr.FieldDefn("Name", ogr.OFTString)
    field_name.SetWidth(24)
    layer.CreateField(field_name)

    for i, pnt in enumerate(AOI_center_coords):
        try:
            # create the feature
            feature = ogr.Feature(layer.GetLayerDefn())

            # Set the attributes using the values from the delimited text file
            feature.SetField("Name", 'Sample Site ' + str(i))

            aoi_geo = rect_coord_geometry(center=pnt, side_len_km=side_len_km)

            # Create the point from the Well Known Txt
            shp = ogr.CreateGeometryFromWkt(aoi_geo.ExportToWkt())

            # Set the feature geometry using the point
            feature.SetGeometry(shp)

            # Create the feature in the layer (shapefile)
            layer.CreateFeature(feature)

        except:
            print('An error occurred')
            pass


def assess_containment(geopoint=None, regions=None):
    """Pass back an array of all the regions IDs that contain the given geopoint"""
    containment = []

    if geopoint is not None:
        if regions is None:
            return []

        for region in regions:
            if type(region) is SpatialFeature:
                contains = region.ogr_geometry.Contains(geopoint.ogr_geometry)
                if contains is True:
                    containment.append(region.unique_id)

    return containment


def generate_csr_points_region(region=None, num=1000):

    # check if the region is a Region object
    if type(region) is not Region:
        raise Exception('Input polygon is not of type movdata.base.Region')

    poly = region.ogr_geometry

    env = poly.GetEnvelope()
    x_min, x_max, y_min, y_max = env[0], env[1], env[2], env[3]

    list_of_points = []
    counter = 0
    while counter < num:
        pnt = ogr.Geometry(type=ogr.wkbPoint)
        pnt.AddPoint(random.uniform(x_min, x_max), random.uniform(y_min, y_max), 0.)
        pnt.AssignSpatialReference(SRS.WGS84())

        if poly.Contains(pnt):
            list_of_points.append(pnt)
            counter += 1
    return list_of_points


def habiba_trajectory():
    """Create a trajectory based on two weeks of movement of the elephant Habiba in Samburu National Reserve"""

    datafile = r'../examples/sample_data/habiba.csv'
    movdata = pd.read_csv(datafile, sep=',', header=0)
    movdata['Fixtime'] = pd.to_datetime(movdata['Fixtime'], format="%Y-%m-%d %H:%M:%S", utc=True)
    # Create a trajectory from the dataframe
    relocs = Relocations([Fix(GeoPoint(i.Longitude, i.Latitude, 0), i.Fixtime) for i in movdata.itertuples()], 'Habiba')
    traj = Trajectory(relocs)
    return traj


def samburu_point():
    """Create a random OGR point in Samburu National Reserve, Kenya"""
    point = ogr.Geometry(type=ogr.wkbPoint)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    point.AddPoint(x=37.52, y=0.58, z=0)
    point.AssignSpatialReference(srs)
    return point


def ewaso_river():
    """Create the OGR geometry for the Ewaso Nyiro river flowing through Samburu National Reserve, Kenya"""
    shapefile = r'../examples/Data/spatial_data/EwasoNyiroRiver.shp'
    driver = ogr.GetDriverByName("ESRI Shapefile")
    data_source = driver.Open(shapefile, 0)
    layer = data_source.GetLayer()
    geoms = []
    for feature in layer:
        geom = feature.GetGeometryRef()
        geoms.append(geom)
    return geoms[0]


def samburu_polygon():
    """Create a random polygon based on a random point in Samburu National Reserve, Kenya"""
    pnt = samburu_point()
    return rect_coord_geometry(center=(pnt.GetX(), pnt.GetY()), side_len_km=km_to_degrees(10.0))


def reduce_region(gdf=None, rasters=None, reduce_func=None):
    """
    A function to apply the reduce_func to the values of the pixels within each of the rasters for every
    shape within the input geopandas dataframe 'geometry' column
    :param gdf: geopandas dataframe
    :param rasters: a list of raster names
    :return: None
    """
    # define valid region reduce functions
    #reduce_funcs = [np.mean, np.sum, np.min, np.max, np.percentile, np.count_nonzero]

    try:
        # check for correct input types
        assert type(gdf) is gpd.geodataframe.GeoDataFrame
        assert type(rasters) is list
        #assert reduce_func in reduce_funcs  # ToDo: better way to test the type of reduce function?

        def tmp(r):
            result = dict()
            for raster_name in rasters:
                print('Processing: ', raster_name, ' and ', r.name)
                try:
                    with rasterio.open(raster_name) as src:
                        # src is an ndarray with dimensions (num_band, num_rows, num_cols)
                        # out_img is a masked ndarray that uses the same NoData value as
                        # the input raster (defaults to 0)
                        project = pyproj.Transformer.from_crs(gdf.crs, src.crs, always_xy=True).transform
                        proj_shp = transform(project, r['geometry'])
                        out_img, out_transform = mask(src, [proj_shp], filled=False)

                        # apply the input reduce_func to the masked ndarray.
                        # Note that this also performs a stack reduce
                        # if there is more than one band
                        result[raster_name] = reduce_func(out_img.compressed())

                except Exception as ex:
                    print(ex)
            return result

        gdf['reduce_region'] = gdf.apply(tmp, axis=1)

    except Exception as ex:
        print(ex)