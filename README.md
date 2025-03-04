# veda-data

[![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/nasa-impact/veda-data/ci.yaml?style=for-the-badge&label=CI)](https://github.com/NASA-IMPACT/veda-data/actions/workflows/ci.yaml)

This repository houses config data used to load datasets into the [VEDA catalog](https://nasa-impact.github.io/veda-docs/services/apis.html). Inclusion in the VEDA catalog is a prerequisite for displaying datasets in the [VEDA Dashboard](https://www.earthdata.nasa.gov/dashboard/).

The config data provided here gets processed in the [veda-data-airflow](https://github.com/NASA-IMPACT/veda-data-airflow) ingestion system. See [Dataset Submission Process](#dataset-submission-process) for details about submitting work to the ingestion system.

## Dataset submission process

![veda-data-publication][veda-data-publication]

> [!NOTE]
> See these links for technical details about the automated publishing methods veda-data provides:
>
> * [Explanation of the GitHub Actions workflows that publish and promote data](/docs/gh-actions-publish-and-promote-workflows)
> * [Automated publish design doc](/docs/publishing-data-annotated)

To add data to VEDA you will:

### Step 1: Stage your files

Upload files to the staging bucket `s3://veda-data-store-staging` (which you can do with a VEDA JupyterHub account--request access [here](https://docs.openveda.cloud/user-guide/scientific-computing/getting-access.html)) or a self-hosted bucket in s3 has shared read access to VEDA service. [See docs.openveda.cloud for additional details on preparing files.](https://docs.openveda.cloud/user-guide/content-curation/dataset-ingestion/file-preparation.html)

### Step 2: Generate STAC metadata in the staging catalog

Metadata must first be added to the Staging Catalog [staging.openveda.cloud/api/stac](https://staging.openveda.cloud/api/stac). You will need to create a dataset config file using the veda-ingest-ui to generate STAC Collection metadata and generate Item records for the files you have uploaded in Step 1.

* Use the veda-ingest-ui form to generate a dataset config and open a veda-data PR

* OR manually generate a dataset-config JSON and open a veda-data PR

* When a veda-data PR is opened, a github action will automatically (1) POST the config to airflow and stage the collection and items in the staging catalog instance and (2) open a veda-config dashboard preview for the dataset.

> See detailed steps for the [dataset submission process](https://docs.openveda.cloud/user-guide/content-curation/dataset-ingestion/) in the Content Curation section of the User Guide in [veda-docs](https://nasa-impact.github.io/veda-docs) where you can also find this full ingestion workflow example [geoglam ingest notebook](https://docs.openveda.cloud/user-guide/content-curation/dataset-ingestion/example-template/example-geoglam-ingest.html)

### Step 3: Acceptance testing

Perform acceptance testing appropriate for your data. This should include reviewing the [staging.openveda.cloud STAC browser](https://staging.openveda.cloud) and reviewing the corresponding veda-config PR dashboard preview.

> See the [Content Curation/Dashboard Configuration](https://docs.openveda.cloud/user-guide/content-curation/dashboard-configuration/) section of the User Guide in docs.openveda.cloud for more information about configuring a dashboard preview.

### Step 4: Promote to production

After acceptance testing, request approval--when your PR is merged, the dataset config JSON will be used to generate records in the production VEDA catalog!

> You can manually run the dataset promotion pipeline instead of using an ingestion tool or the automated github actions in this repo. The promotion configuration can be created from a copy of the staging dataset config with an additional field `transfer` which should be true if s3 objects need to be transferred to the produciton data store. Please open a PR to add the promotion configuration to [`ingestion-data/production/promotion-config`](#productionpromotion-config).

### Step 5 [Optional]: Share your data

* Share your data in the VEDA Dashboard [User Guide > Content Curation > Dashboard Configuration](https://docs.openveda.cloud/user-guide/content-curation/dashboard-configuration/)

* Add JupyterHub hosted usage examples to docs.openveda.cloud [User Guide > Content Curation > Usage Example Notebook Submission](https://docs.openveda.cloud/user-guide/content-curation/docs-and-notebooks.html)

## Project ingestion data structure

When submitting STAC records for ingestion, a pull request can be made with the data structured as described below. The `ingestion-data/` directory contains artifacts of the ingestion configuration used to publish to the staging and production catalogs.

> **Note**
Various ingestion workflows are supported and documented below but only the configuration metadata used to publish to the VEDA catalog are stored in this repo. It is not expected that every ingestion will follow exactly the same pattern nor will each ingested collection have have all types of configuration metadata here. The primary method used to ingest is [**`dataset-config`**](#stagedataset-config).

### `<stage>/collections/`

The `ingestion-data/collections/` directory holds json files representing the data for VEDA collection metadata (STAC). STAC Collection metadata can be generated from an id, title, description using Pystac. See [User Guide > Content Curation > Dataset Ingestion > STAC Collection Creation](https://docs.openveda.cloud/user-guide/notebooks/veda-operations/stac-collection-creation.html) to get started.

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

The `ingestion-data/dataset-config/` directory holds JSON files that can be used with the `dataset/publish` workflows endpoint, combining both collection metadata and discovery items. For an example of this ingestion workflow, see this [geoglam ingest notebook in the Content Curation section of the VEDA User Guide](https://docs.openveda.cloud/user-guide/content-curation/dataset-ingestion/example-template/example-geoglam-ingest.html).

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

### `production/promotion-config`

This directory contains the configuration needed to execute a stand-alone airflow DAG that transfers assets to production and generates production metadata. The promotion-config json uses the same schema and values from the [staging/dataset-config JSON](#stagedataset-config) with an additional `transfer` field which should be set to true when S3 objects need to be transferred from a staging location to the production data store. The veda data promotion pipeline copies data from a specified staging bucket and prefix to a permanent location in `s3://veda-data-store` using the collection_id as a prefix and publishes STAC metadata to the produciton catalog.

<details>
  <summary><b>production/promotion-config/collection_id.json</b></summary>

```json
{
    "transfer": true,
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
