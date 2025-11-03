#!/usr/bin/env python
"""
ConnectorProvider class.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import logging
from typing import Any, Dict, Optional
import os

from modules.connectors.minio_connector import MinioConnector


class ConnectorProvider:
    """
    ConnectorProvider is responsible for
    initializing all connectors with a given config.
    Used by airflow operators to access the configured connectors.
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
        self._assetdbtemp_connector = None
        # Default configuration
        self._assetdbtemp_config = {"host": "assetdb-temp", "port": "9002", "user": "minio", "password": "minio123"}

    def configure(self, json_config: Optional[Dict[str, Any]] = None):
        """
        Configure all connectors.

        Configuration is done by the json_config if provided.
        If the no config is provided as a parameter, env variables will be used.
        The fallback for both approaches are the default values for the connection.

        :param json_config: Optional JSON string with configuration for all connectors
        """
        if json_config is not None:
            self._logger.info("Configuring connector provider: %s", json_config)
            try:
                # Using Airflow Connection format
                config_assetdb_temp = json_config["assetdb_temp"]
                self._assetdbtemp_config = {
                    "host": config_assetdb_temp["host"],
                    "port": str(config_assetdb_temp["port"]),
                    "user": config_assetdb_temp["login"],
                    "password": config_assetdb_temp["password"],
                }
            except:
                self._logger.info("Invalid configuration, using default configuration!")
        else:
            # Using config from environment variables, if set
            self._assetdbtemp_config = self._use_env_variables_for_config()

        self._init_connectors()
        self._configured = True
        self._logger.info("Configured!")

    def _use_env_variables_for_config(self) -> Dict[str, str]:
        self._logger.info("Configure connector provider based on environment variables (if set, otherwise default)")
        return {
            "host": os.getenv("HANS_ML_BACKEND_ASSETDB_TEMP_HOST", self._assetdbtemp_config["host"]),
            "port": os.getenv("HANS_ML_BACKEND_ASSETDB_TEMP_PORT", self._assetdbtemp_config["port"]),
            "login": os.getenv("HANS_ML_BACKEND_ASSETDB_TEMP_ROOT_USER", self._assetdbtemp_config["login"]),
            "password": os.getenv("HANS_ML_BACKEND_ASSETDB_TEMP_ROOT_PASSWORD", self._assetdbtemp_config["password"]),
        }

    def _init_connectors(self):
        """
        Initialize all connectors
        """
        self._assetdbtemp_connector = MinioConnector(
            self._assetdbtemp_config["host"],
            self._assetdbtemp_config["port"],
            self._assetdbtemp_config["user"],
            self._assetdbtemp_config["password"],
        )

        self._initialized = True
        return self._initialized

    def get_assetdbtemp_connector(self):
        """
        Provide configured AssetDBTempConnector
        """
        return self._assetdbtemp_connector

    def get_assetdbtemp_connector_width_auth(self, user, password):
        """
        Provide configured MediaDBConnector with different auth
        """
        return MinioConnector(self._assetdbtemp_config["host"], self._assetdbtemp_config["port"], user, password)


connector_provider = ConnectorProvider()
