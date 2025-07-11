from typing import Dict, Any

import http.client
import json
import sys
import os
import uuid
from base64 import b64encode


def trigger_collection_dag(payload: Dict[str, Any], stage: str):
    """
    Triggers the veda_collection_pipeline DAG in either staging or production SM2A.
    """
    dag_name = "veda_collection_pipeline"

    if stage == "staging":
        api_url_env = "STAGING_SM2A_API_URL"
        username_env = "STAGING_SM2A_ADMIN_USERNAME"
        password_env = "STAGING_SM2A_ADMIN_PASSWORD"
    elif stage == "production":
        api_url_env = "SM2A_API_URL"
        username_env = "SM2A_ADMIN_USERNAME"
        password_env = "SM2A_ADMIN_PASSWORD"
    else:
        raise ValueError(
            f"Invalid stage provided: {stage}. Must be 'staging' or 'production'."
        )

    base_api_url = os.getenv(api_url_env)
    username = os.getenv(username_env)
    password = os.getenv(password_env)

    if not all([base_api_url, username, password]):
        raise ValueError(
            f"Missing one or more environment variables: "
            f"stage is None={stage is None}, "
            f"username is None={username_env is None}, "
            f"password is None={password_env is None}"
        )

    api_token = b64encode(f"{username}:{password}".encode()).decode()

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + api_token,
    }

    body = {
        **payload,
        "dag_run_id": f"{dag_name}-{uuid.uuid4()}",
        "note": "Run from GitHub Actions veda-data",
    }
    http_conn = http.client.HTTPSConnection(base_api_url)
    http_conn.request(
        "POST", f"/api/v1/dags/{dag_name}/dagRuns", json.dumps(body), headers
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
