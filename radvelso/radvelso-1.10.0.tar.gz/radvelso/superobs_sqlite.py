#!/usr/bin/python3

import os
import tempfile
import argparse 
import numpy as np
import sqlite3
import time 
import glob
import dask
import dask.distributed
from dask.delayed import delayed
import copy
import sys
import datetime
import radvelso


def find_schema(schema):
  """find schema file contained in the Python package

   args: 
     schema: the schema we are looking for

   output:
     full path of schema file that was found
  """

  #full path of radvelso module
  radvelso_dir = os.path.dirname(radvelso.__file__)
  #root path of radvelso package (one dir up from radvelso module)
  package_dir = os.path.dirname(radvelso_dir)
  #full path of schema we are looking for
  schema_file = f'{package_dir}/schema/{schema}'

  if not os.path.isfile(schema_file):
    raise ValueError(f'schema_file: {schema_file} does not exist')

  return schema_file


def make_input_ppi_db(filein, 
                      stn, 
                      this_time, 
                      nominal_ppi_elevation, 
                      min_range_in_ppi, 
                      max_range_in_ppi):

  """make a separate db for one PPI

   This db is saved in memory and allows quich search of averaging boxes

   args: 
     filein                 : input sqlite file containing many radars and times
     stn                    : radar for this one volume scan
     this_time              : end time of this one volume san
     nominal_ppi_elevation  : nominal elevation
     min_range_in_ppi       : min range in PPI
     max_range_in_ppi       : max range in PPI

   output: 
     sqlite connection to the created db

  """

  
  # https://tools.ietf.org/html/rfc3986  Uniform Resource Identifier (URI)
  # The advantage of using a URI filename is that query parameters on the
  # URI can be used to control details of the newly created database connection in parallel
  conn_ppi_db = sqlite3.connect("file::memory:?cache=shared",uri=True)
  # off the journal
  conn_ppi_db.execute("""PRAGMA journal_mode=OFF;""")
  # SQLite continues without syncing as soon as it has handed data off to the operating system
  conn_ppi_db.execute("""PRAGMA synchronous=OFF;""")

  schema = find_schema('schema')
  with open(schema) as f:
    schema = f.read()
  conn_ppi_db.executescript(schema)
  # improve searches with index tables
  create_index_tables_elevation_azimuth(conn_ppi_db)
  create_index_tables_idobs_iddata(conn_ppi_db)
  # attach database
  conn_ppi_db.execute("ATTACH DATABASE ? AS db_all", (filein,)) 
  #select headers in desirec PPI
  order_sql = """ INSERT into header 
                  SELECT 
                    * 
                  FROM
                    db_all.header 
                  WHERE
                    id_stn = ?   
                    and time = ? 
                    and round(nominal_ppi_elevation, 1) = ? ;"""
  conn_ppi_db.execute(order_sql, (stn, this_time, nominal_ppi_elevation))
  #select associated data entries
  order_sql = """ INSERT into data 
                  SELECT
                    * 
                  FROM
                    db_all.data 
                  WHERE
                    id_obs in (SELECT
                                 id_obs 
                               FROM
                                 header  );"""
  conn_ppi_db.execute(order_sql)

  conn_ppi_db.commit()

  return conn_ppi_db


def num_obs_in_ppi(conn_ppi_db, 
                   min_range_in_ppi, 
                   max_range_in_ppi):
  """count total number of observations in PPI
  
  args:
    conn_ppi_db      : connexion to sqlite db for this PPI
    min_range_in_ppi : min range in PPI
    max_range_in_ppi : max range in PPI

  output:
    number of observations in PPI
  """

  order_sql= """ SELECT
                   count(*)
                 FROM
                   data 
                 WHERE
                   range >= ? 
                   and range <= ?"""
  
  conn_ppi_db.row_factory =sqlite3.Row
  cursor = conn_ppi_db.cursor()
  cursor.execute( order_sql,(min_range_in_ppi, max_range_in_ppi))
  result = cursor.fetchone()
  number_obs_ppi   = result[0]

  return number_obs_ppi
    

