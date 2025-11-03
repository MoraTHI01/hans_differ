#!/usr/bin/env python
"""
ConnectorProvider class.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import json
import os
import logging

from modules.connectors.airflow_connector import AirflowConnector
from modules.connectors.minio_connector import MinioConnector
from modules.connectors.mongo_connector import MongoConnector
from modules.connectors.opensearch_connector import OpensearchConnector


class ConnectorProvider:
    """
    ConnectorProvider is responsible for
    initializing all connectors with a given config.
    Used by flask to access the configured connectors.
    """

    def __init__(self):
        name = __class__.__name__
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        log_ch = logging.StreamHandler()
        log_ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_ch.setFormatter(formatter)
        self._logger.addHandler(log_ch)
        self._initialized = False
        self._configured = False
        self._airflow_connector = None
        self._assetdb_connector = None
        self._mediadb_connector = None
        self._metadb_connector = None
        # Default configuration using docker network to backend
        self._airflow_config = {
            "host": "host.docker.internal",
            "port": "8080",
            "user": "airflow",
            "password": "airflow",
        }
        self._assetdb_config = {
            "host": "assetdb",
            "port": "9001",
            "user": "minio",
            "password": "minio123",
        }
        self._mediadb_config = {
            "host": "mediadb",
            "port": "9000",
            "user": "minio",
            "password": "minio123",
        }
        self._metadb_config = {
            "host": "metadb",
            "port": "27017",
            "user": "root",
            "password": "password",
            "database": "meta",
        }
        self._opensearch_config = {
            "host": "searchengine",
            "port": "9200",
            "user": "admin",
            "password": "admin",
        }

    def configure_with_env(self):
        """
        Configure all connectors using environment variables

        """
        self._airflow_config["host"] = os.environ["AIRFLOW_HOST"]
        self._airflow_config["port"] = os.environ["AIRFLOW_PORT"]
        self._airflow_config["user"] = os.environ["AIRFLOW_ROOT_USER"]
        self._airflow_config["password"] = os.environ["AIRFLOW_ROOT_PASSWORD"]

        self._assetdb_config["host"] = os.environ["MINIO_ASSETDB_HOST"]
        self._assetdb_config["port"] = os.environ["MINIO_ASSETDB_PORT"]
        self._assetdb_config["user"] = os.environ["MINIO_ASSETDB_ROOT_USER"]
        self._assetdb_config["password"] = os.environ["MINIO_ASSETDB_ROOT_PASSWORD"]

        self._mediadb_config["host"] = os.environ["MINIO_MEDIADB_HOST"]
        self._mediadb_config["port"] = os.environ["MINIO_MEDIADB_PORT"]
        self._mediadb_config["user"] = os.environ["MINIO_MEDIADB_ROOT_USER"]
        self._mediadb_config["password"] = os.environ["MINIO_MEDIADB_ROOT_PASSWORD"]

        self._metadb_config["host"] = os.environ["MONGO_METADB_HOST"]
        self._metadb_config["port"] = os.environ["MONGO_METADB_PORT"]
        self._metadb_config["user"] = os.environ["MONGO_METADB_ROOT_USER"]
        self._metadb_config["password"] = os.environ["MONGO_METADB_ROOT_PASSWORD"]
        self._metadb_config["database"] = os.environ["MONGO_METADB_DATABASE"]

        self._opensearch_config["host"] = os.environ["OPENSEARCH_HOST"]
        self._opensearch_config["port"] = os.environ["OPENSEARCH_PORT"]
        self._opensearch_config["user"] = os.environ["OPENSEARCH_ROOT_USER"]
        self._opensearch_config["password"] = os.environ["OPENSEARCH_ROOT_PASSWORD"]

        self._init_connectors()
        self._configured = True
        self._logger.info("Configured!")

    def configure(self, json_config):
        """
        Configure all connectors

        :param str json_config: JSON string with configuration for all connectors
        """
        self._logger.info("Configure: %s", json_config)
        # TODO: Parse json config from outside to configure connectors
        self._init_connectors()
        self._configured = True
        self._logger.info("Configured!")

    def _init_connectors(self):
        """
        Initialize all connectors
        """
        self._airflow_connector = AirflowConnector(
            self._airflow_config["host"],
            self._airflow_config["port"],
            self._airflow_config["user"],
            self._airflow_config["password"],
        )

        self._assetdb_connector = MinioConnector(
            self._assetdb_config["host"],
            self._assetdb_config["port"],
            self._assetdb_config["user"],
            self._assetdb_config["password"],
        )

        self._mediadb_connector = MinioConnector(
            self._mediadb_config["host"],
            self._mediadb_config["port"],
            self._mediadb_config["user"],
            self._mediadb_config["password"],
        )

        self._metadb_connector = MongoConnector(
            self._metadb_config["host"],
            self._metadb_config["port"],
            self._metadb_config["user"],
            self._metadb_config["password"],
            self._metadb_config["database"],
        )

        self._opensearch_connector = OpensearchConnector(
            self._opensearch_config["host"],
            self._opensearch_config["port"],
            self._opensearch_config["user"],
            self._opensearch_config["password"],
        )

        self._initialized = True
        return self._initialized

    def get_airflow_connector(self):
        """
        Provide configured AirflowConnector
        """
        return self._airflow_connector

    def get_assetdb_connector(self):
        """
        Provide configured AssetDBConnector
        """
        return self._assetdb_connector

    def get_assetdb_connector_with_auth(self, user, password):
        """
        Provide configured AssetDBConnector with different auth
        """
        return MinioConnector(self._assetdb_config["host"], self._assetdb_config["port"], user, password)

    def get_mediadb_connector(self):
        """
        Provide configured MediaDBConnector
        """
        return self._mediadb_connector

    def get_mediadb_connector_with_auth(self, user, password):
        """
        Provide configured MediaDBConnector with different auth
        """
        return MinioConnector(self._mediadb_config["host"], self._mediadb_config["port"], user, password)

    def get_metadb_connector(self):
        """
        Provide configured MetaDBConnector
        """
        return self._metadb_connector

    def get_opensearch_connector(self):
        """
        Provide configured OpensearchConnector
        """
        return self._opensearch_connector


connector_provider = ConnectorProvider()
connector_provider.configure_with_env()
