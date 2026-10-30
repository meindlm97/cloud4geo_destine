# cloud4geo_destine
Download DestinE Climate DT Phase 2 data using the Polytope-Client and store zarr-files on the Cloud4geo storage provided by EODC.

## Installation and Setup
To run the [download script](https://github.com/meindlm97/cloud4geo_destine/blob/main/download_GAR.py) and also the [plotting notebook](https://github.com/meindlm97/cloud4geo_destine/blob/main/plot_GAR.ipynb) you can use the [environment.yml](https://github.com/meindlm97/cloud4geo_destine/blob/main/environment.yml) file provided to create a conda environment that can run the code. The following commands create the environment and also create an ipykernel called eodc-zarr that can be used in Jupyter notebooks if selected.

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
- Data is provided on a hierachical [HEALPix](https://healpix.sourceforge.io/) grid for all models (ICON & IFS-FESOM/IFS-NEMO). 
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