def average_boxes(conn_filememory,
                  id_obs,
                  id_data,
                  azimuth,
                  half_delta_range,
                  range_bin_centers, 
                  half_delta_azimuth):
  """ Average input data found in range and azimuth "box"
     
  args:
    conn_filememory      : connexcion to output file (and attached ppi_db)
    id_obs               : id_obs for this ray
    id_data              : id_data for this averaging box
    azimuth              : center azimuth of averaging box
    half_delta_range     : half of the delta_range for this averaging box
    range_bin_centers    : range center for this averaging box 
    half_delta_azimuth   : half of azimuthal span of averaging box

  output:
    number of observations used in this average
  """

  # bounds of the box
  right_azimuth   = azimuth+half_delta_azimuth
  left_azimuth    = azimuth-half_delta_azimuth
  range_box_start = range_bin_centers-half_delta_range
  range_box_end   = range_bin_centers+half_delta_range

  # Condition changes for azimuth centered at zero 
  condition="and"
  if (left_azimuth<0): 
    left_azimuth=360.-half_delta_azimuth  
    condition="or"
  
  order_sql = """ SELECT 
                    count(*),
                    sum(center_elevation)
                  FROM
                    db_ppi.data natural join db_ppi.header 
                  WHERE
                    range >= ? 
                    and range < ? 
                    and id_obs in(
                      SELECT 
                        id_obs 
                      FROM 
                        db_ppi.header 
                      WHERE 
                        center_azimuth >= ? 
                        """ + condition + """ center_azimuth < ?
                    ) """

  cursor = conn_filememory.execute(order_sql, (range_box_start, range_box_end, left_azimuth, right_azimuth))
  result = cursor.fetchone()
  # get Num observation for thos box
  number_obs_box=result[0]
  # get sum elevation for this box
  sum_elevation = result[1]

  if number_obs_box == 0: 

    # no observations in averaging box, we exit here  
    return 0, 0

  else:

    # Write the found values of avg (obsvalue) (among others) in the box
    order_sql = """INSERT into data(
                     id_obs, 
                     range, 
                     obsvalue, 
                     half_delta_azimuth, 
                     half_delta_range, 
                     id_data, 
                     quality_index,
                     number_obs
                     ) 
                   SELECT
                     ?, ?,
                     avg(obsvalue), 
                     ?, ?, ?,
                     avg(quality_index), ?
                   FROM
                     db_ppi.data 
                   WHERE
                     range >= ? 
                     and range < ? 
                     and id_obs in(
                       SELECT 
                         id_obs 
                       FROM 
                         db_ppi.header 
                       WHERE 
                         center_azimuth >= ? """+condition+""" center_azimuth < ?
                     )"""
    
    conn_filememory.execute(order_sql, (id_obs, range_bin_centers, 
                                     half_delta_azimuth, half_delta_range, id_data, number_obs_box,
                                     range_box_start, range_box_end, left_azimuth, right_azimuth,))


  return number_obs_box, sum_elevation


