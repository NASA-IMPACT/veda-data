from typing import Dict, Any

import json
import sys
import os

from scripts.airflow_api import AirflowAPIError, trigger_dag_run


class MissingFieldError(Exception):
    pass


def validate_discovery_item_config(item: Dict[str, Any]) -> Dict[str, Any]:
    required_fields = ["bucket", "discovery", "filename_regex", "prefix"]
    for field in required_fields:
        if field not in item:
            raise MissingFieldError(
                f"Missing required field '{field}' in discovery item: {item}"
            )
    return item


def publish_to_staging(payload):
    base_api_url = os.getenv("STAGING_SM2A_API_URL")
    dataset_pipeline_dag = os.getenv("DATASET_DAG_NAME", "veda_dataset_pipeline")
    username = os.getenv("STAGING_SM2A_ADMIN_USERNAME")
    password = os.getenv("STAGING_SM2A_ADMIN_PASSWORD")
    api_version_env = os.getenv("STAGING_AIRFLOW_API_VERSION", "3")

    if not all([base_api_url, username, password]):
        raise ValueError(
            "Missing required env vars STAGING_SM2A_API_URL, "
            "STAGING_SM2A_ADMIN_USERNAME, STAGING_SM2A_ADMIN_PASSWORD"
        )

    assert base_api_url is not None
    assert username is not None
    assert password is not None

    try:
        result = trigger_dag_run(
            base_api_url=base_api_url,
            dag_id=dataset_pipeline_dag,
            conf=payload.get("conf", {}),
            username=username,
            password=password,
            api_version=api_version_env,
        )
        print(json.dumps({"statusCode": result["statusCode"]}))
        print(result["body"])
        return result
    except AirflowAPIError as e:
        print(json.dumps({"statusCode": 500, "error": str(e)}))
        raise


def promote_to_production(payload):
    base_api_url = os.getenv("SM2A_API_URL")
    promotion_dag = os.getenv("PROMOTION_DAG_NAME", "veda_promotion_pipeline")
    username = os.getenv("SM2A_ADMIN_USERNAME")
    password = os.getenv("SM2A_ADMIN_PASSWORD")
    api_version_env = os.getenv("PRODUCTION_AIRFLOW_API_VERSION", "3")

    if not all([base_api_url, username, password]):
        raise ValueError(
            "Missing required env vars SM2A_API_URL, "
            "SM2A_ADMIN_USERNAME, SM2A_ADMIN_PASSWORD"
        )
    assert base_api_url is not None
    assert username is not None
    assert password is not None

    payload["conf"].setdefault("transfer", False)

    try:
        result = trigger_dag_run(
            base_api_url=base_api_url,
            dag_id=promotion_dag,
            conf=payload.get("conf", {}),
            username=username,
            password=password,
            api_version=api_version_env,
        )
        print(json.dumps({"statusCode": result["statusCode"]}))
        print(result["body"])
        return result
    except AirflowAPIError as e:
        print(json.dumps({"statusCode": 500, "error": str(e)}))
        raise


if __name__ == "__main__":
    try:
        with open(sys.argv[1], "r") as file:
            _input = json.load(file)
            stage = sys.argv[2]
            discovery_items = _input.get("discovery_items")
            validated_discovery_items = [
                validate_discovery_item_config(item) for item in discovery_items
            ]
            transfer = _input.get("transfer")
            if transfer is not None and not isinstance(transfer, bool):
                raise ValueError(
                    f"Invalid value for 'transfer': {transfer!r}. Must be a boolean."
                )
            dag_payload = {"conf": _input}
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
