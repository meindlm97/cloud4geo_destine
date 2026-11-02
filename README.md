# cloud4geo_destine

Download DestinE Climate DT Phase 2 data using the Polytope-Client and store zarr-files on the Cloud4geo storage provided by EODC.

## Installation and Setup

To run the [example download script](https://github.com/meindlm97/cloud4geo_destine/blob/main/download_GAR.py) and also the [plotting notebook](https://github.com/meindlm97/cloud4geo_destine/blob/main/plot_GAR.ipynb) you can use the [environment.yml](https://github.com/meindlm97/cloud4geo_destine/blob/main/environment.yml) file provided to create a conda environment that can run the code. The following commands create the environment and also create an ipykernel called *eodc-zarr* that can be used in Jupyter notebooks if selected.

```
# create conda environment named 'eodc-zarr' based on the environment.yml
conda env create -n eodc-zarr -f environment.yml

# activate the environment
conda activate eodc-zarr

# set environment to the default used by ipykernels
python3 -m ipykernel install --user --name=eodc-zarr
```

## Destination Earth

Destination Earth is a flagship initiative of the European Commission to develop a highly-accurate digital model of the Earth (a digital twin of the Earth) to model, monitor and simulate natural phenomena, hazards and the related human activities. This initiative presents the first ever attempt to operationalise the production of global multi-decadal climate projections at km-scale resolutions of 5 to 10km. To access the datasets from the [Earth Data Hub](https://earthdatahub.destine.eu/) you need to register on the [Destination Earth Platform](https://platform.destine.eu/). In order to get full access to the data, one has to [upgrade the access](https://platform.destine.eu/access-policy-upgrade/) by selecting the appropriate user category (e.g Academia & research). Your request will reviewed and you will be notified on the acceptance.

**⚠️Note**: 
- Data is provided on a hierachical [HEALPix](https://healpix.sourceforge.io/) grid for all models (ICON & IFS-NEMO/IFS-FESOM). 
- Data is provided on various levtype values, for different parameters: 2 metre temperature (2t) has the parameter 167, Total precipitation rate (avg_tprate) has the parameter 235055. For more information check out the [Climate DT data catalogue](https://platform.destine.eu/services/documents-and-api/doc/?service_name=climate-dt-user-guide).

The easiest way to access the Destination Earth DT data is via the [Polytope web service](https://github.com/destination-earth-digital-twins/polytope-examples/tree/main):

1. The polytope-client can be installed from PyPI:

```pip install --upgrade polytope-client```

2. Retrieve a token from the Destination Earth Service Platform (DESP) by running the script included in the repository:

```python desp-authentication.py```

You will then be prompted to enter your username and password which were set during the registration process.

You will also need some additional dependencies to run the script, which can be also installed using pip:

```pip install --upgrade lxml conflator```

The script automatically places your token in ```~/.polytopeapirc``` where the client will pick it up. The token is a long-lived ("offline_access") token.

## Earthkit package and Polytope service

[earthkit](https://earthkit.readthedocs.io/) is a collection of open-source Python packages developed by ECMWF to simplify working with weather and climate data. In this repository two of its components are used:

- **earthkit-data** for retrieving the data. It provides a common interface to many data sources, including Polytope. The data is requested via `earthkit.data.from_source()` and can then be converted directly into an xarray Dataset with `.to_xarray()`.
- **earthkit-plots** for plotting the downloaded data on maps.

[Polytope](https://polytope.readthedocs.io/en/latest/) is a data extraction service developed by ECMWF, which provides both access to full field global data and feature extraction capabilities. Instead of downloading entire global fields, Polytope can cut out the requested feature (e.g. a bounding box, a time series at a point or a vertical profile) directly on the server, so that only the data actually needed is transferred. This is essential for the km-scale Climate DT data, where a single global field at 5 km resolution is very large.

The download script sends the request to the Polytope service as follows:

```python
import earthkit.data

data = earthkit.data.from_source(
    "polytope",                   # data source: Polytope service
    "destination-earth",          # Polytope collection for DestinE data
    request,                      # MARS-style request (see table below)
    address="polytope.lumi.apps.dte.destination-earth.eu",  # data bridge (LUMI or MN5)
    stream=False,                 # download the full result before returning it
)

ds = data.to_xarray()             # convert to an xarray Dataset
```

The authentication token stored in `~/.polytopeapirc` (see above) is picked up automatically, so no credentials need to be passed in the script.

**Data bridges: LUMI and MareNostrum 5**

The Climate DT simulations are run on two European pre-exascale supercomputers of the EuroHPC Joint Undertaking: [LUMI](https://www.lumi-supercomputer.eu/) (CSC, Kajaani, Finland) and [MareNostrum 5](https://www.bsc.es/marenostrum/marenostrum-5) (BSC, Barcelona, Spain). The model output is stored on a *data bridge* attached to each machine, and each data bridge has its own Polytope endpoint:

| Data bridge | Polytope address |
|---|---|
| LUMI | `polytope.lumi.apps.dte.destination-earth.eu` |
| MareNostrum 5 (MN5) | `polytope.mn5.apps.dte.destination-earth.eu` |

Data of a given simulation is only available on the data bridge where it is stored, so the `address` has to match the model and experiment requested. If a request fails or returns no data, try the other data bridge. Which simulation is stored on which data bridge is documented in the [Climate DT user guide](https://platform.destine.eu/services/documents-and-api/doc/?service_name=climate-dt-user-guide).

## Request parameters

The [example download script](https://github.com/meindlm97/cloud4geo_destine/blob/main/download_GAR.py) sends one request per day to the Polytope service. The table below explains each parameter of the request:

| Key | Value | Description |
|---|---|---|
| `activity` | `projections` | Type of simulation: `baseline` (historical/control runs) or `projections` (future scenario runs) |
| `class` | `d1` | Destination Earth data class |
| `dataset` | `climate-dt` | Climate Digital Twin |
| `experiment` | `ssp3-7.0` | Experiment: `hist` (historical) or `ssp3-7.0` (SSP3-7.0 emission scenario) |
| `generation` | `2` | Climate DT production generation (Phase 2) |
| `levtype` | `sfc` | Level type: surface (single-level) field |
| `date` | `YYYYMMDD` | Day to retrieve, set for each request in the loop |
| `model` | `icon` | Climate model: `icon`, `ifs-nemo` or `ifs-fesom` |
| `expver` | `0001` | Experiment version |
| `param` | `167` | GRIB parameter ID, `167` = 2 m temperature (2t) |
| `realization` | `1` | Ensemble member |
| `resolution` | `high` | Spatial resolution of the model output: `high` or `standard` |
| `stream` | `clte` | Climate stream for Climate DT output |
| `type` | `fc` | Forecast/model output |
| `time` | `0000/0100/.../2300` | All 24 hourly time steps of the day |
| `feature` | `boundingbox` | Spatial cut-out done on the server, so only the region is downloaded. `points` are the [lat, lon] of two opposite corners: north-west (50.0 N, 1.5 E) and south-east (40.0 N, 17.0 E), covering the Greater Alpine Region |

The values must be adjusted accordingly for the downloads. In our case, this specifically applies to the keys:
 - `activity`
 - `experiment`
 - `levtype`
 - `date`
 - `model`
 - `param`

The [Climate DT Generation 2 multi-decadal global simulations](https://platform.destine.eu/climate-dt/) are produced with three state-of-the-art coupled Earth-system models (ICON, IFS-NEMO and IFS-FESOM). The simulations cover the period 1990-2049, including a historical (01/01/1990–31/12/2014) and a scenario (01/01/2015–31/12/2049) experiment. Therefore, we consider six downloads (3 x 2) per parameter. To provide a clearer overview, we plan to create a seperature [issue](https://github.com/meindlm97/cloud4geo_destine/issues) for each download and make the corresponding download scripts available.

## Data catalogue

**levtype=sfc**

| Short name | Parameter ID | Long name | Units | Frequency |
|---|---|---|---|---|
| 2t | 167 | 2 metre temperature | K | hourly |
| avg_tprate | 235055 | Time-mean total precipitation rate | kg m**-2 s**-1 | hourly |
| avg_sdswrf | 235035 | Time-mean surface downward short-wave radiation flux | W m-2 | hourly |
| 10u | 165 | 10 metre U wind component | m s**-1 | hourly |
| 10v | 166 | 10 metre V wind component | m s**-1 | hourly |

*Need to clarify: How are daily mean, minimum and maximum temperatures calculated?* 

**levtype=pl**

19 pressure levels: (1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 70, 50, 30, 20, 10, 5, 1)

| Short name | Parameter ID | Long name | Units | Frequency |
|---|---|---|---|---|
| r | 157 | Relative humidity | % | hourly |

*Select "levtype": "pl" in the Polytope request.*
