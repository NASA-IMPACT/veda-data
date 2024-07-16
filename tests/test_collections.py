from pathlib import Path

import pytest
from pystac import Collection

ROOT = Path(__file__).parents[1]
COLLECTIONS_PATH = ROOT / "ingestion-data" / "production" / "collections"


@pytest.mark.parametrize("path", COLLECTIONS_PATH.rglob("*.json"))
def test_validate(path: Path) -> None:
    collection = Collection.from_file(str(path))
    collection.validate()
