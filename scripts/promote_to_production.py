from typing import Dict, Any
from urllib.parse import urljoin

import json
import sys
import os
import subprocess


class MissingFieldError(Exception):
    pass


def validate_discovery_item_config(item: Dict[str, Any]) -> Dict[str, Any]:
    if "bucket" not in item:
        raise MissingFieldError(
            "Missing required field 'bucket' in discovery item: {item}"
        )
    # if "datetime_range" not in item:
    #     raise MissingFieldError(
    #         "Missing required field 'datetime_range' in discovery item: {item}"
    #     )
    if "discovery" not in item:
        raise MissingFieldError(
            "Missing required field 'discovery' in discovery item: {item}"
        )
    if "filename_regex" not in item:
        raise MissingFieldError(
            "Missing required field 'filename_regex' in discovery item: {item}"
        )
    if "prefix" not in item:
        raise MissingFieldError(
            "Missing required field 'prefix' in discovery item: {item}"
        )
    return item


def promote_to_production(dag_input):
    base_api_url = os.getenv("SM2A_API_URL", "")
    promotion_dag = os.getenv("PROMOTION_DAG_NAME", "veda_promotion_pipeline")
    path = urljoin("api/v1/dags/", promotion_dag)
    full_api_url = urljoin(base_api_url, path)

    api_token = os.getenv("SM2A_DEV_BASIC_AUTH_SECRET")
    print(f"DAG INPUT: ${dag_input}")

    if not full_api_url or not api_token:
        raise ValueError(
            "SM2A_API_URL or SM2A_DEV_BASIC_AUTH_SECRET is not"
            + "set in the environment variables."
        )

    print(f"FULL API URL ${full_api_url}")

    curl_command = [
        "curl",
        "-X",
        "GET",
        "-H",
        f"Authorization: Basic {api_token}",
        full_api_url,
    ]

    try:
        result = subprocess.run(
            curl_command, capture_output=True, text=True, check=True
        )
        print("SM2A API Response:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error during SM2A API request")
        print(e.stderr)
        raise


if __name__ == "__main__":
    try:
        with open(sys.argv[1], "r") as file:
            input = json.load(file)
            discovery_items = input.get("discovery_items")
            validated_discovery_items = [
                validate_discovery_item_config(item) for item in discovery_items
            ]

            dag_input = {
                "collection": input.get("collection"),
                "data_type": input.get("data_type"),
                "description": input.get("description"),
                "discovery_items": validated_discovery_items,
                "is_periodic": input.get("is_periodic", "true"),
                "time_density": input.get("time_density"),
                "title": input.get("title"),
                "transfer": input.get("transfer", "false"),
            }
            promote_to_production(dag_input)

    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON content in file {sys.argv[1]}")