def create_header(conn_filememory, 
                  ray,        
                  avg_elevation,
                  id_obs):
  """ Create header entry

  A header is created matching a bunch of entries in data table

  args:
    conn_filememory  : connextion to  file in memory
    sample_header    : dictionary entry containing info from first header in ppi
    ray              : data structure of averaging ray        
    avg_elevation    : average elevation envountered along averaging ray 
    id_obs           : id_obs of radar beam
  
  output:
    Nothing
    header entry is written in output sqlite file

  """

  #get first header in PPI
  order_sql =  """ SELECT * FROM db_ppi.header """  
  conn_filememory.row_factory = sqlite3.Row 
  cursor = conn_filememory.cursor()
  cursor.execute( order_sql)
  sample_header = cursor.fetchone()

  #variables from the first header encountered
  #those will not change for a given PPI
  id_stn                = sample_header['id_stn']
  location              = sample_header['location']
  lat                   = sample_header['lat']
  lon                   = sample_header['lon']
  date                  = sample_header['date']
  time                  = sample_header['time']
  codtyp                = sample_header['codtyp']
  antenna_altitude      = sample_header['antenna_altitude']
  nyquist               = sample_header['nyquist']
  nominal_ppi_elevation = sample_header['nominal_ppi_elevation']
  time_start            = sample_header['time_start']
  time_end              = sample_header['time_end']
     
  #variables that depend on averaging parameters for this ray
  azimuth     = ray['azimuth']
  range_start = ray['min_range_in_ppi']
  range_end   = ray['max_range_in_ppi']

  #variables that depend on the data that was averaged for this ray
  # avg_elevation
  # time_start
  # time_end 

  order_sql ="""INSERT  into  header(
                  id_obs,id_stn, location, lat, lon, date, time, codtyp, 
                  antenna_altitude, nyquist, nominal_ppi_elevation,
                  center_azimuth, range_start, range_end,
                  center_elevation, time_start, time_end) 
                VALUES
                   ( ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) """

  conn_filememory.execute( order_sql,(id_obs, id_stn, location, lat, lon, date, time, codtyp,
                                   antenna_altitude, nyquist, nominal_ppi_elevation, 
                                   azimuth, range_start, range_end, 
                                   avg_elevation, time_start, time_end) )

def create_index_tables_elevation_azimuth(conn):
  """ Create index tables
  For elevation and azimuth  
  args:
    conn          : connextion to sqlite file
  output:
    Nothing
    index tables i sqlite file
 
  """

  order_sql ="""CREATE INDEX 
                  NOMINAL_PPI_ELEVATIONS 
                ON header (NOMINAL_PPI_ELEVATION);"""
  conn.execute(order_sql)

  order_sql ="""CREATE INDEX
                  CENTER_AZIMUTHS 
                ON header (CENTER_AZIMUTH);"""
  conn.execute(order_sql)

def create_index_tables_idobs_iddata(conn):
  """ Create index tables
  For id_obs and id_data
  args:
    conn          : connextion to sqlite file
  output:
    Nothing
    index tables i sqlite file

  """
  
  order_sql = """ CREATE INDEX
                    idx1
                  ON header(id_obs);"""
  conn.execute(order_sql)
  
  order_sql = """CREATE INDEX
                   idx2 
                 ON data(id_obs);"""
  conn.execute(order_sql)

  order_sql = """CREATE INDEX
                   idx3 
                 ON data(id_data);"""
  conn.execute(order_sql)

def create_info_midas_tables(filein,
                              conn_pathfileout, 
                              n_rays,        
                              delta_range,
                              ops_run_name):
  """ Create header entry

  A header is created matching a bunch of entries in data table

  args:
    filein        : input sqlite file with raw data
    conn_pathfileout  : connextion to output file
    n_rays        : number of rays 
    delta_range   : delta range of the boxes
    ops_run_name  : name of operational run
  output:
    Nothing
    info table entry is written in output sqlite file

  """

  conn_pathfileout.execute("""ATTACH DATABASE ? AS db_all""", (filein,) ) 

  # Info table
  order_sql ="""CREATE TABLE info( NAME, DESCRIPTION, UNIT );"""
  conn_pathfileout.execute( order_sql)
  order_sql =""" INSERT  into  info (
                   NAME, DESCRIPTION, UNIT) 
                 SELECT * 
                   from  db_all.info """
  conn_pathfileout.execute( order_sql)
  order_sql =""" UPDATE  info SET DESCRIPTION = REPLACE(DESCRIPTION,'OFF','ON') where name = 'SUPEROBBING';"""
  conn_pathfileout.execute( order_sql)
  order_sql =""" UPDATE  info SET DESCRIPTION = ? where name = 'SUPEROBBING_NUMBER_RAYS' ;"""
  conn_pathfileout.execute( order_sql, ( n_rays, ))
  order_sql =""" UPDATE  info SET DESCRIPTION = ? where name = 'SUPEROBBING_DELTA_RANGE' ;"""
  conn_pathfileout.execute( order_sql, (delta_range, ))

  # Resume table 
  order_sql ="""CREATE TABLE resume(date integer , time integer , run varchar(9));"""
  conn_pathfileout.execute( order_sql)
  YYYYMMDD = os.path.basename(filein)[:8]
  HH = os.path.basename(filein)[8:10]
  order_sql = """INSERT into resume values(?,?,?);"""
  conn_pathfileout.execute( order_sql, (YYYYMMDD, HH, ops_run_name,))
  
  # rdb4_schema table
  order_sql ="""CREATE TABLE rdb4_schema( schema  varchar(9) );"""
  conn_pathfileout.execute( order_sql)
  order_sql ="""INSERT into rdb4_schema values('radvel');"""
  conn_pathfileout.execute( order_sql)

  # commint and detach database
  conn_pathfileout.commit()
  conn_pathfileout.execute("DETACH DATABASE db_all")


