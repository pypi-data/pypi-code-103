import numpy as np

def fill_ray_dict(n_rays=8, 
                  min_range_in_ppi = 10000.,
                  max_range_in_ppi = 240000,
                  delta_range = 10000.):
    '''
    make a list of rays that will be included in average

      - all points of original data must be used.  In other words, the averaging scheme fully covers PPI
      - area is somewhat preserved ; new azimuths are added when areas become too large. We call this a new level.
      - range / delta_range is constant here
      - averaged radar rays must have constant center azimuth
      - delta_azimuth varies with range
    '''

    #setup dict for averaging
    half_delta_range = delta_range/2.
    range_bin_bounds = np.arange(min_range_in_ppi, max_range_in_ppi+delta_range, delta_range)
    range_bin_centers = range_bin_bounds[0:-1] + half_delta_range
    #in the average, we include   [azimuth - half_delta_azimuth , azimuth - half_delta_azimuth[
    #                             including lowest bound,               excluding highest bound
    half_delta_azimuth_rad = np.pi / n_rays #simplified from 1/2*(2pi radians / n_rays)
    azimuth_arr = np.linspace(0, 360, n_rays, endpoint=False)
    #make a list of rays in averaged PPI
    ray_list = []
    #fill ray list with full rays
    level = 1
    for this_azimuth in azimuth_arr:
        this_ray_dict = {'level'             : level,
                         'azimuth'           : this_azimuth,
                         'min_range_in_ppi'  : min_range_in_ppi,
                         'max_range_in_ppi'  : max_range_in_ppi, 
                         'range_bin_centers' : range_bin_centers,
                         'half_delta_range'  : half_delta_range,
                         'half_delta_azimuth': np.full_like(range_bin_centers,np.rad2deg(half_delta_azimuth_rad)) }
        ray_list.append(this_ray_dict)
    #fill in delta_azimuth for each range bins, add rays when needed
    this_range = range_bin_centers[0]
    ref_area = ( (this_range + half_delta_range)**2. - (this_range - half_delta_range)**2.) * half_delta_azimuth_rad
    for rr, this_range in enumerate(range_bin_centers):
        this_area = ( (this_range + half_delta_range)**2. - (this_range - half_delta_range)**2.) * half_delta_azimuth_rad

        #add rays and reduce delta azimuth to sorta preserve areas
        if this_area >= 1.3*ref_area:

            #double number of rays
            if np.pi/n_rays < np.deg2rad(0.5):
                #if delta azimuth is smaller than 0.5 degrees there will be no data in averaging bin
                #delay the addition of levels
                continue

            #add a level:
            #   by level, we mean a batch of rays that start at a given range.
            level += 1
            n_rays *= 2
            half_delta_azimuth_rad = np.pi / n_rays #simplified from 1/2*(2pi radians / n_rays)
            azimuth_arr = np.linspace(0, 360, n_rays, endpoint=False)

            #reduce delta azimuth for existing rays at all ranges greater than this one
            for this_ray in ray_list:
                inds = np.asarray(this_ray['range_bin_centers'] >= this_range).nonzero()[0]
                this_ray['half_delta_azimuth'][inds] = np.rad2deg(half_delta_azimuth_rad)

            #add new azimuth not already in dict
            azimuths_already_in_list = [this_ray['azimuth'] for this_ray in ray_list]
            for this_azimuth in azimuth_arr:
                if not np.any(np.isclose(this_azimuth, azimuths_already_in_list)):
                    #this azimuth is not already in ray list
                    #add new ray to list
                    this_ray_dict = {'level'             : level,
                                     'azimuth'           : this_azimuth,
                                     'min_range_in_ppi'  : this_range - half_delta_range,
                                     'max_range_in_ppi'  : max_range_in_ppi, 
                                     'range_bin_centers' : range_bin_centers[rr:],
                                     'half_delta_range'  : delta_range/2.,
                                     'half_delta_azimuth': np.full_like(range_bin_centers,np.rad2deg(half_delta_azimuth_rad))}
                    ray_list.append(this_ray_dict)
                    

    #print some info
    print(f'there are {len(ray_list)} rays in the averaged PPI in {level} levels')


    return ray_list


if __name__ == '__main__':
    fill_ray_dict()
