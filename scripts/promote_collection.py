from typing import Dict, Any

import http.client
import json
import sys
import os
import uuid
from base64 import b64encode


class MissingFieldError(Exception):
    pass


def validate_discovery_item_config(item: Dict[str, Any]) -> Dict[str, Any]:
    if "bucket" not in item:
        raise MissingFieldError(
            "Missing required field 'bucket' in discovery item: {item}"
        )
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


def publish_to_staging(payload):
    base_api_url = os.getenv("STAGING_SM2A_API_URL")
    dataset_pipeline_dag = os.getenv("DATASET_DAG_NAME", "veda_dataset_pipeline")
    username = os.getenv("STAGING_SM2A_ADMIN_USERNAME")
    password = os.getenv("STAGING_SM2A_ADMIN_PASSWORD")

    api_token = b64encode(f"{username}:{password}".encode()).decode()

    if not base_api_url or not api_token:
        raise ValueError(
            "STAGING_SM2A_API_URL or STAGING_SM2A_ADMIN_USERNAME"
            + " or STAGING_SM2A_ADMIN_PASSWORD is not"
            + " set in the environment variables."
        )

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + api_token,
    }

    body = {
        **payload,
        "dag_run_id": f"{dataset_pipeline_dag}-{uuid.uuid4()}",
        "note": "Run from GitHub Actions veda-data",
    }
    http_conn = http.client.HTTPSConnection(base_api_url)
    http_conn.request(
        "POST",
        f"/api/v1/dags/{dataset_pipeline_dag}/dagRuns",
        json.dumps(body),
        headers,
    )
    response = http_conn.getresponse()
    response_data = response.read()
    http_conn.close()

    print(json.dumps({"statusCode": response.status}))
    print(response_data.decode())
    return {"statusCode": response.status, "body": response_data.decode()}


def promote_to_production(payload):
    base_api_url = os.getenv("SM2A_API_URL")
    promotion_dag = os.getenv("PROMOTION_DAG_NAME", "veda_promotion_pipeline")
    username = os.getenv("SM2A_ADMIN_USERNAME")
    password = os.getenv("SM2A_ADMIN_PASSWORD")

    api_token = b64encode(f"{username}:{password}".encode()).decode()

    if not base_api_url or not api_token:
        raise ValueError(
            "SM2A_API_URL or SM2A_ADMIN_USERNAME or SM2A_ADMIN_PASSWORD is not"
            + " set in the environment variables."
        )

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + api_token,
    }

    payload["conf"]["transfer"] = True
    body = {
        **payload,
        "dag_run_id": f"{promotion_dag}-{uuid.uuid4()}",
        "note": "Run from GitHub Actions veda-data",
    }
    http_conn = http.client.HTTPSConnection(base_api_url)
    http_conn.request(
        "POST", f"/api/v1/dags/{promotion_dag}/dagRuns", json.dumps(body), headers
    )
    response = http_conn.getresponse()
    response_data = response.read()
    http_conn.close()

    print(json.dumps({"statusCode": response.status}))
    print(response_data.decode())
    return {"statusCode": response.status, "body": response_data.decode()}


if __name__ == "__main__":
    try:
        with open(sys.argv[1], "r") as file:
            input = json.load(file)
            stage = sys.argv[2]
            discovery_items = input.get("discovery_items")
            validated_discovery_items = [
                validate_discovery_item_config(item) for item in discovery_items
            ]
            dag_payload = {"conf": input}
            if stage == "production":
                promote_to_production(dag_payload)
            elif stage == "staging":
                publish_to_staging(dag_payload)

    except IndexError:
        print("Usage: promote_collection.py <file_name> <stage>")
    except FileNotFoundError:
        print(f"Error: File '{sys.argv[1]}' not found.")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON content in file {sys.argv[1]}")