def superobs(filein, 
             stn,
             this_datetime, 
             pathfileout,
             ray_list, 
             ops_run_name, 
             timer=False):

  """ Average  a volume scan
  
  This function takes in raw measurements in an sqlite file and 
  creates an average volume scan based on the content of the 
  provided averaging structure. 

  args:
    filein        : input sqlite file with raw data
    stn           : name of radar that generated the volume scan being processed
    this_datetime : valid date time of radar observation 
    pathfileout   : output averaging  sqlite file 
    ray_list      : averaging template containing info for how to average PPIs
    ops_run_name  : name of operational run 
    timer         : activation of time analysis, only the first PPI in a volume scan will be averaged

  output:
    This function outputs nothing
    However, the averaged data is put in a sqlite file with the same name
    as the original but with the suffix "_superobs" 

  """
  #zero padded string 020100
  hhmiss_pad =  this_datetime.strftime('%H%M%S') 
  #no zeros on left but still 0 if 000000
  hhmiss_nopad = str(int(hhmiss_pad))

  #figure out minimum and maximum ranges in averaged PPI
  n_rays = len(ray_list)
  min_range_in_ppi = 1.e9
  max_range_in_ppi  = 0.
  for this_ray in ray_list:
    min_range_in_ppi = np.amin([this_ray['min_range_in_ppi'], min_range_in_ppi])
    max_range_in_ppi = np.amax([this_ray['max_range_in_ppi'], max_range_in_ppi])


  #Prepare file in memory
  filememory=f'file:{filein}_{hhmiss_pad}_{stn}?mode=memory&cache=shared'
  print(f'Averaging volume scan for radar {stn} at time {hhmiss_pad} into {os.path.basename(filememory)}')
  conn_filememory = sqlite3.connect(filememory, uri=True, check_same_thread=False)
  # off the journal
  conn_filememory.execute("""PRAGMA journal_mode=OFF;""")
  # SQLite continues without syncing as soon as it has handed data off to the operating system
  conn_filememory.execute("""PRAGMA synchronous=OFF;""")

  schema = find_schema('schema')
  with open(schema) as f:
    schema = f.read( )
  conn_filememory.executescript(schema)
  # improve searches with index tables
  create_index_tables_idobs_iddata(conn_filememory)
  # Construct a new Generator with the default BitGenerator (PCG64).
  rng = np.random.default_rng()
  maxsize = sys.maxsize
  # maxsize = 9223372036854775807 from python -c 'import sys; print(sys.maxsize)'
  ids     = rng.integers(maxsize, size=2)
  id_data = ids[0].tolist()
  id_obs  = ids[1].tolist()
  #list of elevations in file for this radar at this time
  conn_elevation = sqlite3.connect(filein)
  order_sql = """ SELECT 
                    distinct nominal_ppi_elevation 
                  FROM
                    header 
                  WHERE
                    id_stn = ?
                    and time = ? 
                  ORDER BY 
                    1;"""
  nominal_ppi_elevations = [ np.round(elev[0],4) for elev in conn_elevation.execute(order_sql, (stn, hhmiss_nopad)).fetchall() ]
  conn_elevation.close()

  if timer : 
    nominal_ppi_elevations = nominal_ppi_elevations[0:1]
  for nominal_ppi_elevation in nominal_ppi_elevations:

    conn_ppi_db = make_input_ppi_db(filein, 
                                    stn, 
                                    hhmiss_nopad, 
                                    nominal_ppi_elevation, 
                                    min_range_in_ppi, 
                                    max_range_in_ppi)

    #temporarily attach ppi db to output file
    conn_filememory.execute('ATTACH DATABASE "file::memory:?cache=shared" AS db_ppi') 

    #iterate over rays of the averaged PPI
    number_obs_ppi = 0
    for ray in ray_list:    

      #variables that do not change for a given ray
      azimuth          = ray['azimuth']
      half_delta_range = ray['half_delta_range']

      # average boxes and write result in data table of filememory db (Memory)
      sum_elev_ray   = 0.
      number_obs_ray = 0
      for range_bin_center, half_delta_azimuth in zip(ray['range_bin_centers'], 
                                                      ray['half_delta_azimuth']):
             
        number_obs_box, sum_elev_box = average_boxes(conn_filememory,
                                                     id_obs,
                                                     id_data,
                                                     azimuth, 
                                                     half_delta_range,
                                                     range_bin_center,
                                                     half_delta_azimuth)
        if number_obs_box > 0:
          id_data = (rng.integers(maxsize, size=1))[0].tolist()

          sum_elev_ray   += sum_elev_box
          number_obs_ray += number_obs_box
      
      # if any data was found in ray, create header entry matching average bins
      # already entered in data table
      if number_obs_ray > 0:

        avg_elevation = sum_elev_ray / number_obs_ray

        create_header(conn_filememory, 
                      ray, 
                      avg_elevation,
                      id_obs)
        id_obs  = (rng.integers(maxsize, size=1))[0].tolist()
      
      #keep track of how many obs have been averagd in ppi
      number_obs_ppi += number_obs_ray

    # Test number of observations in source PPI vs num observation used in averaging boxes
    number_obs_in_source_ppi = num_obs_in_ppi(conn_ppi_db, 
                                              min_range_in_ppi, 
                                              max_range_in_ppi)

    if (number_obs_ppi != number_obs_in_source_ppi): 
      raise RuntimeError("""Error: number of observations in source ppi is different from number of obs used in average""")

    conn_filememory.commit()
    conn_filememory.execute("DETACH DATABASE db_ppi")
    conn_ppi_db.close()

  # Update flag, varno and vcoord_type
  conn_filememory.execute("UPDATE data SET flag=0, varno=21014, vcoord_type=7007")
  conn_filememory.commit()
  # Copy in a single sqlite file from memory (parallel)
  try:
      combine(pathfileout, filememory)
  except sqlite3.Error as error:
    print("Error while creating a single sqlite file:  {os.path.basename(filememory)}", error)
  # close connection 
  conn_filememory.close()


