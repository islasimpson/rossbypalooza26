# Information on the data download and processing

Seasonal predictions for systems other than CESM were downloaded from the [Copernicus Climate Change Services](https://cds.climate.copernicus.eu/datasets), selecting "Season Forecasts" for "Product type" in the menu on the left hand side.

Here's the process that was used for dealing with the seasonal predictions from the above climate data store (CDS).

- Data downloaded using scripts at `./DATA_DOWNLOAD/download_*.py` 
- Raw grib files end up in `/glade/campaign/cgd/cas/islas/DATASETS/CDS/seasonal/$model/grib/`

For each model, there are mutiple systems.  For each system there is a common hindcast period and then there are forecasts.  For some systems, there are lagged initialization dates which means that the time values for data for each member are not consistent.

- Informationon the hindcast and forecast years for each system are in `./DATA_DOWNLOAD/system_year_info.yaml`
- For each system, the members/dates are sorted and the anomalies from the lead dependent climatology are computed at `./processing/CDS/sort_and_remove_climo/*.ipynb`.
- This results in output located at `/glade/campaign/cgd/cas/islas/DATASETS/CDS/seasonal/$model/nc/`

Finally, the systems are combined by taking the hindcast anomalies for the most recent system and combining that with all the relevant forecasts anomalies from each system.  Regridding to a common 1 degree grid is also done at this stage since not all systems for a given model have the same grid.

- The sorting is done at `./processing/CDS/combine_systems/combine_$model.ipynb`
- Output is at `/glade/campaign/cgd/cas/islas/DATASETS/CDS/seasonal/combine_systems/$model`

