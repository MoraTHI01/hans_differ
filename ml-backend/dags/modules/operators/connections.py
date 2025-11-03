#!/usr/bin/env python
"""
Helpers for handling Airflow connections.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import pendulum
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator


def get_assetdb_temp_config():
    """
    Helper to receive assetdb-temp configuration.
    Uses airflow CONN_ID to receive config for assetdb-temp airflow connection.

    :return: dict Configuration for assetdb-temp
    """
    import json
    from airflow.exceptions import AirflowFailException
    from airflow.hooks.base_hook import BaseHook

    # Using CONN_ID to receive config for assetdb-temp connection
    conn_assetdb_temp = BaseHook.get_connection("assetdb_temp")

    # Configure connector_provider
    return {
        "conn_id": "assetdb_temp",
        "conn_type": conn_assetdb_temp.conn_type,
        "host": conn_assetdb_temp.host,
        "port": conn_assetdb_temp.port,
        "login": conn_assetdb_temp.login,
        "schema": conn_assetdb_temp.schema,
        "password": conn_assetdb_temp.get_password(),
        "bucket": json.loads(conn_assetdb_temp.extra)["bucket"],
        "archive-bucket": json.loads(conn_assetdb_temp.extra)["archive-bucket"],
    }


def get_connection_config(conn_id):
    """
    Helper to receive connection configuration.
    Uses airflow CONN_ID to receive config for airflow connection.

    :param str conn_id: Airflow CONN_ID.

    :return: dict Configuration for connection
    """
    import json
    from airflow.exceptions import AirflowFailException
    from airflow.hooks.base_hook import BaseHook

    # Using CONN_ID to receive config for assetdb-temp connection
    conn = BaseHook.get_connection(conn_id)

    # Configure connector_provider
    return {
        "conn_id": conn_id,
        "conn_type": conn.conn_type,
        "host": conn.host,
        "port": conn.port,
        "schema": conn.schema,
        "login": conn.login,
        "password": conn.get_password(),
    }
