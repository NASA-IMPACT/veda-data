"""
Supports Airflow 2 and 3 (API v1 / v2)
"""

import os
import uuid
import json
import http.client

from typing import Dict, Any
from base64 import b64encode


class AirflowAPIError(Exception):
    pass


def _build_request_body_v2(
    conf: Dict[str, Any], dag_id: str, note: str = ""
) -> Dict[str, Any]:
    """Build the request body for Airflow 2 API v1"""
    return {
        "conf": conf,
        "dag_run_id": f"{dag_id}-{uuid.uuid4()}",
        "note": note or "Run from GitHub Actions veda-data workflow",
    }


def _build_request_body_v3(
    conf: Dict[str, Any], dag_id: str, note: str = ""
) -> Dict[str, Any]:
    """Build the request body for Airflow 3 API v2"""
    return {
        "conf": conf,
        "dag_run_id": f"{dag_id}-{uuid.uuid4()}",
        "note": note or "Run from GitHub Actions veda-data workflow",
    }


def trigger_dag_run(
    base_api_url: str,
    dag_id: str,
    conf: Dict[str, Any],
    username: str,
    password: str,
    api_version: str = None,
) -> Dict[str, Any]:
    """
    Trigger a DAG run with version-aware API handling

    Raises: AirflowAPIError if it fails
    """

    if api_version is None:
        api_version = os.getenv("AIRFLOW_API_VERSION", "3")

    if api_version == "2":
        request_body = _build_request_body_v2(conf, dag_id)
        api_path = f"/api/v1/dags/{dag_id}/dagRuns"
    else:
        request_body = _build_request_body_v3(conf, dag_id)
        api_path = f"/api/v2/dags/{dag_id}/dagRuns"

    api_token = b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + api_token,
    }

    try:
        http_conn = http.client.HTTPSConnection(base_api_url)
        http_conn.request("POST", api_path, json.dumps(request_body), headers)
        response = http_conn.getresponse()
        response_data = response.read()
        http_conn.close()

        if response.status >= 400:
            raise AirflowAPIError(
                f"Airflow API v{api_version} returns "
                f"{response.status}: {response_data.decode()}"
            )

        return {
            "statusCode": response.status,
            "body": response_data.decode(),
        }

    except http.client.HTTPException as e:
        raise AirflowAPIError(f"HTTP error: {str(e)}")
