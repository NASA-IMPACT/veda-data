#! /usr/bin/env python
"""
This file creates a minimal <collection>.data.mdx file
from the input dataset config json file
Dependency: `dataset.mdx` file
"""

import yaml
import os
import json
import sys


def create_frontmatter(input_data):
    """
    Creates json based on input dataset config
    """
    collection_id = input_data["collection"]

    json_data = {
        "id": collection_id,
        "name": input_data.get("title", "Dataset Title"),
        "featured": False,
        "description": input_data.get("description", "Dataset Description"),
        "media": {
            "src": "https://bootstrap-cheatsheet.themeselection.com/assets/images/bs-images/img-2x1.png",
            "alt": "Placeholder image",
            "author": {"name": "Media author", "url": ""},
        },
        "taxonomy": [
            {"name": "Theme", "values": ["Greenhouse Gases"]},
            {"name": "Source", "values": ["NASA"]},
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

    for asset_id, asset in input_data.get("item_assets", {}).items():
        layer = {
            "id": f"{collection_id}-{asset_id}",
            "stacCol": collection_id,
            "name": asset.get("title", "Asset Title"),
            "type": "raster",
            "description": asset.get("description", "Asset Description"),
            "zoomExtent": [0, 4],
            "sourceParams": {
                "assets": asset_id,
                "resampling_method": "bilinear",
                "colormap_name": "wistia",
                "rescale": "0,365",
                "maxzoom": 4,
            },
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
            "legend": {
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
            },
            "info": {
                "source": "NASA",
                "spatialExtent": "Global",
                "temporalResolution": "Annual",
                "unit": "Days",
            },
        }
        json_data["layers"].append(layer)

    # Convert json to yaml for frontmatter
    yaml_data = yaml.dump(json_data, sort_keys=False)

    return yaml_data


def safe_open_w(path):
    """Open "path" for writing, creating any parent directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, "w")


if __name__ == "__main__":
    input_data = json.load(open(sys.argv[1]))
    dataset_config = create_frontmatter(input_data)
    front_matter = f"---\n{dataset_config}---\n"

    # Path to the existing file
    curr_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(curr_directory, "dataset.mdx")

    # Read the existing content of the file
    with open(file_path, "r") as file:
        existing_content = file.read()

    # Combine front matter and existing content
    new_content = front_matter + existing_content

    # Write the combined content back to the file
    output_filepath = os.path.join(
        curr_directory,
        f"../ingestion-data/dataset-mdx/{input_data['collection']}.data.mdx",
    )
    with safe_open_w(output_filepath) as ofile:
        ofile.write(new_content)
