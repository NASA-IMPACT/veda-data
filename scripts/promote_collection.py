from typing import Dict, Any

import json
import sys
import os

from scripts.airflow_api import AirflowAPIError, trigger_dag_run


def trigger_collection_dag(payload: Dict[str, Any], stage: str):
    """
    Triggers the veda_collection_pipeline DAG in either staging or production SM2A.
    """
    dag_name = "veda_collection_pipeline"

    if stage == "staging":
        api_url_env = "STAGING_SM2A_API_URL"
        username_env = "STAGING_SM2A_ADMIN_USERNAME"
        password_env = "STAGING_SM2A_ADMIN_PASSWORD"
        api_version_env = "STAGING_AIRFLOW_API_VERSION"
    elif stage == "production":
        api_url_env = "SM2A_API_URL"
        username_env = "SM2A_ADMIN_USERNAME"
        password_env = "SM2A_ADMIN_PASSWORD"
        api_version_env = "PRODUCTION_AIRFLOW_API_VERSION"
    else:
        raise ValueError(
            f"Invalid stage provided: {stage}. Must be 'staging' or 'production'."
        )

    base_api_url = os.getenv(api_url_env)
    username = os.getenv(username_env)
    password = os.getenv(password_env)
    api_version = os.getenv(api_version_env, "3")  # default to Airflow version 3?

    if not all([base_api_url, username, password]):
        raise ValueError(
            f"Missing one or more environment variables: "
            f"stage is None={stage is None}, "
            f"username is None={username_env is None}, "
            f"password is None={password_env is None}"
        )

    assert base_api_url is not None
    assert username is not None
    assert password is not None

    try:
        result = trigger_dag_run(
            base_api_url=base_api_url,
            dag_id=dag_name,
            conf=payload.get("conf", {}),
            username=username,
            password=password,
            api_version=api_version,
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
            input_data = json.load(file)
            stage = sys.argv[2]
            dag_payload = {"conf": input_data}
            trigger_collection_dag(dag_payload, stage)

    except IndexError:
        print("Usage: promote_collection.py <file_name> <stage>")
    except FileNotFoundError:
        print(f"Error: File '{sys.argv[1]}' not found.")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON content in file {sys.argv[1]}")