def combine(pathfileout, filememory):
 
   
  """ Creating a single sqlite file from multiple sqlite files
 
  args:
    pathfileout   : output averaging  sqlite file 
    filememory    : name of the sqlite file in memory to copy
  output:
    Nothing
    A sqlite file is made with all averaged volume scans
  """

  # write in output averaging  sqlite file 
  conn_pathfileout = sqlite3.connect(pathfileout, uri=True, isolation_level=None, timeout=999)
  # off the journal
  conn_pathfileout.execute("""PRAGMA journal_mode=OFF;""")
  # SQLite continues without syncing as soon as it has handed data off to the operating system
  conn_pathfileout.execute("""PRAGMA synchronous=OFF;""")
  # Wait to read and write until the next process finishes
  # attach the sqlite file in memory for one PPI
  conn_pathfileout.execute("ATTACH DATABASE ? AS this_avg_db;", (filememory,))
  order_sql = """ INSERT into header
                    SELECT
                     *
                    FROM  this_avg_db.header;"""
  conn_pathfileout.execute(order_sql) 
  order_sql = """ INSERT into data
                    SELECT
                      *
                    FROM  this_avg_db.data;"""
  conn_pathfileout.execute(order_sql)

  conn_pathfileout.commit()
  conn_pathfileout.execute(""" DETACH DATABASE this_avg_db """)


