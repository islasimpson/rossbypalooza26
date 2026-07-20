# rossbypalooza26
A github repo for analysis code for the Simpson/Yeager group at Rossbypalooza

Recommended conda environment = npl_2026a

To install utilities in rossby_utils do the following from the rossbypalooza26 directory

```
module load conda
conda activate npl_2026a
pip install -e --user
```

Contents of this repo

- `./DATA_DOWNLOAD` = scripts for downloading seasonal prediction data from other models from Copernicus CDS
- `./processing/CDS/` = scripts for processing models downloaded from the CDS
    - `./sort_and_remove_climo` = sorting CDS model data, organizing timestamps etc, and removing the lead dependent climatology for each system
    - `./combine_systems` = scripts for combining the hindcasts anomalies for different systems to cover as long a period as possible
- `./processing/ERA5/` = scripts for obtaining monthly averaged ERA5 in the form of `(year,lead,...)` for direct comparison to hindcasts from the GDEX ERA5 data
- `./processing/CESM2/` = scripts for sorting out CESM2 hindcast datasets into easy to use form `(member,year,lead,...)`

