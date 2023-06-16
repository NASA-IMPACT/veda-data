# veda-data

This repository houses data used to define a VEDA dataset to load into the [VEDA catalog](https://nasa-impact.github.io/veda-docs/services/apis.html). Inclusion in the VEDA catalog is a prerequisite for displaying the dataset in the [VEDA Dashboard](https://www.earthdata.nasa.gov/dashboard/).

The data provided here gets processed in the ingestion system [veda-data-airflow](https://github.com/NASA-IMPACT/veda-data-airflow), to which this repository is directly linked (as a Git submodule).


## Dataset Submission Process

The VEDA user docs explain the full [dataset submission process](https://nasa-impact.github.io/veda-docs/contributing/dataset-ingestion/).

Ultimately, submission to the VEDA catalog requires that you [open an issue with the "new dataset" template](https://github.com/NASA-IMPACT/veda-data/issues/new?assignees=&labels=dataset&projects=&template=new-dataset.yaml&title=New+Dataset%3A+%3Cdataset+title%3E). This template will require, at minimum:

1. a description of the dataset
2. the location of the data (in S3, CMR, etc.), and 
3. a point of contact for the VEDA team to collaborate with. 

One or more notebooks showing how the data should be processed would be appreciated.


## JSON Data Structure

When submitting STAC records to ingest, a pull request can be made with the data structured as described below. 

### `collections/`

The `json_data/collections/` directory holds json files representing the data for VEDA collection metadata (STAC).

Should follow the following format:

```json
{
    "id": "<collection-id>",
    "type": "Collection",
    "links":[
    ],
    "title":"<collection-title>",
    "extent":{
        "spatial":{
            "bbox":[
                [
                    "<min-longitude>",
                    "<min-latitude>",
                    "<max-longitude>",
                    "<max-latitude>",
                ]
            ]
        },
        "temporal":{
            "interval":[
                [
                    "<start-date>",
                    "<end-date>",
                ]
            ]
        }
    },
    "license":"MIT",
    "description": "<collection-description>",
    "stac_version": "1.0.0",
    "dashboard:is_periodic": "<true/false>",
    "dashboard:time_density": "<month/>day/year>",
    "item_assets": {
        "cog_default": {
            "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            "roles": [
                "data",
                "layer"
            ],
            "title": "Default COG Layer",
            "description": "Cloud optimized default layer to display on map"
        }
    }
}

```

### `step_function_inputs/`

The `json_data/step_function_inputs/` directory holds json files representing the step function inputs for initiating the discovery, ingest and publication workflows.
Can either be a single input event or a list of input events.

Should follow the following format:

```json
{
    "collection": "<collection-id>",
    "discovery": "<s3/cmr>",

    ## for s3 discovery
    "prefix": "<s3-key-prefix>",
    "bucket": "<s3-bucket>",
    "filename_regex": "<filename-regex>",
    "datetime_range": "<month/day/year>",
    
    ## for cmr discovery
    "version": "<collection-version>",
    "temporal": ["<start-date>", "<end-date>"],
    "bounding_box": ["<bounding-box-as-comma-separated-LBRT>"],
    "include": "<filename-pattern>",    

# Information about the scripts.
The repository contain multiple scripts to convert different types of netCDF or geotiff files to COGs. Below is the information about the scripts present in the repo:

* **odiac_netcdf_to_cog_transformation** : You need to download the netcdf ODIAC dataset from  https://db.cger.nies.go.jp/dataset/ODIAC/DL_odiac2022.html . Once downloaded, we can use this script to convert the raw netCDFs into COGs. For tracking purposes, this script also creates a csv file which contains the names of the all the files that have been transformed from the given dataset. A JSON file is also created which contains the metadata from the dataset.

* **odiac_geotiff_to_cog_transformation** : You need to download the ODIAC dataset from  https://db.cger.nies.go.jp/dataset/ODIAC/DL_odiac2022.html . Once downloaded, we can use this script to convert the geotiffs into COGs. For tracking purposes, this script also creates a csv file which contains the names of the all the files that have been transformed from the given dataset. The dataset does not provide any meaningful metadata that could be stored into a json file.

* **nex_cmip6_netcdf_to_cog_transformation** : The code directly reads the CMIP6 netcdf files from the NEX bucket and transforms them into COGs. The transformed COGs are then stored into the bucket specified in the code (for now it is cmip6-staging in the covid response AWS account). The code also allows us to keep a track of files that have been converted by storing their names in a .csv file which is then cross checked with the csv file that is present in the NEX bucket. Only the files which have not been previously transformed are read from the bucket and transformed when we run the code.
## In progress




    ### misc
    "cogify": "<true/false>",
    "upload": "<true/false>",
    "dry_run": "<true/false>",
}
```