def collision_test(conn_pathfileout):
   
   """Check the collisiona and that the id_obs from the header have an associated properly to id_data.
 
   args:
    conn_pathfileout   : connection of  output averaging  sqlite file 
   output:
    Nothing

   """
   # distinct id_obs from header
   # count id_obs from header
   order_sql = """select 
                    count(distinct id_obs)
                  from header;"""
   cursor   = conn_pathfileout.cursor()
   cursor.execute(order_sql)
   result   = cursor.fetchone()
   distinct_id_obs_from_header = result[0]
   order_sql = """select 
                    count(id_obs)
                  from header;"""
   cursor   = conn_pathfileout.cursor()
   cursor.execute(order_sql)
   result   = cursor.fetchone()
   count_id_obs_from_header = result[0]
   
   # distinct id_obs from data
   # distinct id_data from data
   # count id_data from data
   order_sql = """select 
                    count(distinct id_obs)
                  from data;"""
   cursor   = conn_pathfileout.cursor()
   cursor.execute(order_sql)
   result   = cursor.fetchone()
   distinct_id_obs_from_data = result[0]
   order_sql = """select 
                    count(distinct id_data)
                  from data;"""
   cursor   = conn_pathfileout.cursor()
   cursor.execute(order_sql)
   result   = cursor.fetchone()

   distinct_id_data_from_data = result[0]
   order_sql = """select 
                    count(id_data)
                  from data;"""
   cursor   = conn_pathfileout.cursor()
   cursor.execute(order_sql)
   result   = cursor.fetchone()
   count_id_data_from_data = result[0]


   if (distinct_id_obs_from_header !=  distinct_id_obs_from_data): 
      raise RuntimeError("""Error: id_obs is not associated properly""")
   if (distinct_id_obs_from_header !=  count_id_obs_from_header): 
      raise RuntimeError("""Error: id_obs is in collision""")
   if (distinct_id_data_from_data  !=  count_id_data_from_data): 
      raise RuntimeError("""Error: id_data is in collision""")

