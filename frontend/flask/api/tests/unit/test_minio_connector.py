#!/usr/bin/env python
"""
Test minio storage connector
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import pytest
from connectors.minio_connector import MinioConnector


@pytest.fixture
def connector_valid():
    """
    Provide a valid configured MinioConnector for testing.
    """
    return MinioConnector("assetdb", "9001", "minio", "minio123")


@pytest.fixture
def connector_invalid():
    """
    Provide an invalid configured MinioConnector for testing.
    """
    return MinioConnector("localhost", "0", "minio", "minio123")


def test_init(connector_valid):
    """
    Test creation of a MinioConnector instance
    """
    assert connector_valid is not None


def test_connect_valid(connector_valid):
    """
    Test connection of a valid MinioConnector instance
    """
    assert connector_valid.connect() is True


def test_disconnect_valid(connector_valid):
    """
    Test closing connection of a valid MinioConnector instance
    """
    assert connector_valid.disconnect() is True


def test_connect_invalid(connector_invalid):
    """
    Test connection of an invalid MinioConnector instance
    """
    assert connector_invalid.connect() is False


def test_gen_presigned_url(connector_valid):
    """
    Test to receive a pre-signed url for Sintel.test.pdf stored in Minio assetdb in bucket raw.
    """
    assert connector_valid.connect() is True
    obj = connector_valid.gen_presigned_url("assetdb:raw:Sintel.test.pdf")
    print(obj)
    assert obj is not None
    assert "Sintel.test.pdf" in obj


def test_gen_all_presigned_url(connector_valid):
    """
    Test to receive all pre-signed url for all stored items in Minio assetdb bucket raw.
    """
    assert connector_valid.connect() is True
    obj = connector_valid.gen_all_presigned_url("assetdb:raw")
    print(obj)
    assert obj is not None
    for element in obj:
        assert "Sintel.test" in element[0]


def test_get_metadata(connector_valid):
    """
    Test to receive metadata for Sintel.test.pdf stored in Minio assetdb in bucket raw.
    """
    assert connector_valid.connect() is True
    obj = connector_valid.get_metadata("assetdb:raw:Sintel.test.pdf")
    print(obj)
    assert obj is not None
    assert obj["Content-Type"] == "application/pdf"
