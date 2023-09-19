#!/usr/bin/env python3

"""Validates all collections in ingestion-data/collections"""

import json
import sys
from pathlib import Path

from pystac import Collection, STACValidationError

root = Path(__file__).parents[1]
collections = root / "ingestion-data" / "collections"

errors = dict()
for path in collections.rglob("*.json"):
    try:
        collection = Collection.from_file(str(path))
    except Exception as error:
        errors[path.name] = {
            "type": "error",
            "message": f"cannot read collection, {type(error)}: {error}",
        }
        continue
    try:
        collection.validate()
    except STACValidationError as error:
        if isinstance(error.source, list):
            message = [str(e) for e in error.source]
        else:
            message = str(error.source)
        errors[path.name] = {
            "type": "invalid",
            "message": message,
        }

if errors:
    json.dump(errors, sys.stdout, indent=2)
    sys.exit(1)
