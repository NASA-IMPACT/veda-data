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


def _build_request_body(
    conf: Dict[str, Any], dag_id: str, note: str = "", api_version: str = "3"
) -> Dict[str, Any]:
    """Build the request body for the DagRun"""
    run_id = os.getenv("GITHUB_RUN_ID")
    if run_id:
        run_url = (
            f"{os.getenv('GITHUB_SERVER_URL')}/{os.getenv('GITHUB_REPOSITORY')}"
            f"/actions/runs/{run_id}"
        )
        default_note = f"Run from GitHub Actions: {run_url}"
    else:
        default_note = "Run from GitHub Actions veda-data workflow"

    body = {
        "conf": conf,
        "dag_run_id": f"{dag_id}-{uuid.uuid4()}",
        "note": note or default_note,
    }
    if api_version != "2":
        body["logical_date"] = None
    return body


def _generate_jwt_token(secret: str, sub: str, expiration_time: int = 3600) -> str:
    """Generate a HS512 JWT Token for Airflow API authentication"""
    import jwt
    import time

    payload = {
        "iss": "airflow",
        "sub": sub,
        "aud": "apache-airflow",
        "nbf": int(time.time()),
        "iat": int(time.time()),
        "exp": int(time.time()) + expiration_time,
    }
    return jwt.encode(payload, secret, algorithm="HS512")


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

    api_path = f"/api/v{'1' if api_version == '2' else '2'}/dags/{dag_id}/dagRuns"
    request_body = _build_request_body(conf, dag_id, api_version=api_version)

    if api_version == "2":
        api_token = b64encode(f"{username}:{password}".encode()).decode()
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic " + api_token,
        }
    else:
        jwt_secret = os.getenv("AIRFLOW_JWT_SECRET")
        if not jwt_secret:
            raise AirflowAPIError("AIRFLOW_JWT_SECRET environment variable not set")
        jwt_sub = os.getenv("AIRFLOW_JWT_SUB")
        if not jwt_sub:
            raise AirflowAPIError("AIRFLOW_JWT_SUB environment variable not set")
        access_token = _generate_jwt_token(jwt_secret, jwt_sub)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
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

    except AirflowAPIError:
        raise
    except Exception as e:
        raise AirflowAPIError(f"Failed to trigger the DAG run: {str(e)}")
