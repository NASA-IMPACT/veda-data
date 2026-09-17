"""
Supports Airflow 2 and 3 (API v1 / v2)
"""

import os
import uuid
import json
import http.client
import urllib.parse

from typing import Dict, Any
from base64 import b64encode


class AirflowAPIError(Exception):
    pass


def _build_request_body(
    conf: Dict[str, Any],
    dag_id: str,
    note: str = "",
    logical_date=None,
) -> Dict[str, Any]:
    """Build the request body for the DagRun"""
    body = {
        "conf": conf,
        "dag_run_id": f"{dag_id}-{uuid.uuid4()}",
        "note": note or "Run from GitHub Actions veda-data workflow",
    }
    if logical_date:
        body["logical_date"] = logical_date
    return body


def _get_oauth2_token() -> str:
    """Get OAuth2 access token from Airflow API"""
    keycloak_url = os.getenv("KEYCLOAK_URL")
    keycloak_realm = os.getenv("KEYCLOAK_REALM")
    client_id = os.getenv("KEYCLOAK_CLIENT_ID")
    client_secret = os.getenv("KEYCLOAK_CLIENT_SECRET")

    if not all([keycloak_url, keycloak_realm, client_id, client_secret]):
        raise AirflowAPIError("Missing Keycloak environment variables")

    token_endpoint = (
        f"{keycloak_url}/realms/{keycloak_realm}/protocol/openid-connect/token"
    )
    print(f"Token endpoint is is : {token_endpoint}")

    parsed_url = urllib.parse.urlparse(token_endpoint)
    host = parsed_url.hostname
    path = (
        f"{parsed_url.path}?{parsed_url.query}" if parsed_url.query else parsed_url.path
    )

    data = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
    )
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        http_conn = http.client.HTTPSConnection(host)
        http_conn.request("POST", path, data, headers)
        response = http_conn.getresponse()
        response_data = json.loads(response.read().decode())
        http_conn.close()

        if response.status != 200:
            raise AirflowAPIError(f"Login failed: {response_data}")

        token = response_data["access_token"]
        print(f"Token beginning is : {token[:50]}")
        return token
    except AirflowAPIError:
        raise
    except Exception as e:
        raise AirflowAPIError(f"Failed to get Keycloak token: {str(e)}")


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
    request_body = _build_request_body(conf, dag_id)

    if api_version == "2":
        api_token = b64encode(f"{username}:{password}".encode()).decode()
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic " + api_token,
        }
    else:
        access_token = _get_oauth2_token()
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
