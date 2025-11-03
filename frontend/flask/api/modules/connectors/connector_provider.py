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
import os

from api.modules.config import get_backend_assetdb_host, get_backend_assetdb_password
from api.modules.config import get_backend_assetdb_port, get_backend_assetdb_user
from api.modules.config import get_backend_mediadb_host, get_backend_mediadb_password
from api.modules.config import get_backend_mediadb_port, get_backend_mediadb_user
from api.modules.config import get_backend_metadb_database, get_backend_metadb_host
from api.modules.config import get_backend_metadb_password, get_backend_metadb_port, get_backend_metadb_user
from api.modules.config import get_backend_opensearch_host, get_backend_opensearch_password
from api.modules.config import get_backend_opensearch_port, get_backend_opensearch_user
from api.modules.config import get_ml_backend_host, get_ml_backend_password
from api.modules.config import get_ml_backend_port, get_ml_backend_user, get_ml_backend_postfix
from api.modules.config import get_ml_service_llm_host, get_ml_service_llm_password
from api.modules.config import get_ml_service_llm_port, get_ml_service_llm_user
from api.modules.config import get_ml_service_llm_model_id, get_ml_service_llm_max_new_tokens
from api.modules.config import get_ml_service_vllm_host, get_ml_service_vllm_password
from api.modules.config import get_ml_service_vllm_port, get_ml_service_vllm_user
from api.modules.config import get_ml_service_vllm_model_id, get_ml_service_vllm_max_new_tokens
from api.modules.config import get_ml_service_embedding_host, get_ml_service_embedding_password
from api.modules.config import get_ml_service_embedding_port, get_ml_service_embedding_user
from api.modules.config import get_ml_service_translation_host, get_ml_service_translation_password
from api.modules.config import get_ml_service_translation_port, get_ml_service_translation_user
from api.modules.config import (
    get_ml_service_orchestrator_llm_flag,
    get_ml_service_orchestrator_translation_flag,
    get_ml_service_orchestrator_embedding_flag,
)
from api.modules.config import (
    get_ml_service_orchestrator_llm_route,
    get_ml_service_orchestrator_translation_route,
    get_ml_service_orchestrator_embedding_route,
)
from api.modules.config import get_ml_service_orchestrator_vllm_route, get_ml_service_orchestrator_vllm_flag
from api.modules.config import get_ml_service_orchestrator_host, get_ml_service_orchestrator_port
from api.modules.config import get_ml_service_orchestrator_user, get_ml_service_orchestrator_password

from api.modules.connectors.airflow_connector import AirflowConnector
from api.modules.connectors.minio_connector import MinioConnector
from api.modules.connectors.mongo_connector import MongoConnector
from api.modules.connectors.opensearch_connector import OpensearchConnector
from api.modules.connectors.llm_connector import LlmConnector
from api.modules.connectors.vllm_connector import VLlmConnector
from api.modules.connectors.embedding_connector import EmbeddingConnector
from api.modules.connectors.translation_connector import TranslationConnector