def compute_average(center_time,
         window_width,
         desired_radar_list,
         infile_list, 
         pathout, 
         outfile_struc, 
         timing, 
         ops_run_name, 
         n_rays, 
         delta_range,
         n_cpus):
  """launch computation of average volums scans, possibly in parallel

  args:
    center_time  : datetime object,  center time of the assimilation window
    window_width : [hours] Width of the assimilation window
    desired_radar_list : list of radars to process
    infile_list  : list of input files to be superobbed
    pathout      : output average sqlite file(s) 
    outfile_struc: structure of output file name ; will be passed to strftime
    timing       : activation of time analysis, only the first PPI in a volume scan will be averaged
    ops_run_name : name of operational run 
    n_rays       : number of rays
    delta_range  : delta range of the boxes
    n_cpus       : number of cpus for parallel execution, with n_cpus=1 joba are launched sequentially and dask is not invoked 
 
  output:
    Nothing
    Average sqlite file(s) are created with the '_thin' suffix

  """

  #start and stop time of assimilation window
  window_t0 = center_time - datetime.timedelta(seconds=3600*window_width/2.)
  window_tf = center_time + datetime.timedelta(seconds=3600*window_width/2.)
  
  #flush fileout if it already exists
  pathfileout=f"{pathout}/{center_time.strftime(outfile_struc)}"

  if os.path.isfile(pathfileout):
    os.remove(pathfileout)

  #init large output file
  conn_pathfileout = sqlite3.connect(pathfileout)

  schema = find_schema('schema')
  with open(schema) as f:
    schema = f.read()
  conn_pathfileout.executescript(schema)

  print('make list of files, radars and times that will be processed in parallel...')
  vol_scan_list = []
  for this_file in infile_list:
    with sqlite3.connect(this_file) as conn_loops:
      # list of radars in the file
      avail_radar_list  = [ stn[0] for stn in conn_loops.execute("select distinct ID_STN from header order by 1;").fetchall() ]
      print (avail_radar_list)
      for this_radar in avail_radar_list:
        #select radars if desired radar_list is specified
        print (this_radar,desired_radar_list != 'all')
        if desired_radar_list != 'all':
          if this_radar not in avail_radar_list:
            continue
        # dates
        result = conn_loops.execute(f"select distinct DATE, printf('%06d', TIME) from header where ID_STN = '{this_radar}' ;").fetchall()
        datetime_list  = [datetime.datetime.strptime(f'{date_time[0]}{date_time[1]}', '%Y%m%d%H%M%S') for date_time in result]
        datetime_list.sort()
        print ("DAVID",datetime_list)
        for this_date in datetime_list:
          #only include date in assimilation window
          print (this_date ,'>', window_t0, this_date ,'<',window_tf)
          if (this_date > window_t0) and (this_date <= window_tf):
            vol_scan_list.append( {'file':this_file, 'radar':this_radar, 'date':this_date} )
  
  if len(vol_scan_list) == 0:
    raise RuntimeError('List of volume scan to process is empty. Check that files are available and search criteria are correct.')

  print('make averaging template')
  #initialize template that will be used for averaging every PPIs
  min_range_in_ppi =  10000.
  max_range_in_ppi = 240000.
  averaging_template = radvelso.fill_ray_dict(n_rays=n_rays,
                                              min_range_in_ppi = min_range_in_ppi,
                                              max_range_in_ppi = max_range_in_ppi,
                                              delta_range= delta_range)
  
  tc_0 = time.time()
  if timing :

    print ("Compute only one PPI ")
    this_file  = vol_scan_list[0]['file']
    this_radar = vol_scan_list[0]['radar']
    this_date  = vol_scan_list[0]['date']
    superobs(this_file, this_radar, this_date, 
             pathfileout, averaging_template, ops_run_name, timer=True)
    tc_1 = time.time()

  else:

    if n_cpus == 1:
      #serial execution, usefull for debugging
      print('Serial execution')
      for vscan in vol_scan_list:
        superobs(vscan['file'] ,vscan['radar'], vscan['date'], 
                 pathfileout, averaging_template, ops_run_name)
    else:
      print(f'Compute {len(vol_scan_list)} volume scans in parallel')
      with tempfile.TemporaryDirectory() as tmpdir:
        #the directory dask-worker-space/ will be in tmpdir
        with dask.distributed.Client(processes=True, threads_per_worker=1, 
                                     n_workers=n_cpus, 
                                     local_directory=tmpdir, 
                                     silence_logs=40) as client:

          #delay data 
          averaging_template = dask.delayed(averaging_template)
          joblist = [delayed(superobs)(vscan['file'], vscan['radar'], vscan['date'], 
                                       pathfileout, averaging_template, ops_run_name) for vscan in vol_scan_list]
          dask.compute(joblist)
   
    sample_file  = vol_scan_list[0]['file']
    # create info and resume_tables in fileout
    create_info_midas_tables(sample_file, conn_pathfileout, n_rays, delta_range, ops_run_name)   
    # improve searches with index tables
    create_index_tables_idobs_iddata(conn_pathfileout)
    # collision_test
    collision_test(conn_pathfileout)
    # close connection
    conn_pathfileout.close()
    tc_1 = time.time()
   
  print(f"Runtime total: {round(tc_1-tc_0,4)} s")

