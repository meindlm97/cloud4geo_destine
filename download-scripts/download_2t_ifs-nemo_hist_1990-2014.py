# download_GAR.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download hourly 2 metre temperature(2t) form the Destination Earth
Climate Digital Twin (Climate DT) via th Polytiope service and store it
as a single Zarr archive.

Data: IFS-NEMO model, historical experiment, high resolution
Region: Greater Alpine Region (GAR), cut out with a bounding box
Period: 1990-2014, one request per day (24 hourly steps each)

@author: Maximilian Meindl, University of Vienna
"""

import pandas as pd        # used to build the list od dates
import earthkit.data       # ECMWF library for accessing DestinE data via Polytope
import xarray as xr        # data handling and Zarr output (used via ds.to_zarr)

# Output path of the Zarr store that collects all downloaded days
zarr_path = "/jetfs/scratch/mmeindl/HighResLearn/download/cloud4geo_km-scale/2t_ifs-nemo_hist_1990-2014.zarr"

# Time period to be downloaded: eveyr day from 1 to 31 January 2020
dates = pd.date_range("1990-01-01", "2014-12-31", freq="D")

# One request is sent per day. Splitting the period into daily requests
# keeps each request small and lets the Zarr store grow step by step.
for i, date in enumerate(dates):
    # Date in the YYYYMMDD format expected by the request
    date_str = date.strftime("%Y%m%d")
    print(f"[{i+1}/{len(dates)}] Downloading {date_str}...")

    # MARS-style request describing which data to retrieve
    request = {
        # Type of simulation: "baseline" (historical/control runs) or "projections" (future scenario runs)
        "activity": "baseline",
        "class": "d1",                    # Destination Earth data class
        "dataset": "climate-dt",          # Climate Digitial Twin
        "experiment": "hist",
        "generation": "2",                # Climate DT production generation (phase 2)
        "levtype": "sfc",                 # surface (single-level) field
        "date": date_str,                 # day to retrieve
        "model": "ifs-nemo",              # climate model (IFS-NEMO)
        "expver": "0001",                 # experiemnt version
        "param": "167",                   # GRIB parameter ID 167 = 2-m temperature (t2m)
        "realization": "1",               # ensemble member
        "resolution": "high",             
        "stream": "clte",                 # climate stream for Climate DT output
        "type": "fc",                     # forecast/model output
        "time": "/".join(f"{h:04d}" for h in range(0, 2400, 100)),
        "feature": {
            "type": "boundingbox",
            "points": [[50.0, 1.5], [40.0, 17.0]], # Greater Alpine Region
        },
    }

    # Send the request to the DestinE Polytope service.
    # The adress chooses the data bridge: MareNostrum 5 (MN5)
    data = earthkit.data.from_source(
        "polytope", "destination-earth", request,
        address="polytope.mn5.apps.dte.destination-earth.eu",
        stream=False,
    )

    # Convert the downloaded data into an xarray Dataset
    ds = data.to_xarray()

    if i == 0:
        # First day: create a new Zarr store overwrites an existing one!)
        ds.to_zarr(zarr_path, mode="w")
    else:
        # Following days: append along the time dimension.
        # "datetimes" must match the name of the time dimension in ds
        ds.to_zarr(zarr_path, mode="a", append_dim="datetimes")

print("Done!")
