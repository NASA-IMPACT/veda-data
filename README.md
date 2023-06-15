# veda-data

This repo houses data used to define a VEDA dataset. These datasets are available on the VEDA dashboard (https://www.earthdata.nasa.gov/dashboard/).

For information on how this data gets consumed by the VEDA data ingestion system, see [veda-data-airflow](https://github.com/NASA-IMPACT/veda-data-airflow). This project is also included as a submodule for that repository.

The VEDA user docs explain the [dataset ingestion process](https://nasa-impact.github.io/veda-docs/contributing/dataset-ingestion/).

## Dataset Submission Process

To submit a dataset to the VEDA catalog, please start by opening an issue with the `new-dataset` template. This template will require, at minimum, a description of the dataset, the location of the data (in S3, CMR, etc.), and a point of contact for the VEDA team to collaborate with. One or more notebooks showing how the data should be processed would be appreciated.

If desired, a pull request can be made with the data structured as described below. 

## JSON Data Structure

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
    
    ### misc
    "cogify": "<true/false>",
    "upload": "<true/false>",
    "dry_run": "<true/false>",
}
```