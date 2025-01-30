"""
Generate STAC Collections for OCO-3 Zarr stores from JPL

python generate.py ...
"""
import sys
import json
import fsspec
import xarray as xr
from pathlib import Path

import xstac

def generate_collection():
    return {
        "id": "oco3-target-zarrs",
        "description": "OCO-3 target-focused product (TFP) stored as individual Zarr stores. Each individual target is fitted to a localized, configurable grid centered around the target's center.",
        "type": "Collection",
        "title": "OCO-3 Level 3 Target-Focused Zarr Products",
        "stac_version": "1.0.0",
        "links": [
            {
                "rel": "license",
                "title": "EOSDIS Data Use Policy",
                "href": "https://science.nasa.gov/earth-science/earth-science-data/data-information-policy",
            },
            {
                "rel": "about",
                "title": "Github Repository",
                "href": "https://github.com/EarthDigitalTwin/OCO3-data-transformer/"
            }
        ],
        "extent": {
            "spatial": {"bbox": [-180, -90, 180, 90]},
            "temporal": {"interval": [["2014-09-06", "2020-01-01"]]},
        },
        "providers": [
            {
                "name": "NASA VEDA",
                "roles": ["host"],
                "url": "https://earthdata.nasa.gov/dashboard",
            },
            {
                "name": "JPL",
                "roles": ["producer"],
                "url": "https://ocov3.jpl.nasa.gov/sams/index.php",
            },
        ],
        "dashboard:is_periodic": True, 
        "dashboard:time_density": "day"
    }

s3_target_zarr_dir = "s3://sdap-dev-zarr/OCO3/outputs/veda/demo-2024.10.28-target/SIMULTEST_TFP_post_qf/oco3/"
# TODO: add all sites
site_names = ["cal001"]

def generate_item(site_name):
    site_zarr_s3url = f"{s3_target_zarr_dir}/{site_name}.zarr"
    item_template = {
        "id": f"oco3-target-{site_name}",
        "type": "Feature",
        "links": [],
        # TODO
        # "bbox": BBOX[region],
        # "geometry": shapely.geometry.mapping(shapely.geometry.box(*BBOX[region])),
        "stac_version": "1.0.0",
        "properties": {"start_datetime": None, "end_datetime": None},
        "assets": {
            "zarr-s3": {
                "href": site_zarr_s3url,
                "type": "application/vnd+zarr",
                "roles": ["data", "zarr", "s3"],
                "xarray:open_kwargs": {"consolidated": True},
            }
        },
    }

    store = fsspec.get_mapper(site_zarr_s3url)
    ds = xr.open_zarr(store, consolidated=True)
    # may have to insert bbox and geometry here

    item = xstac.xarray_to_stac(
        ds, item_template, temporal_dimension="time", x_dimension="longitude", y_dimension="latitude"
    )

    item_result = item.to_dict(include_self_link=False)

    for link in item_result["links"]:
        if link["rel"] == "root":
            link["href"] = "../catalog.json"
            link["rel"] = str(link["rel"].value)
            link["type"] = str(link["type"].value)

    return item_result


def main(args=None):
    collection = generate_collection()

    outfile = Path(__file__).parent / "collection.json"
    outfile.parent.mkdir(exist_ok=True, parents=True)

    with open(outfile, "w") as f:
        json.dump(collection, f, indent=2)

    # TODO
    # for site_zarr in site_zarrs...
    # outfile = Path(__file__).parent / f"{frequency}/{region}/item.json"

    # with open(outfile, "w") as f:
    #     json.dump(item, f, indent=2)


if __name__ == "__main__":
    sys.exit(main())
