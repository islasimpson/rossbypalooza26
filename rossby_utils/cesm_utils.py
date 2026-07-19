# Utilities that are useful for processing CESM3 data
import xarray as xr
import numpy as np

def round_lons_and_lats(dat):
    """
    Function for fixing tiny round-off level differences in the lon or lat variables
    """
    if 'lat' in dat.coords:
        dat = dat.assign_coords(lat=np.round(dat['lat'], 6))
    if 'lon' in dat.coords:
        dat = dat.assign_coords(lon=np.round(dat['lon'], 6))
    return dat

def fix_cesm_time(dat):
    """
    Fix the peculiarities of the CESM calendar
    By default, the timestamp of a month is the end of the averaging 
    period which is midnight of the first day of the following month
    e.g., Nov 1990 will be December 1st 1990
    Changing this to be the average of time bounds.
    """

    if 'time_bound' in dat.data_vars:
        timebndsvar='time_bound'
    elif 'time_bnds' in dat.data_vars:
        timebndsvar='time_bnds'
    else:
        print('this code only works with time bounds variables time_bounds or time_bnds')
        
    timebnds = dat[timebndsvar]
    timebnddim = timebnds.dims[1]
    diff = np.array(timebnds.isel({timebnddim:1})) - np.array(timebnds.isel({timebnddim:0}))
    diff = diff / 2.
    newtime = np.array(timebnds.isel({timebnddim:0})) + diff
    dat['time'] = newtime
    return dat
