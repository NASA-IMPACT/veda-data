#! /usr/bin/env python
"""
This file creates a minimal <collection>.data.mdx file
from the input dataset config json file
Dependency: `dataset.mdx` file
"""

import yaml
import os
import sys
import requests

base_json = {
    "id": "",
    "name": "",
    "featured": False,
    "description": "",
    "media": {
        "src": "https://bootstrap-cheatsheet.themeselection.com/assets/images/bs-images/img-2x1.png",
        "alt": "Placeholder image",
        "author": {"name": "Media author", "url": ""},
    },
    "taxonomy": [
        {"name": "Source", "values": ["NASA"]},
        {"name": "Topics", "values": ["Agriculture", "Biomass", "Landcover"]},
    ],
    "infoDescription": """::markdown
        - **Temporal Extent:** 2015 - 2100
        - **Temporal Resolution:** Annual
        - **Spatial Extent:** Global
        - **Spatial Resolution:** 0.25 degrees x 0.25 degrees
        - **Data Units:** Days (Days per year above 90°F or 110°F)
        - **Data Type:** Research
    """,
    "layers": [],
}


def define_source_params(input_data):
    # TODO. Temp shortcut assumes single renders configuration with key 'dashboard'
    # for all assets
    source_params = {}
    # legend_type = "gradient"
    if renders := input_data.get("renders", None):
        if default_renders := renders.get("dashboard", None):
            # hack remove title if present
            if default_renders.get("title", None):
                default_renders.pop("title")

            # hack custom categorical colormaps don't need rescale
            # but veda-ui may use a default if not provided
            if not default_renders.get("rescale", None):
                default_renders["rescale"] = [
                    [0, 255]
                ]  # @QUESTION: This isn't being parsed correctly
                # legend_type = "categorical"  # assumption

            source_params = default_renders
            return source_params


# TODO We need to first preview the data in staging,
# the staging stac_api should be an env variable
staging_stac_api = "https://staging.openveda.cloud/api/stac"
staging_raster_api = "https://staging.openveda.cloud/api/raster"


def define_layer_data(item_assets, collection_id, source_params, legend):
    layers = []
    for asset_id, asset in item_assets:
        layer = {
            "id": f"{collection_id}-{asset_id}",
            "stacCol": collection_id,
            "stacApiEndpoint": staging_stac_api,  # TODO remove when promoting to prod
            "tileApiEndpoint": staging_raster_api,  # TODO remove when promoting to prod
            "name": asset.get("title", "Asset Title"),
            "type": "raster",
            "description": asset.get("description", "Asset Description"),
            "zoomExtent": [0, 4],
            "sourceParams": source_params,
            "compare": {
                "datasetId": collection_id,
                "layerId": asset_id,
                "mapLabel": (
                    "::js ({ dateFns, datetime, compareDatetime }) "
                    "=> {if (dateFns && datetime && compareDatetime)"
                    "return `${dateFns.format(datetime, 'yyyy')} "
                    "VS ${dateFns.format(compareDatetime, 'yyyy')}`;}"
                ),
            },
            "analysis": {"exclude": False, "metrics": ["mean"]},
            "legend": legend,
            "info": {
                "source": "NASA",
                "spatialExtent": "Global",
                "temporalResolution": "Annual",
                "unit": "Days",
            },
        }
        layers.append(layer)
    return layers


def define_legend(legend_type):
    # TODO this hack works around some legend needs that are not in stac metadata
    legend_gradient = {
        "unit": {"label": "Days"},
        "type": "gradient",
        "min": 0,
        "max": 365,
        "stops": [
            "#E4FF7A",
            "#FAED2D",
            "#FFCE0A",
            "#FFB100",
            "#FE9900",
            "#FC7F00",
        ],
    }

    legend_categorical = {
        "type": "categorical",
        "min": 0,
        "max": 255,
        "stops": [
            {"color": "#486DA2", "label": "Category 1"},
            {"color": "#E7EFFC", "label": "Category 2"},
            {"color": "#E1CDCE", "label": "Category 3"},
        ],
    }
    return legend_gradient if legend_type == "gradient" else legend_categorical


def generate_dataset_config_json(input_data):
    """
    Creates json based on input dataset config
    """
    collection_id = input_data["id"]
    legend_type = "gradient"
    source_params = define_source_params(input_data)
    if not source_params.get("rescale", None):
        legend_type = "categorical"  # assumption

    legend = define_legend(legend_type)
    item_assets = input_data.get("item_assets", {}).items()
    layers = define_layer_data(item_assets, collection_id, source_params, legend)

    json_data = base_json
    json_data["id"] = collection_id
    json_data["name"] = input_data.get("title", "Dataset Title")
    json_data["description"] = input_data.get("description", "Dataset Description")
    json_data["layers"] = layers

    return json_data


def transform_json_to_yaml(json_data):
    # Convert json to yaml for frontmatter
    yaml_data = yaml.dump(json_data, sort_keys=False)
    return yaml_data


def safe_open_w(path):
    """Open "path" for writing, creating any parent directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, "w")


if __name__ == "__main__":
    collection_id = sys.argv[1]
    if ".json" in collection_id:
        collection_id = os.path.basename(collection_id).replace(".json", "")

    # todo this should be in env config
    stac_api = "https://staging.openveda.cloud/api/stac"
    input_data = requests.get(f"{stac_api}/collections/{collection_id}").json()

    # dataset_config = create_frontmatter(input_data)
    dataset_config_json = generate_dataset_config_json(input_data)
    dataset_config_yaml = transform_json_to_yaml(dataset_config_json)

    # front_matter = f"---\n{dataset_config}---\n"
    front_matter = f"---\n{dataset_config_yaml}---\n"

    # Path to the existing file
    curr_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(curr_directory, "dataset.mdx")

    # Read the existing content of the file
    with open(file_path, "r") as file:
        existing_content = file.read()

    # Combine front matter and existing content
    new_content = front_matter + existing_content

    # Write the combined content back to the file
    mdx_path = f"../ingestion-data/dataset-mdx/{collection_id.lower()}.data.mdx"
    output_filepath = os.path.join(
        curr_directory,
        mdx_path,
    )
    with safe_open_w(output_filepath) as ofile:
        ofile.write(new_content)

    print(collection_id)
