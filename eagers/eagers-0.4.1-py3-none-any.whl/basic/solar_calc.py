# import numpy as np
from numpy import sin, cos, tan, arcsin, arccos


def solar_calc(longitude, latitude, time_zone, inp_date):
    """ Calculate position of sun and sunrise and sunset times.\n
    Calculated using NOAA solar calculations available at:
    https://www.esrl.noaa.gov/gmd/grad/solcalc/NOAA_Solar_Calculations_day.xls \n
    LONGITUDE is longitude (+ to east).\n
    LATITUDE is latitude (+ to north).\n
    TIME_ZONE is the time zone (+ to east).\n
    INP_DATE is the date as a list of datetime objects, i.e. Jan 1 2017 = 
    datetime(2017,1,1).\n
    SUNRISE and SUNSET are given in fraction of the day, i.e. 6am = 6/24.\n
    AZIMUTH and ZENITH are given in degrees."""

    sunrise = []
    sunset = []
    zenith = []
    azimuth = []
    degrees = 180/3.141592653589793
    radians = 3.141592653589793/180

    tpm = [(x - x.replace(hour=0, minute=0, second=0)).total_seconds() / 24 / 3600  for x in inp_date] # time past midnight [days]
    jd = [x.toordinal() + 1721424.5 - time_zone/24 for x in inp_date]
        # Julian day [days]
        # Julian calendar epoch: Jan 1, 4713 B.C., 12:00:00.0
        # UNIX epoch: Jan 1, 0001 A.D., 00:00:00.0
        # MATLAB epoch: Jan 1, 0000 A.D., 00:00:00.0
        # 1721423.5 days from Julian epoch to UNIX epoch, plus 1 to match
        #     Microsoft Excel's year 1900 exception to the Gregorian calendar.
        # USNO Julian Date Converter:
        #     http://aa.usno.navy.mil/data/docs/JulianDate.php
        # More info on Excel dates:
        #     http://calendars.wikia.com/wiki/Microsoft_Excel_day_number
    for x in range(len(jd)):
        jc = (jd[x] - 2451545) / 36525 # Julian century
        geom_mean_long_sun = (280.46646 + jc * (36000.76983 + jc*0.0003032)) % 360 # [degrees]
        geom_mean_anom_sun = 357.52911 + jc * (35999.05029 - 0.0001537*jc) # [degrees]
        eccent_earth_orbit = 0.016708634 - jc * (0.000042037 + 0.0000001267*jc)
        sun_eq_of_center = float(
            sin(radians * (geom_mean_anom_sun)) * (1.914602 - jc * (0.004817 + 0.000014*jc)) 
            + sin(radians * (2*geom_mean_anom_sun)) * (0.019993 - 0.000101*jc) 
            + sin(radians * (3*geom_mean_anom_sun)) * 0.000289)
        sun_true_long = geom_mean_long_sun + sun_eq_of_center # [degrees]
        mean_obliq_ecliptic = 23 + (26 + (21.448 - jc * (46.815 + jc * (0.00059 - jc*0.001813))) / 60) / 60 # [degrees]
        sun_app_long = sun_true_long - 0.00569 - 0.00478 * sin(radians * (125.04 - 1934.136*jc)) # [degrees]
        obliq_corr = mean_obliq_ecliptic + 0.00256*cos(radians * (125.04 - 1934.136*jc)) # [degrees]
        sun_declin = arcsin(sin(radians * (obliq_corr))* sin(radians * (sun_app_long))) # solar declination [degrees]
        var_y = tan(radians * (obliq_corr/2)) * tan(radians * (obliq_corr/2))
        eq_of_time = 4 * degrees * ( var_y * sin(2*radians * (geom_mean_long_sun)) \
            - 2 * eccent_earth_orbit * sin(radians * (geom_mean_anom_sun)) \
            + 4 * eccent_earth_orbit * var_y * sin(radians * (geom_mean_anom_sun)) * cos(2*radians * (geom_mean_long_sun)) \
            - 0.5 * var_y * var_y * sin(4*radians * (geom_mean_long_sun)) \
            - 1.25 * eccent_earth_orbit * eccent_earth_orbit * sin(2*radians * (geom_mean_anom_sun)))
        ha_sunrise = degrees * (arccos( \
            cos(radians * (90.833)) / (cos(radians * (latitude)) * cos(sun_declin)) \
            - tan(radians * (latitude)) * tan(sun_declin)))
            # sunlight hours [degrees]
        solar_noon = (720 - 4*longitude - eq_of_time + time_zone*60) / 1440
        sunrise.append(solar_noon - ha_sunrise * 4 / 1440) # Local Sidereal Time (LST)
        sunset.append(solar_noon + ha_sunrise * 4 / 1440) # Local Sidereal Time (LST)
        tst = (tpm[x]*1440 + eq_of_time + 4*longitude - 60*time_zone) % 1440 # True Solar Time [min]
        if tst/4 < 0:
            hour_angle = tst/4 + 180 # [degrees]
        else:
            hour_angle = tst/4 - 180 # [degrees]
        zenith.append(degrees * (arccos(sin(radians * (latitude)) * sin(sun_declin) 
            + cos(radians * (latitude)) * cos(sun_declin) * cos(radians * (hour_angle)))))  # [degrees]
        ang = float(degrees * (arccos(((sin(radians * (latitude))*cos(radians * (zenith[x]))) - sin(sun_declin))
            / (cos(radians * (latitude))*sin(radians * (zenith[x]))))))
        if hour_angle>0:
            azimuth.append((ang+180) % 360)#[degrees] (clockwise from N)
        else:
            azimuth.append((540-ang) % 360) #[degrees] (clockwise from N)
    return sunrise, sunset, azimuth, zenith
