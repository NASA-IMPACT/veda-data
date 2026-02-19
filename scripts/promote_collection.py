from typing import Dict, Any

import http.client
import json
import sys
import os
import uuid
import requests


def trigger_collection_dag(payload: Dict[str, Any], stage: str):
    """
    Triggers the veda_collection_pipeline DAG in either staging or production SM2A.
    """
    dag_name = "veda_collection_pipeline"

    if stage == "staging":
        api_url_env = "STAGING_SM2A_API_URL"
        token_url = f"https://{os.getenv('KEYCLOAK_STAGING_URL')}/realms/veda/protocol/openid-connect/token"
        client_id = "airflow-webserver-fab"
        client_secret = os.getenv("KEYCLOAK_STAGING_SM2A_FAB_CLIENT_SECRET")
    elif stage == "production":
        api_url_env = "SM2A_API_URL"
        token_url = f"https://{os.getenv('KEYCLOAK_PROD_URL')}/realms/veda/protocol/openid-connect/token"
        client_id = "airflow-webserver-fab"
        client_secret = os.getenv("KEYCLOAK_PROD_SM2A_FAB_CLIENT_SECRET")
    else:
        raise ValueError(
            f"Invalid stage provided: {stage}. Must be 'staging' or 'production'."
        )

    base_api_url = os.getenv(api_url_env)

    response = requests.post(
        token_url,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        },
    )
    access_token = response.json()["access_token"]

    if not all([base_api_url, access_token]):
        raise ValueError(
            f"Missing one or more environment variables: "
            f"stage is None={stage is None}, "
            f"access_token is None={access_token is None}"
        )

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
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
