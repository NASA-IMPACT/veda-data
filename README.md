# veda-data

[![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/nasa-impact/veda-data/ci.yaml?style=for-the-badge&label=CI)](https://github.com/NASA-IMPACT/veda-data/actions/workflows/ci.yaml)

This repository houses config data used to load datasets into the [VEDA catalog](https://nasa-impact.github.io/veda-docs/services/apis.html). Inclusion in the VEDA catalog is a prerequisite for displaying datasets in the [VEDA Dashboard](https://www.earthdata.nasa.gov/dashboard/).

The config data provided here gets processed in the [veda-data-airflow](https://github.com/NASA-IMPACT/veda-data-airflow) ingestion system. See [Dataset Submission Process](#dataset-submission-process) for details about submitting work to the ingestion system.

## Dataset submission process

![veda-data-publication][veda-data-publication]

To add data to VEDA you will:

1. **Stage your files:** Upload files to the staging bucket `s3://veda-data-store-staging` (which you can do with a VEDA JupyterHub account--request access [here](https://nasa-impact.github.io/veda-docs/services/jupyterhub.html)) or a self-hosted bucket in s3 has shared read access to VEDA service.

2. **Generate STAC metadata in the staging catalog:** Metadata must first be added to the Staging Catalog [staging.openveda.cloud/api/stac](https://staging.openveda.cloud/api/stac). You will need to create a dataset config file and submit it to the `/workflows/dataset/publish` endpoint to generate STAC Collection metadata and generate Item records for the files you have uploaded in Step 1. See detailed steps for the [dataset submission process](https://nasa-impact.github.io/veda-docs/contributing/dataset-ingestion/) in the contribuing section of [veda-docs](https://nasa-impact.github.io/veda-docs) where you can also find this full ingestion workflow example [geoglam ingest notebook](https://nasa-impact.github.io/veda-docs/contributing/dataset-ingestion/example-template/example-geoglam-ingest.html)

3. **Acceptance testing\*:** Perform acceptance testing appropriate for your data. \*In most cases this will be opening a dataset PR in [veda-config](https://github.com/NASA-IMPACT/veda-config) to generate a dashboard preview of the data. See [veda-docs/contributing/dashboard-configuration](https://nasa-impact.github.io/veda-docs/contributing/dashboard-configuration/dataset-configuration.html) for instructions on generating a dashboard preview).

4. **Promote to production!** Open a PR in the [veda-data](https://github.com/NASA-IMPACT/veda-data) repo with the dataset config metadata you used to add your data to the Staging catalog in Step 2. Add your config to `ingestion-data/production/dataset-config`. When your PR is approved, this configuration will be used to generate records in the production VEDA catalog!

5. **[Optional] Share your data :** Share your data in the [VEDA Dashboard](https://www.earthdata.nasa.gov/dashboard/) by submitting a PR to [veda-config](https://github.com/NASA-IMPACT/veda-config) ([see veda-docs/contributing/dashboard-configuration](https://nasa-impact.github.io/veda-docs/contributing/dashboard-configuration/dataset-configuration.html)) and add jupyterhub hosted usage examples to [veda-docs/contributing/docs-and-notebooks](https://nasa-impact.github.io/veda-docs/contributing/docs-and-notebooks.html)

## Project ingestion data structure

When submitting STAC records for ingestion, a pull request can be made with the data structured as described below. The `ingestion-data/` directory contains artifacts of the ingestion configuration used to publish to the staging and production catalogs.

> **Note**
Various ingestion workflows are supported and documented below but only the configuration metadata used to publish to the VEDA catalog are stored in this repo. It is not expected that every ingestion will follow exactly the same pattern nor will each ingested collection have have all types of configuration metadata here. The primary method used to ingest is [**`dataset-config`**](#stagedataset-config).

### `<stage>/collections/`

The `ingestion-data/collections/` directory holds json files representing the data for VEDA collection metadata (STAC). STAC Collection metadata can be generated from an id, title, description using Pystac. See this [veda-docs/contributing notebook example](https://nasa-impact.github.io/veda-docs/notebooks/veda-operations/stac-collection-creation.html) to get started.

Should follow the following format:

<details>
  <summary><b>/collections/collection_id.json</b></summary>

```json
{
    "id": "<collection-id>",
    "type": "Collection",
    "links":[
    ],
    "title":"<collection-title>",
    "description": "<collection-description>",
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
    "stac_extensions": [
        "https://stac-extensions.github.io/render/v1.0.0/schema.json",
        "https://stac-extensions.github.io/item-assets/v1.0.0/schema.json"
    ],
    "stac_version": "1.0.0",
    "license": "CC0-1.0",
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
    },
    "providers": [
        {
            "name": "NASA VEDA",
            "url": "https://www.earthdata.nasa.gov/dashboard/",
            "roles": [
                "host"
            ]
        }
    ],
    "renders": {
        "dashboard": {
            "colormap_name": "<colormap_name>",
            "rescale": [
                [
                    "<min_rescale>",
                    "<max_rescale>"
                ]
            ],
            "nodata": "nan",
            "assets": [
                "cog_default"
            ],
            "title": "VEDA Dashboard Render Parameters"
        }
    }
}

```

</details>

### `<stage>/discovery-items/`

The `ingestion-data/discovery-items/` directory holds json files representing the inputs for initiating the discovery, ingest and publication workflows.
Can either be a single input event or a list of input events.

Should follow the following format:

<details>
  <summary><b>/discovery-items/collection_id.json</b></summary>

```json
{
    "collection": "<collection-id>",

    ## for s3 discovery
    "prefix": "<s3-key-prefix>",
    "bucket": "<s3-bucket>",
    "filename_regex": "<filename-regex>",
    "datetime_range": "<month/day/year>",

    ### misc
    "dry_run": "<true/false>"
}
```

</details>

### `<stage>/dataset-config/`

The `ingestion-data/dataset-config/` directory holds json files that can be used with the `dataset/publish` workflows endpoint, combining both collection metadata and discovery items. For an example of this ingestion workflow, see this [geoglam ingest notebook in nasa-impact.github.io/veda-docs/contributing/dataset-ingeston](https://nasa-impact.github.io/veda-docs/contributing/dataset-ingestion/example-template/example-geoglam-ingest.html).

<details>
  <summary><b>/dataset-config/collection_id.json</b></summary>

```json
{
    "collection": "<collection-id>",
    "title": "<collection-title>",
    "description": "<collection-description>",
    "type": "cog",
    "spatial_extent": {
        "xmin": -180,
        "ymin": 90,
        "xmax": -90,
        "ymax": 180
    },
    "temporal_extent": {
        "startdate": "<start-date>",
        "enddate": "<end-date>"
    },
    "license": "CC0-1.0",
    "is_periodic": false,
    "time_density": null,
    "stac_version": "1.0.0",
    "discovery_items": [
        {
            "prefix": "<prefix>",
            "bucket": "<bucket>",
            "filename_regex": "<regexß>",
            "discovery": "s3",
            "upload": false
        }
    ]
}

```

</details>

### `production/transfer-config`

This directory contains the configuration needed to execute a stand-alone airflow DAG that copies data from a specified staging bucket and prefix to a permanent location in `s3://veda-data-store` using the collection_id as a prefix.

Should follow the following format:

<details>
  <summary><b>/production/transfer-config/collection_id.json</b></summary>

```json
{
    "collection": "<collection-id>",

    ## the location of the staged files
    "origin_bucket": "<s3-bucket>",
    "origin_prefix": "<s3-key-prefix>",
    "bucket": "<s3-bucket>",
    "filename_regex": "<filename-regex>",

    ### misc
    "dry_run": "<true/false>"
}
```

</details>

## Validation

This repository provides a script for validating all collections in the ingestion-data directory.
First, install the requirements (preferably in a virtual environment):

```shell
pip install -r requirements.txt
```

Then:

```shell
pytest
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

[veda-data-publication]: ./docs/publishing-data.excalidraw.png
