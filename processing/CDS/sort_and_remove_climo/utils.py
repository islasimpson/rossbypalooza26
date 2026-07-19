import xarray as xr
import numpy as np
import pandas as pd

# Utilities for dealing with hindcasts downloaded from CDS

def get_midmonth_time(dat, shift_days=5):
    """ 
    Function for converting valid_time to be the middle of the month
    instead of the end of the averaging period.
    Note that forecasts can vary as to how far time + step extends into the 
    next month, so use shift_days to modify the shift as needed
    """

    valid_time = dat.valid_time
    month = valid_time - np.timedelta64(shift_days,"D")
    month_d1 = month.dt.floor("D").astype("datetime64[M]")
    ndays = month.dt.days_in_month
    midday = (ndays + 1) // 2
    newtime = month_d1 + (midday - 1).astype("timedelta64[D]")
    newtime = newtime.compute()
    # replace valid_time axis with the midmonth time
    dat['valid_time'] = newtime
    return dat

def deal_with_lagged_inits(dat, times, data_var):
    """
    Function for dealing with lagged initial condition dates
    Grouping by valid_time and dropping invalid members
    """
    monthly_groups = []
    for forecast_time, group in dat.groupby(times):
        # remove forecast multiindex
        group = group.rename({'forecast':'number2'})
        #group = group.reset_index("number2", drop=True)
        # Combine lagged initialization and original member number
        group = group.stack(member=("number2","number"))
        # find member combinations that are valid
        valid_member = group[data_var].notnull().any(dim=['latitude','longitude']).compute()
        valid_indices = np.flatnonzero(valid_member.values)
        group_valid = group.isel(member=valid_indices)
        # replace the multi-index with a simple member coord
        group_valid =group_valid.assign_coords(member=np.arange(group_valid.sizes['member']))
        #
        if "time" in group_valid:
            group_valid = group_valid.drop_vars("time") 
        group_valid = group_valid.expand_dims(time=[forecast_time])
        monthly_groups.append(group_valid)
    dat_monthly = xr.concat(monthly_groups, dim='time')
    return dat_monthly

def sort_predictions(dat, data_var):
    """ 
    function for sorting out hindcasts into (year,lead,lat,lon) arrays
    accounts for lagged initial condition dates when necessary

    data = hindcast array
    data_var = variable name
    """

    reduce_dims = [
        dim for dim in ["number","latitude","longitude"]
        if dim in dat[data_var].dims ]

    has_time = "time" in dat.dims
    has_step = "step" in dat.dims

#    probe = ( dat[data_var].isel(latitude=slice(0,2), longitude=slice(0,2)).notnull().any(dim=['number','latitude','longitude']).compute())
    probe = ( dat[data_var].mean(dim=['latitude','longitude'], skipna=True)
            .notnull()
            .any(dim=['number']).compute()) 

    # case1, has both time and step
    if has_time and has_step:
        # compute validity array
        time_ind, step_ind = np.nonzero(probe.values)
        time_indexer = xr.DataArray(time_ind, dims='forecast')
        step_indexer = xr.DataArray(step_ind, dims='forecast')
        dat_stack = dat.isel(time=time_indexer, step=step_indexer)

#        valid = ( dat[data_var].notnull().any(dim=reduce_dims).compute() )
#        valid_stack = valid.stack(forecast=("time","step"),
#                       create_index=False)
#        valid_indices = np.flatnonzero(valid_stack.values)
#       
#        # stack the data
#        dat_stack = dat.stack(forecast=('time','step'), create_index=False)
#      
#        # select only valid data
#        dat_stack = dat_stack.isel(forecast=valid_indices)
#    
        flag_lagged = dat.sizes["time"] > 1
     # case2, only has time ! this may not work properly below
    elif has_time:
        #valid = ( dat[data_var].notnull().any(dim=reduce_dims).compute())
        #valid_indices = np.flatnonzero(probe.values)
        time_ind  = np.flatnonzero(probe.values)
        time_indexer = xr.DataArray(time_ind, dims='forecast')
        dat_stack = dat.isel(time=time_indexer)
        
        flag_lagged = dat.sizes["time"] > 1

        #flag_lagged = False
    elif has_step:
        #valid = (dat[data_var].notnull().any(dim=reduce_dims).compute())
        #valid_indices = np.flatnonzero(probe.values)
        step_ind = np.flatnonzero(probe.values)
        step_indexer = xr.DataArray(step_ind, dims='forecast')
        dat_stack = dat.isel(step = step_indexer)

        flag_lagged = False
    else:
        dat_stack = dat.expand_dims(forecast  = [0])
        flag_lagged = False 

        #dat_stack = (dat.isel(step=valid_indices).rename(step="forecast"))

        #flag_lagged = False

    # Set the time axis to always be the 15th of the month
    month_key = (dat_stack.valid_time.astype("datetime64[M]").rename("target_month").compute() )
    times = ( month_key + np.timedelta64(14,"D")).astype("datetime64[ns]")
    dat_stack['valid_time'] = times

    # Now deal with lagged initial condition dates.  Group by valid time and drop invali members
    if flag_lagged:
        dat_monthly = deal_with_lagged_inits(dat_stack, times, data_var)
    else: 
        # rename forecast and number and give it the mid-month times
        dat_monthly = dat_stack.rename({'forecast':'time', 'number':'member'})
        dat_monthly = dat_monthly.assign_coords(time=('time', np.atleast_1d(times.values)))
        #dat_monthly['time'] = times.values



#    # check for lagged initializations
#    flag_lagged=False
#    try:
#        dat_stack = dat.stack(forecast=('time','step'))
#        flag_lagged=True
#    except:
#        dat_stack = dat.rename(time='forecast')
#
#    # get an appropriate time axis that is the middle of the month
#    #dat_stack = get_midmonth_time(dat_stack)
#    
#    # drop empty elements
#    valid = dat_stack[data_var].notnull().any(dim=['number','latitude','longitude']).compute()
#    dat_stack = dat_stack.isel(forecast=valid)
#
#    # Set the time axis to always be the 15th of the month
#    month_key = (dat_stack.valid_time.astype("datetime64[M]").rename("target_month").compute() )
#    times = ( month_key + np.timedelta64(14,"D")).astype("datetime64[ns]")
#    dat_stack['valid_time'] = times
#
#    # sort out the time axis
#    # valid time is at the end of the averaging period (December 1 for November etc)
#    # Changing the time to be the middle of the month
#    #dat_stack = get_midmonth_time(dat_stack)
#    #times = dat_stack.valid_time.compute()
#
#    # Now deal with lagged initial condition dates.  Group by valid time and drop invali members
#    if flag_lagged:
#        dat_monthly = deal_with_lagged_inits(dat_stack, times, data_var)
#    else: 
#        # rename forecast and number and give it the mid-month times
#        dat_monthly = dat_stack.rename({'forecast':'time', 'number':'member'})
#        dat_monthly = dat_monthly.assign_coords(time=('time', np.atleast_1d(times.values)))
#        #dat_monthly['time'] = times.values

    return dat_monthly













