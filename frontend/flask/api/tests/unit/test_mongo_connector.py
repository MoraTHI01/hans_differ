#!/usr/bin/env python
"""
Test mongo db storage connector
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import json
from pathlib import Path
import pytest
from connectors.mongo_connector import MongoConnector


DATA_PATH = Path(__file__).parent.joinpath("data/")


@pytest.fixture
def connector_valid():
    """
    Provide a valid configured MongoConnector for testing.
    """
    return MongoConnector("metadb", "27017", "root", "password", "meta")


@pytest.fixture
def connector_invalid():
    """
    Provide an invalid configured MongoConnector for testing.
    """
    return MongoConnector("localhost", "27018", "root", "password", "meta")


def test_init(connector_valid):
    """
    Test creation of a MongoConnector instance
    """
    assert connector_valid is not None


def test_connect_valid(connector_valid):
    """
    Test connection of a valid MongoConnector instance
    """
    assert connector_valid.connect() is True


def test_disconnect_valid(connector_valid):
    """
    Test closing connection of a valid MongoConnector instance
    """
    assert connector_valid.disconnect() is True


def test_connect_invalid(connector_invalid):
    """
    Test connection of an invalid MongoConnector instance
    """
    assert connector_invalid.connect() is False


def test_put_object(connector_valid):
    """
    Test to store metadata from mongo_entry.json
    in mongo db on server metadb in database meta.
    """
    assert connector_valid.connect() is True
    file = str(DATA_PATH.joinpath("mongo_entry.json"))
    f = open(file, "r", encoding="UTF-8")
    metadata = f.read()
    json_obj = json.loads(metadata)
    uuid = json_obj["uuid"]
    urn_input = f"metadb:meta:post:id:{uuid}"
    success, urn_result = connector_valid.put_object(urn_input, None, "application/json", json_obj)
    assert success is True
    assert urn_result == urn_input


def test_get_metadata(connector_valid):
    """
    Test to receive metadata mongo_entry.json stored
    in mongo db on server metadb in database meta.
    """
    assert connector_valid.connect() is True
    obj = connector_valid.get_metadata("metadb:meta:post:id:fe3d7656-261a-41bd-a616-85c62c0320d2")
    assert obj is not None
    print(obj)
    assert obj["uuid"] == "fe3d7656-261a-41bd-a616-85c62c0320d2"
    assert obj["title"] == "test-mongo-db-entry-title"
