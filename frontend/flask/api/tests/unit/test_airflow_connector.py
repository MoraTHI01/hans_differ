#!/usr/bin/env python
"""
Test airflow connector
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


from pathlib import Path
from uuid import uuid4
import pytest
from api.modules.connectors.airflow_connector import AirflowConnector

DATA_PATH = Path(__file__).parent.joinpath("data/")


@pytest.fixture
def connector_valid():
    """
    Provide a valid configured AirflowConnector for testing.
    """
    return AirflowConnector("host.docker.internal", "8080", "airflow", "airflow")


@pytest.fixture
def connector_invalid():
    """
    Provide an invalid configured AirflowConnector for testing.
    """
    return AirflowConnector("localhost", "8080", "airflow", "airflow")


def test_init(connector_valid):
    """
    Test creation of a AirflowConnector instance
    """
    assert connector_valid is not None


def test_connect_valid(connector_valid):
    """
    Test connection of a valid AirflowConnector instance
    """
    assert connector_valid.connect() is True


def test_disconnect_valid(connector_valid):
    """
    Test closing connection of a valid AirflowConnector instance
    """
    assert connector_valid.disconnect() is True


def test_connect_invalid(connector_invalid):
    """
    Test connection of an invalid AirflowConnector instance
    """
    assert connector_invalid.connect() is False


def test_get_dags(connector_valid):
    """
    Test to receive all available DAG's from apache airflow.
    """
    assert connector_valid.connect() is True
    dag_collection = connector_valid.get_dags()
    print(dag_collection)
    found = False
    for item in dag_collection["dags"]:
        if item["dag_id"] == "test_dag_v1":
            found = True
    assert found is True


def test_post_dag_run(connector_valid):
    """
    Test to start a DAG on apache airflow.
    """
    assert connector_valid.connect() is True
    dag_uuid = str(uuid4())
    dag_config = {"test": {"test": "test"}}
    assert connector_valid.post_dag_run("test_dag_v1", dag_uuid, dag_config) is True
    dag_run_collection = connector_valid.get_running_dags()
    print(dag_run_collection)
    found = False
    for item in dag_run_collection["dag_runs"]:
        if item["dag_id"] == "test_dag_v1":
            found = True
    assert found is True
