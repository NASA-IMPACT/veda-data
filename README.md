# veda-data

[![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/nasa-impact/veda-data/ci.yaml?style=for-the-badge&label=CI)](https://github.com/NASA-IMPACT/veda-data/actions/workflows/ci.yaml)

This repository houses data used to define a VEDA dataset to load into the [VEDA catalog](https://nasa-impact.github.io/veda-docs/services/apis.html). Inclusion in the VEDA catalog is a prerequisite for displaying the dataset in the [VEDA Dashboard](https://www.earthdata.nasa.gov/dashboard/).

The data provided here gets processed in the ingestion system [veda-data-airflow](https://github.com/NASA-IMPACT/veda-data-airflow), to which this repository is directly linked (as a Git submodule).

## Dataset Submission Process

The VEDA user docs explain the full [dataset submission process](https://nasa-impact.github.io/veda-docs/contributing/dataset-ingestion/).

Ultimately, submission to the VEDA catalog requires that you [open an issue with the "new dataset" template](https://github.com/NASA-IMPACT/veda-data/issues/new?assignees=&labels=dataset&projects=&template=new-dataset.yaml&title=New+Dataset%3A+%3Cdataset+title%3E). This template will require, at minimum:

1. a description of the dataset
2. the location of the data (in S3, CMR, etc.), and
3. a point of contact for the VEDA team to collaborate with.

One or more notebooks showing how the data should be processed would be appreciated.

## Ingestion Data Structure

When submitting STAC records to ingest, a pull request can be made with the data structured as described below.

### `collections/`

The `ingestion-data/collections/` directory holds json files representing the data for VEDA collection metadata (STAC).

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

### `step-function-inputs/`

The `ingestion-data/step-function-inputs/` directory holds json files representing the step function inputs for initiating the discovery, ingest and publication workflows.
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

## Validation

This repository provides a script for validating all collections.
First, install the requirements (preferably in a virtual environment):

```shell
pip install -r requirements.txt
```

Then:

```shell
python scripts/validate_collections.py
```

## Development

We use [pre-commit](https://pre-commit.com/) hooks to keep our notebooks and Python scripts consistently formatted.
To contribute, first install the requirements, then install the **pre-commit** hooks:

```shell
pip install -r requirements.txt  # recommend a virtual environment
pre-commit install
```

The hooks will run automatically on any changed files when you commit.
To run the hooks on the entire repository (which is what happens in CI):

```shell
pre-commit run --all-files
```

If you need to add a Python dependency, add your dependency to `requirements.in`:
Then run:

```shell
pip-compile
```

This will update `requirements.txt` with a complete, realized set of Python dependencies.