def arg_call():
    import argparse 

    parser = argparse.ArgumentParser()
    parser.add_argument('--center_time',  default='undefined', type=str,   help="YYYYMMDDHH center time of assimilation window")
    parser.add_argument('--window_width', default=0.,          type=float, help="[hours] width of assimilation window")
    parser.add_argument('--desired_radar_list', nargs="+", default='all',          help="List of radars to process")
    parser.add_argument('--inputfiles', nargs="+", default='undefined',    help="input sqlite file to average")
    parser.add_argument('--pathin',       default='undefined', type=str,   help="directory where are input sqlite files")
    parser.add_argument('--infile_struc', default='*/%Y%m%d%H_ra',type=str,help="structure of input file name")
    parser.add_argument('--pathout',      default=os.getcwd(), type=str,   help="where averaged sqlite files will be put")
    parser.add_argument('--outfile_struc',default='%Y%m%d%H_superobbed_dvel_ground_radars.sqlite', type=str,   help="structure of output file name")
    parser.add_argument('--timing',       action="store_true",             help="Average only one PPI for time analysis" ) 
    parser.add_argument('--ops_run_name', default='N1',        type=str,   help="Name of operational run (will show up in rdb4_schema)" ) 
    parser.add_argument('--n_rays',       default=20,          type=int,   help="Number of rays for averaging" )
    parser.add_argument('--delta_range',  default=10000.,      type=float, help="Delta_range  for averaging" )
    parser.add_argument('--n_cpus',       default=1,           type=int,   help="Number of rays for averaging" )

    args = parser.parse_args()

    if args.inputfiles == 'undefined' and args.pathin == 'undefined':

      args.center_time = '2019073100'
      args.window_width = 6.
      args.desired_radar_list = ['casra', 'usdyx']
      #option1: explicitely specify inputfiles
      #args.inputfiles = ['/space/hall4/sitestore/eccc/cmd/a/dlo001/data/doppler_qc/doppler_qc_v0.3/sqlite_v1.0.0_qc/split_6h/USVNX/2019073100_ra',
      #                   '/space/hall4/sitestore/eccc/cmd/a/dlo001/data/doppler_qc/doppler_qc_v0.3/sqlite_v1.0.0_qc/split_6h/CASRA/2019073100_ra']
      #option2: specify pathin + infile_struc and let Python search for files
      args.pathin = '/space/hall4/sitestore/eccc/cmd/a/dlo001/data/doppler_qc/doppler_qc_v0.3/sqlite_v1.0.0_qc/split_6h/'
      args.pathout = './work'
      args.timing = False
      args.plot   = False
      args.n_cpus = 40

      print(f'superobs called with no input filename(s)')
      print(f'We are running demo with:')
      for arg in vars(args):
        print(f'--{arg}  {getattr(args, arg)}')


    #argument checking
    if args.center_time == 'undefined':
        raise ValueError('Center time of assimilation window must be provided')
    else:
       args.center_time = datetime.datetime.strptime(args.center_time, '%Y%m%d%H')

    if np.isclose(args.window_width, 0.) :
        raise ValueError('Window width must be provided')

    if args.inputfiles != 'undefined':
      #if inputfiles argument is provided, we use that
      infile_list = args.inputfiles 

    elif args.pathin != 'undefined': 
      #alternatively, search for files with pathin+infile_struc 
      if not os.path.isdir(args.pathin):
        raise ValueError(f'pathin: {args.pathin} does not exist.')
      search_str = args.center_time.strftime(args.infile_struc)
      infile_list = glob.glob(f'{args.pathin}/{search_str}')

    else:
      raise ValueError('At least one of inputfiles ot pathin must be provided')

    #check infile_list
    if len(infile_list) == 0:
      raise ValueError('infile_list is empty, we stop here')
      sys.exit(1)

    else:
      for this_file in infile_list:
        if not os.path.isfile(this_file):
          raise ValueError(f'inputfiles: {this_file} does not exist.')

    if not os.path.isdir(args.pathout):
      os.mkdir(args.pathout)

    #sys.exit is used to the return status of main is catched and passed to caller
    print (infile_list)
    sys.exit(compute_average(args.center_time,
                  args.window_width,
                  args.desired_radar_list,
                  infile_list, 
                  args.pathout, 
                  args.outfile_struc, 
                  args.timing, 
                  args.ops_run_name, 
                  args.n_rays, 
                  args.delta_range, 
                  args.n_cpus) )

if __name__ == '__main__':
    arg_call()
