import os
import sys
import json
import requests

changed_files = sys.argv[1]

WORKFLOWS_URL = os.getenv("WORKFLOWS_URL")
publish_url = f"{WORKFLOWS_URL.strip('/')}/dataset/publish"

for file in changed_files:
    dataset_config = json.load(open(file))
    response = requests.post(publish_url, json=dataset_config)
    if response.status_code not in (200, 201):
        raise Exception("Failed publishing because: ", response.text)
