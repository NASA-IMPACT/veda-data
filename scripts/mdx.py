import yaml
import os


input_data = {
  "collection": "climdex-tmaxxf-access-cm2-ssp370",
  "bucket": "veda-data-store-staging",
  "prefix": "climdex-tmaxxf-access-cm2-ssp370/",
  "filename_regex": ".*-ssp370_(.*)_tmax.*.tif",
  "datetime_group": ".*-ssp370_(.*)_tmax.*.tif",
  "datetime_range": "year",
  "assets": {
    "tmax_above_86": {
      "title": "Tmax Above 86",
      "description": "Tmax Above 86",
      "regex": ".*-ssp370_(.*)_tmax_above_86.tif"
    },
    "tmax_above_90": {
      "title": "Tmax Above 90",
      "description": "Tmax Above 90",
      "regex": ".*-ssp370_(.*)_tmax_above_90.tif"
    },
    "tmax_above_100": {
      "title": "Tmax Above 100",
      "description": "Tmax Above 100",
      "regex": ".*-ssp370_(.*)_tmax_above_100.tif"
    },
    "tmax_above_110": {
      "title": "Tmax Above 110",
      "description": "Tmax Above 110",
      "regex": ".*-ssp370_(.*)_tmax_above_110.tif"
    },
    "tmax_above_115": {
      "title": "Tmax Above 115",
      "description": "Tmax Above 115",
      "regex": ".*-ssp370_(.*)_tmax_above_115.tif"
    }
  }
}


def create_frontmatter(input_data):
    collection_id = input_data["collection"]

    json_data = {
        "id": collection_id,
        "name": input_data.get("title", "Dataset Title"),
        "featured": False,
        "description": input_data.get("description", "Dataset Description"),
        "media": {
            "src": "https://bootstrap-cheatsheet.themeselection.com/assets/images/bs-images/img-2x1.png",
            "alt": "Placeholder image",
            "author": {
                "name": "Media author",
                "url": ""
            }
        },
        "taxonomy": [
            {"name": "Theme", "values": ["Greenhouse Gases"]},
            {"name": "Source", "values": ["NASA"]},
        ],
        "infoDescription": "::markdown\n  - **Temporal Extent:** 2015 - 2100\n  - **Temporal Resolution:** Annual\n  - **Spatial Extent:** Global\n  - **Spatial Resolution:** 0.25 degrees x 0.25 degrees\n  - **Data Units:** Days (Days per year above 90°F or 110°F)\n  - **Data Type:** Research",
        "layers": []
    }

    for asset_id, asset in input_data.get("assets", {}).items():
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
                "maxzoom": 4
            },
            "compare": {
                "datasetId": collection_id,
                "layerId": asset_id,
                "mapLabel": "::js ({ dateFns, datetime, compareDatetime }) => {if (dateFns && datetime && compareDatetime) return `${dateFns.format(datetime, 'yyyy')} VS ${dateFns.format(compareDatetime, 'yyyy')}`;}"
            },
            "analysis": {
                "exclude": False,
                "metrics": ["mean"]
            },
            "legend": {
                "unit": {"label": "Days"},
                "type": "gradient",
                "min": 0,
                "max": 365,
                "stops": ["#E4FF7A", "#FAED2D", "#FFCE0A", "#FFB100", "#FE9900", "#FC7F00"]
            },
            "info": {
                "source": "NASA",
                "spatialExtent": "Global",
                "temporalResolution": "Annual",
                "unit": "Days"
            }
        }
        json_data["layers"].append(layer)
    yaml_data = yaml.dump(json_data, sort_keys=False)

    return yaml_data


def safe_open_w(path):
    ''' Open "path" for writing, creating any parent directories as needed.
    '''
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, 'w')


if __name__ == "__main__":
    dataset_config = create_frontmatter(input_data)
    front_matter = f"---\n{dataset_config}---\n"

    # Path to the existing file
    file_path = "dataset.mdx"

    # Read the existing content of the file
    with open(file_path, "r") as file:
        existing_content = file.read()

    # Combine front matter and existing content
    new_content = front_matter + existing_content

    # Write the combined content back to the file
    with safe_open_w(f"../datasets/{input_data['collection']}.data.mdx") as file:
        file.write(new_content)
