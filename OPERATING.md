# Operating Guide: Data Transformation and Ingest for VEDA

This guide provides information on how VEDA runs data ingest, transformation and metadata (STAC) publication workflows via AWS Services, such as step functions.

NOTE: Since collection ingest still requires calling the database from a local machine, users must add their IP to an inbound rule on the security group attached to the RDS instance.

## Data

### `collections/`

The `collections/` directory holds json files representing the data for VEDA collection metadata (STAC).

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

The `step_function_inputs/` directory holds json files representing the step function inputs for initiating the discovery, ingest and publication workflows.
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