class ConnectorProvider:
    """
    ConnectorProvider is responsible for
    initializing all connectors with a given config.
    Used by flask to access the configured connectors.
    """

    def __init__(self):
        name = __class__.__name__
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.ERROR)
        log_ch = logging.StreamHandler()
        log_ch.setLevel(logging.ERROR)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_ch.setFormatter(formatter)
        self._logger.addHandler(log_ch)
        self._initialized = False
        self._configured = False
        self._airflow_connector = None
        self._assetdb_connector = None
        self._mediadb_connector = None
        self._metadb_connector = None
        self._opensearch_connector = None
        self._llm_connector = None
        self._vllm_connector = None
        # Default configuration using docker network to backend
        airflow_port = os.getenv("HANS_ML_BACKEND_AIRFLOW_PORT")
        self._airflow_config = {
            "host": "host.docker.internal",
            "port": airflow_port,
            "postfix": "/",
            "user": "airflow",
            "password": "airflow",
        }
        assetdb_port = os.getenv("HANS_BACKEND_ASSETDB_PORT")
        self._assetdb_config = {"host": "assetdb", "port": assetdb_port, "user": "minio", "password": "minio123"}
        mediadb_port = os.getenv("HANS_BACKEND_MEDIADB_PORT")
        self._mediadb_config = {"host": "mediadb", "port": mediadb_port, "user": "minio", "password": "minio123"}
        metadb_port = os.getenv("HANS_BACKEND_METADB_PORT")
        self._metadb_config = {
            "host": "metadb",
            "port": metadb_port,
            "user": "root",
            "password": "password",
            "database": "meta",
        }
        opensearch_port = os.getenv("HANS_BACKEND_OPENSEARCH_PORT")
        self._opensearch_config = {
            "host": "searchengine",
            "port": opensearch_port,
            "user": "admin",
            "password": "admin",
        }
        orchestrator_port = os.getenv("HANS_ML_SERVICE_ORCHESTRATOR_PORT")
        llm_port = os.getenv("HANS_ML_SERVICE_LLM_PORT")
        self._llm_config = {
            "llm_host": "host.docker.internal",
            "llm_port": llm_port,
            "llm_user": "admin",
            "llm_password": "admin",
            "orchestrator_host": "host.docker.internal",
            "orchestrator_port": orchestrator_port,
            "orchestrator_user": "admin",
            "orchestrator_password": "admin",
            "orchestrator_llm_route": "llm_service",
            "use_orchestrator": False,
        }
        vllm_port = os.getenv("HANS_ML_SERVICE_VLLM_PORT")
        self._vllm_config = {
            "vllm_host": "host.docker.internal",
            "vllm_port": vllm_port,
            "vllm_user": "admin",
            "vllm_password": "admin",
            "orchestrator_host": "host.docker.internal",
            "orchestrator_port": orchestrator_port,
            "orchestrator_user": "admin",
            "orchestrator_password": "admin",
            "orchestrator_llm_route": "vllm_service",
            "use_orchestrator": False,
        }
        embedding_port = os.getenv("HANS_ML_SERVICE_EMBEDDING_PORT")
        orchestrator_port = os.getenv("HANS_ML_SERVICE_ORCHESTRATOR_PORT")
        self._embedding_config = {
            "embedding_host": "host.docker.internal",
            "embedding_port": embedding_port,
            "embedding_user": "admin",
            "embedding_password": "admin",
            "orchestrator_host": "host.docker.internal",
            "orchestrator_port": orchestrator_port,
            "orchestrator_user": "admin",
            "orchestrator_password": "admin",
            "orchestrator_embedding_route": "embedding_service",
            "use_orchestrator": False,
        }
        translation_port = os.getenv("HANS_ML_SERVICE_TRANSLATION_PORT")
        orchestrator_port = os.getenv("HANS_ML_SERVICE_ORCHESTRATOR_PORT")
        self._translation_config = {
            "translation_host": "host.docker.internal",
            "translation_port": translation_port,
            "translation_user": "admin",
            "translation_password": "admin",
            "orchestrator_host": "host.docker.internal",
            "orchestrator_port": orchestrator_port,
            "orchestrator_user": "admin",
            "orchestrator_password": "admin",
            "orchestrator_translation_route": "translation_service",
            "use_orchestrator": False,
        }

    def configure(self):
        """
        Configure all connectors

        :param str json_config: JSON string with configuration for all connectors
        """
        self._logger.info("Configure")
        self._airflow_config["host"] = get_ml_backend_host()
        self._airflow_config["port"] = get_ml_backend_port()
        self._airflow_config["postfix"] = get_ml_backend_postfix()
        self._airflow_config["user"] = get_ml_backend_user()
        self._airflow_config["password"] = get_ml_backend_password()

        self._assetdb_config["host"] = get_backend_assetdb_host()
        self._assetdb_config["port"] = get_backend_assetdb_port()
        self._assetdb_config["user"] = get_backend_assetdb_user()
        self._assetdb_config["password"] = get_backend_assetdb_password()

        self._mediadb_config["host"] = get_backend_mediadb_host()
        self._mediadb_config["port"] = get_backend_mediadb_port()
        self._mediadb_config["user"] = get_backend_mediadb_user()
        self._mediadb_config["password"] = get_backend_mediadb_password()

        self._metadb_config["host"] = get_backend_metadb_host()
        self._metadb_config["port"] = get_backend_metadb_port()
        self._metadb_config["user"] = get_backend_metadb_user()
        self._metadb_config["password"] = get_backend_metadb_password()
        self._metadb_config["database"] = get_backend_metadb_database()

        self._opensearch_config["host"] = get_backend_opensearch_host()
        self._opensearch_config["port"] = get_backend_opensearch_port()
        self._opensearch_config["user"] = get_backend_opensearch_user()
        self._opensearch_config["password"] = get_backend_opensearch_password()

        self._llm_config["llm_host"] = get_ml_service_llm_host()
        self._llm_config["llm_port"] = get_ml_service_llm_port()
        self._llm_config["llm_user"] = get_ml_service_llm_user()
        self._llm_config["llm_password"] = get_ml_service_llm_password()
        self._llm_config["llm_model_id"] = get_ml_service_llm_model_id()
        self._llm_config["llm_max_new_tokens"] = get_ml_service_llm_max_new_tokens()
        self._llm_config["orchestrator_host"] = get_ml_service_orchestrator_host()
        self._llm_config["orchestrator_port"] = get_ml_service_orchestrator_port()
        self._llm_config["orchestrator_user"] = get_ml_service_orchestrator_user()
        self._llm_config["orchestrator_password"] = get_ml_service_orchestrator_password()
        self._llm_config["orchestrator_llm_route"] = get_ml_service_orchestrator_llm_route()
        self._llm_config["use_orchestrator"] = get_ml_service_orchestrator_llm_flag()

        self._vllm_config["vllm_host"] = get_ml_service_vllm_host()
        self._vllm_config["vllm_port"] = get_ml_service_vllm_port()
        self._vllm_config["vllm_user"] = get_ml_service_vllm_user()
        self._vllm_config["vllm_password"] = get_ml_service_vllm_password()
        self._vllm_config["vllm_model_id"] = get_ml_service_vllm_model_id()
        self._vllm_config["vllm_max_new_tokens"] = get_ml_service_vllm_max_new_tokens()
        self._vllm_config["orchestrator_host"] = get_ml_service_orchestrator_host()
        self._vllm_config["orchestrator_port"] = get_ml_service_orchestrator_port()
        self._vllm_config["orchestrator_user"] = get_ml_service_orchestrator_user()
        self._vllm_config["orchestrator_password"] = get_ml_service_orchestrator_password()
        self._vllm_config["orchestrator_vllm_route"] = get_ml_service_orchestrator_vllm_route()
        self._vllm_config["use_orchestrator"] = get_ml_service_orchestrator_vllm_flag()

        self._embedding_config["embedding_host"] = get_ml_service_embedding_host()
        self._embedding_config["embedding_port"] = get_ml_service_embedding_port()
        self._embedding_config["embedding_user"] = get_ml_service_embedding_user()
        self._embedding_config["embedding_password"] = get_ml_service_embedding_password()
        self._embedding_config["orchestrator_host"] = get_ml_service_orchestrator_host()
        self._embedding_config["orchestrator_port"] = get_ml_service_orchestrator_port()
        self._embedding_config["orchestrator_user"] = get_ml_service_orchestrator_user()
        self._embedding_config["orchestrator_password"] = get_ml_service_orchestrator_password()
        self._embedding_config["orchestrator_embedding_route"] = get_ml_service_orchestrator_embedding_route()
        self._embedding_config["use_orchestrator"] = get_ml_service_orchestrator_embedding_flag()

        self._translation_config["translation_host"] = get_ml_service_translation_host()
        self._translation_config["translation_port"] = get_ml_service_translation_port()
        self._translation_config["translation_user"] = get_ml_service_translation_user()
        self._translation_config["translation_password"] = get_ml_service_translation_password()
        self._translation_config["orchestrator_host"] = get_ml_service_orchestrator_host()
        self._translation_config["orchestrator_port"] = get_ml_service_orchestrator_port()
        self._translation_config["orchestrator_user"] = get_ml_service_orchestrator_user()
        self._translation_config["orchestrator_password"] = get_ml_service_orchestrator_password()
        self._translation_config["orchestrator_translation_route"] = get_ml_service_orchestrator_translation_route()
        self._translation_config["use_orchestrator"] = get_ml_service_orchestrator_translation_flag()

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
            self._airflow_config["postfix"],
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

        self._llm_connector = LlmConnector(
            self._llm_config["llm_host"],
            self._llm_config["llm_port"],
            self._llm_config["llm_user"],
            self._llm_config["llm_password"],
            self._llm_config["llm_model_id"],
            self._llm_config["llm_max_new_tokens"],
            self._llm_config["orchestrator_host"],
            self._llm_config["orchestrator_port"],
            self._llm_config["orchestrator_user"],
            self._llm_config["orchestrator_password"],
            self._llm_config["orchestrator_llm_route"],
            self._llm_config["use_orchestrator"],
        )

        self._vllm_connector = VLlmConnector(
            self._vllm_config["vllm_host"],
            self._vllm_config["vllm_port"],
            self._vllm_config["vllm_user"],
            self._vllm_config["vllm_password"],
            self._vllm_config["vllm_model_id"],
            self._vllm_config["vllm_max_new_tokens"],
            self._vllm_config["orchestrator_host"],
            self._vllm_config["orchestrator_port"],
            self._vllm_config["orchestrator_user"],
            self._vllm_config["orchestrator_password"],
            self._vllm_config["orchestrator_vllm_route"],
            self._vllm_config["use_orchestrator"],
        )

        self._embedding_connector = EmbeddingConnector(
            self._embedding_config["embedding_host"],
            self._embedding_config["embedding_port"],
            self._embedding_config["embedding_user"],
            self._embedding_config["embedding_password"],
            self._embedding_config["orchestrator_host"],
            self._embedding_config["orchestrator_port"],
            self._embedding_config["orchestrator_user"],
            self._embedding_config["orchestrator_password"],
            self._embedding_config["orchestrator_embedding_route"],
            self._embedding_config["use_orchestrator"],
        )

        self._translation_connector = TranslationConnector(
            self._translation_config["translation_host"],
            self._translation_config["translation_port"],
            self._translation_config["translation_user"],
            self._translation_config["translation_password"],
            self._translation_config["orchestrator_host"],
            self._translation_config["orchestrator_port"],
            self._translation_config["orchestrator_user"],
            self._translation_config["orchestrator_password"],
            self._translation_config["orchestrator_translation_route"],
            self._translation_config["use_orchestrator"],
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

    def get_llm_connector(self):
        """
        Provide configured LlmConnector
        """
        return self._llm_connector

    def get_vllm_connector(self):
        """
        Provide configured VLlmConnector
        """
        return self._vllm_connector

    def get_embedding_connector(self):
        """
        Provide configured EmbeddingConnector
        """
        return self._embedding_connector

    def get_translation_connector(self):
        """
        Provide configured TranslationConnector
        """
        return self._translation_connector


connector_provider = ConnectorProvider()
connector_provider.configure()
