#!/usr/bin/env python
""" Script for download seasonal hindcasts for C3S         
    Requires cdsapi to be installed in your python environment (already installed in npl environments)
    Also need a file in your home directory .cdsapirc that contains the CDS url and your access key
"""
import cdsapi
import numpy as np
import os
import yaml
import sys

#read in information about systems and available years
with open("system_year_info.yaml") as f:
    systems = yaml.safe_load(f)

init_mon = 11 # initialization month
init_mon_str = str(init_mon).zfill(2)
target_month = [11, 12, 1, 2, 3] # the hindcast data month
lead= [((m - init_mon) % 12) + 1 for m in target_month] # the lead time for each target month

outpath="/glade/campaign/cgd/cas/islas/DATASETS/CDS/seasonal/"

models=['UKMO']

var="u_component_of_wind"
varshort="u030"
product_type="monthly_mean"

for imodel in models:
 
    # Make model output directory
    #outdir=outpath+imodel
    #os.mkdir(outdir, exist_ok=True)
  
    # get the info about hindcast start and end dates
    modeldat = systems[imodel]
    hindcast_start = modeldat['hindcast']['start']
    hindcast_end = modeldat['hindcast']['end']
    hindcastyears = [str(y) for y in range(hindcast_start, hindcast_end + 1)]

    # loop over forecasts
    for system, years in modeldat["forecast"].items():
        print(system)
  
        # Make output directory for this system
        outdir=outpath+imodel+'/grib/'+varshort+'/'+str(system)
        os.makedirs(outdir, exist_ok=True)

        forecastyears = [ str(y) for y in years ]

        # Loop over target_months
        for i in range(0,len(target_month),1):
            monuse = target_month[i]
            leaduse = lead[i]

            monuse_str = str(int(monuse)).zfill(2)
            leaduse_str = str(int(leaduse)).zfill(2)
            init_mon_str = str(int(init_mon)).zfill(2)

            # download the hindcast set
            dataset = "seasonal-monthly-pressure-levels"
            request = {
                "originating_centre": imodel.lower(),
                "system": str(system),
                "variable": [var],
                "pressure_level": ["30"],
                "product_type": [product_type],
                "year": hindcastyears,
                "month": str(init_mon),
                "leadtime_month":str(leaduse),
                "data_format": "grib"
            }
            client = cdsapi.Client()
            client.retrieve(dataset, request).download(f"{outdir}/hindcast_{varshort}_init{init_mon_str}_mon{monuse_str}.grib")

            # download the forecast set
            request = {
                "originating_centre": imodel.lower(),
                "system": str(system),
                "variable": [var],
                "pressure_level": ["30"], 
                "product_type": [product_type],
                "year": forecastyears,
                "month": str(init_mon),
                "leadtime_month":str(leaduse),
                "data_format": "grib"
            }
            client = cdsapi.Client()
            client.retrieve(dataset, request).download(f"{outdir}/forecast_{varshort}_init{init_mon_str}_mon{monuse_str}.grib")
