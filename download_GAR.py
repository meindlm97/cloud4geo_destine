# download_GAR.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download hourly 2-m air temperature (t2m) form the Destination Earth
Climate Digital Twin (Climate DT) via th Polytiope service and store it
as a single Zarr archive.

Data: ICON model, SSP3-7.0 projection, high resolution
Region: Greater Alpine Region (GAR), cut out with a bounding box
Period: January 2020, one request per day (24 hourly steps each)

@author: Maximilian Meindl, University of Vienna
"""

import pandas as pd        # used to build the list od dates
import earthkit.data       # ECMWF library for accessing DestinE data via Polytope
import xarray as xr        # data handling and Zarr output (used via ds.to_zarr)

# Output path of the Zarr store that collects all downloaded days
zarr_path = "/jetfs/scratch/mmeindl/HighResLearn/download/cloud4geo_km-scale/t2m_icon_ssp3-7.0_2020-01_GAR.zarr"

# Time period to be downloaded: eveyr day from 1 to 31 January 2020
dates = pd.date_range("2020-01-01", "2020-01-31", freq="D")

# One request is sent per day. Splitting the period into daily requests
# keeps each request small and lets the Zarr store grow step by step.
for i, date in enumerate(dates):
    # Date in the YYYYMMDD format expected by the request
    date_str = date.strftime("%Y%m%d")
    print(f"[{i+1}/{len(dates)}] Downloading {date_str}...")

    # MARS-style request describing which data to retrieve
    request = {
        # Type of simulation: "baseline" (historical/control runs) or "projections" (future scenario runs)
        "activity": "projections",
        "class": "d1",                    # Destination Earth data class
        "dataset": "climate-dt",          # Climate Digitial Twin
        # Experiment: "hist" (historical) or "ssp3-7.0" (SSP3-7.0 emission scenario)
        "experiment": "ssp3-7.0",
        "generation": "2",                # Climate DT production generation (phase 2)
        "levtype": "sfc",                 # surface (single-level) field
        "date": date_str,                 # day to retrieve
        "model": "icon",                  # climate model (ICON)
        "expver": "0001",                 # experiemnt version
        "param": "167",                   # GRIB parameter ID 167 = 2-m temperature (t2m)
        "realization": "1",               # ensemble member
        # Spatial resolution of the model output: "high" or "standard"
        "resolution": "high",             
        "stream": "clte",                 # climate stream for Climate DT output
        "type": "fc",                     # forecast/model output
        # All 24 hourly time steps of the day: "0000/0100/.../2300"
        "time": "/".join(f"{h:04d}" for h in range(0, 2400, 100)),
        # Spatial cut-out done on the server, so only the region is downloaded.
        # Points are [lat, lon] of two opposite corners:
        # north-west corner (50.0 N, 1.5 E) and south-east corner (40.0 N, 17.0 E)
        "feature": {
            "type": "boundingbox",
            "points": [[50.0, 1.5], [40.0, 17.0]], # Greater Alpine Region
        },
    }

    # Send the request to the DestinE Polytope service.
    # The adress chooses the data bridge: LUMI or MareNostrum 5 (MN5)
    # which one hold the data depends on the model/experiment.
    data = earthkit.data.from_source(
        "polytope", "destination-earth", request,
        #address="polytope.mn5.apps.dte.destination-earth.eu",
        address="polytope.lumi.apps.dte.destination-earth.eu",
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
