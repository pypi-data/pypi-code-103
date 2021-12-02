#!/usr/bin/env python3


class DbColumn:
    separator = '.'

    att = 'att'
    confidence = 'confidence'
    datapoint = 'data_point'
    datatype = 'data_type'
    dataquality = 'data_quality'
    day = 'day'
    density = 'density'
    eid = 'eid'
    entrance = 'entrance'
    flow = 'flow'
    flowin = 'flow_in'
    flowout = 'flow_out'
    fluidity = 'fluidity'
    fromtraveltime = 'from_travel_time'
    fromroad = 'from_road'
    fromturnratio = 'from_turn_ratio'
    fromzonepoint = 'from_zone_point'
    geom = 'geom'
    id = 'id'
    indicator = 'indicator'
    nbike = 'nbike'
    nbus = 'nbus'
    ncar = 'ncar'
    networkdataquality = 'network_data_quality'
    networkindicator = 'network_indicator'
    occupancy = 'occupancy'
    prediction = 'prediction'
    predictionpoint = 'prediction_point'
    ratio = 'ratio'
    road = 'road'
    roadcenter = 'road_center'
    samples = 'samples'
    sampletime = 'sample_time'
    timestamp = 'timestamp'
    totaltraveldistance = 'total_travel_distance'
    speed = 'speed'
    totraveltime = 'to_travel_time'
    toroad = 'to_road'
    toturnratio = 'to_turn_ratio'
    tozonepoint = 'to_zone_point'
    traveltime = 'travel_time'
    validfrom = 'valid_from'
    validto = 'valid_to'
    webatt = 'web_att'


class DbTable:
    datapoint = 'data_point'
    datapointdataquality = 'data_point_data_quality'
    datapointindicator = 'data_point_indicator'
    datatype = 'data_type'
    networkdataquality = 'network_data_quality'
    networkindicator = 'network_indicator'
    prediction = 'prediction'
    predictionpoint = 'prediction_point'
    road = 'road'
    roadcenter = 'road_center'
    roaddatapoint = 'road_data_point'
    roaddataquality = 'road_data_quality'
    roaddensity = 'road_density'
    roadfluidity = 'road_fluidity'
    roadpartition = 'road_partition'
    roadvehicle = 'road_vehicle'
    turnratio = 'turn_ratio'
    zonepoint = 'zone_point'
    zonepointtraveltime = 'zone_point_travel_time'


class Message:
    data = 'data'
    format = 'format'
    timestamp = 'timestamp'
    kind = 'kind'


class MessageData(DbColumn):
    csvseparator = ';'
    csvquote = '\''
    encoding = 'utf-8'
    separator = '_'

    status = 'status'

    late = -2
    nan = -1

    hendday = 21
    hstartday = 6

    avg = 'avg'
    max = 'max'
    min = 'min'
    raw = 'raw'


class AttId(DbColumn):
    centerxy = 'centerxy'
    centroid = 'centroid'
    datapointseids = 'datapoints'
    datatypeeid = 'datatypeeid'
    ffspeed = 'ffspeed'
    fow = 'fow'
    frc = 'frc'
    fromno = 'fromno'
    geomxy = 'geomxy'
    length = 'length'
    mainroad = 'mainroad'
    maxspeed = 'maxspeed'
    name = 'name'
    nlanes = 'nlanes'
    no = 'no'
    roads = 'roads'
    tono = 'tono'
    x = 'x'
    y = 'y'
    zone = 'zone'


class MessageFormat:
    json = 'json'
    csv = 'csv'


class MessageKind:
    separator = '-'

    mainprefix = 'gtlv'

    past = 'past'

    dataquality = 'dataquality'
    datapoint = 'datapoint'
    datatype = 'datatype'
    indicator = 'indicator'
    mappingroadsdatapoints = 'mappingroadsdatapoints'
    network = 'network'
    partitions = 'partitions'
    prediction = 'prediction'
    predictionpoint = 'predictionpoint'
    traveltime = 'traveltime'
    turnratio = 'turnratio'
    vehicles = 'vehicles'

    density = 'density'
    fluidity = 'fluidity'
    karrusrd = 'karrusrd'
    metropme = 'metropme'
    road = 'road'
    roadcenter = 'roadcenter'
    tomtomfcd = 'tomtomfcd'
    zonepoint = 'zonepoint'


class RequestParam(MessageKind):
    separator = ','

    internalflag = 'internal'

    eid = 'eid'
    fields = 'fields'
    fromdatetime = 'fromdatetime'
    frompoint = 'frompoint'
    fromroad = 'fromroad'
    period = 'period'
    sampling = 'sampling'
    todatetime = 'todatetime'
    topoint = 'topoint'
    toroad = 'toroad'
    window = 'window'
    within = 'within'

    day = 'day'
    month = 'month'
    week = 'week'


class RequestPath(MessageKind):
    separator = '/'

    confidence = 'confidence'
    flow = 'flow'
    occupancy = 'occupancy'
    speed = 'speed'
    flowin = 'flow_in'
    flowout = 'flow_out'
    totaltraveldistance = 'total_travel_distance'


class NetworkObjId:
    datapointsroadsmap = 'datapointsroadsmap'
    frcroadsmap = 'frcroadsmap'
    lonlatnodesmatrix = 'lonlatnodesmatrix'
    mainclustersgeom = 'mainclustersgeom'
    newdpmappings = 'newdpmappings'
    newzonemappings = 'newzonemappings'
    omiteddatapoints = 'omiteddatapoints'
    roadclustermap = 'roadclustermap'
    roadsdatamap = 'roadsdatamap'
    roadsffspeedmap = 'roadsffspeedmap'
    roadszonesmap = 'roadszonesmap'
    voronoiroadmap = 'voronoiroadmap'
    zonesdatamap = 'zonesdatamap'
