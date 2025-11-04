#!/usr/bin/env python
"""Central point to configure flask app"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import os


# ENVIRONMENT CONFIGURATION


def get_backend_host():
    """Get HAnS backend host
    :return: str Backend host
    """
    _backend_hostname = os.environ.get("HANS_BACKEND_HOST", default="localhost")
    return _backend_hostname.lower()


def get_backend_port():
    """Get HAnS backend host port
    :return: str Backend host port
    """
    _backend_port = os.environ.get("HANS_BACKEND_PORT", default="8089")
    return _backend_port.lower()


def get_backend_protocol():
    """Get HAnS backend protocol
    :return: str Backend protocol
    """
    _backend_protocol = os.environ.get("HANS_BACKEND_PROTOCOL", default="http")
    return _backend_protocol.lower()


def get_backend_host_url():
    """Get HAnS backend host url
    :return: str backend host url
    """
    _backend_host_url = os.environ.get("HANS_BACKEND_HOST_URL", default="localhost:8089")
    return _backend_host_url.lower()


def get_frontend_api_host():
    """Get HAnS frontend api host
    :return: str Frontend api host
    """
    _frontend_api_host = os.environ.get("HANS_FRONTEND_API_HOST", default="0.0.0.0")
    return _frontend_api_host.lower()


def get_frontend_api_port():
    """Get HAnS frontend api port
    :return: str Frontend api port
    """
    _frontend_host_api_port = os.environ.get("HANS_FRONTEND_API_PORT", default="5001")
    return _frontend_host_api_port.lower()


def get_frontend_api_production_mode():
    """Get HAnS frontend api production mode
    :return: bool True if enabled, False otherwise
    """
    _frontend_host_api_prod_mode = os.environ.get("HANS_FRONTEND_API_PRODUCTION_MODE", default="False")
    val = _frontend_host_api_prod_mode.lower()
    if val == "true":
        return True
    elif val == "false":
        return False
    else:
        return False


def get_frontend_host():
    """Get HAnS frontend host
    :return: str Frontend host
    """
    _frontend_hostname = os.environ.get("HANS_FRONTEND_HOST", default="localhost")
    return _frontend_hostname.lower()


def get_frontend_port():
    """Get HAnS frontend host port
    :return: str Frontend host port
    """
    _frontend_port = os.environ.get("HANS_FRONTEND_PORT", default="80")
    return _frontend_port.lower()


def get_frontend_protocol():
    """Get HAnS frontend protocol
    :return: str frontend protocol
    """
    _frontend_protocol = os.environ.get("HANS_FRONTEND_PROTOCOL", default="http")
    return _frontend_protocol.lower()


def get_frontend_host_url():
    """Get HAnS frontend host url
    :return: str Frontend host url
    """
    _frontend_host_url = os.environ.get("HANS_FRONTEND_HOST_URL", default="localhost:80")
    return _frontend_host_url.lower()


def get_ml_backend_host():
    """Get HAnS ml-backend host
    :return: str ml-backend host
    """
    _ml_backend_hostname = os.environ.get("HANS_ML_BACKEND_AIRFLOW_HOST", default="host.docker.internal")
    return _ml_backend_hostname.lower()


def get_ml_backend_postfix():
    """Get HAnS ml-backend postfix
    :return: str ml-backend postfix
    """
    _ml_backend_postfix = os.environ.get("HANS_ML_BACKEND_AIRFLOW_POSTFIX", default="/")
    return _ml_backend_postfix


def get_ml_backend_port():
    """Get HAnS ml-backend host port
    :return: str ml-backend host port
    """
    _ml_backend_port = os.environ.get("HANS_ML_BACKEND_AIRFLOW_PORT", default="8080")
    return _ml_backend_port.lower()


def get_ml_backend_user():
    """Get HAnS ml-backend user
    :return: str ml-backend user
    """
    _ml_backend_user = os.environ.get("HANS_ML_BACKEND_AIRFLOW_ROOT_USER", default="airflow")
    return _ml_backend_user


def get_ml_backend_password():
    """Get HAnS ml-backend password
    :return: str ml-backend password
    """
    _ml_backend_password = os.environ.get("HANS_ML_BACKEND_AIRFLOW_ROOT_PASSWORD", default="airflow")
    return _ml_backend_password


def get_hans_dag_output_connection_ids():
    """Get HAnS ml-backend DAG output config
    Providing Airflow CONN_ID's for backend and frontend,
    see https://airflow.apache.org/docs/apache-airflow/stable/howto/connection.html
    :return: dict CONN_ID's
    """
    _backend_connid = os.environ.get("HANS_BACKEND_CONNID", default="hans_backend")
    _frontend_connid = os.environ.get("HANS_FRONTEND_CONNID", default="hans_frontend")
    return {"backend": _backend_connid, "frontend": _frontend_connid}


# DATABASES

# ASSETDB


def get_backend_assetdb_host():
    """Get HAnS backend assetdb host
    :return: str backend assetdb host
    """
    _backend_assetdb_hostname = os.environ.get("HANS_BACKEND_ASSETDB_HOST", default="assetdb")
    return _backend_assetdb_hostname.lower()


def get_backend_assetdb_port():
    """Get HAnS backend assetdb port
    :return: str backend assetdb port
    """
    _backend_assetdb_port = os.environ.get("HANS_BACKEND_ASSETDB_PORT", default="9001")
    return _backend_assetdb_port.lower()


def get_backend_assetdb_user():
    """Get HAnS backend assetdb user
    :return: str backend assetdb user
    """
    _backend_assetdb_user = os.environ.get("HANS_BACKEND_ASSETDB_ROOT_USER", default="minio")
    return _backend_assetdb_user


def get_backend_assetdb_password():
    """Get HAnS backend assetdb password
    :return: str backend assetdb password
    """
    _backend_assetdb_password = os.environ.get("HANS_BACKEND_ASSETDB_ROOT_PASSWORD", default="minio123")
    return _backend_assetdb_password


# MEDIADB


def get_backend_mediadb_host():
    """Get HAnS backend mediadb host
    :return: str backend mediadb host
    """
    _backend_mediadb_hostname = os.environ.get("HANS_BACKEND_MEDIADB_HOST", default="mediadb")
    return _backend_mediadb_hostname.lower()


def get_backend_mediadb_port():
    """Get HAnS backend mediadb port
    :return: str backend mediadb port
    """
    _backend_mediadb_port = os.environ.get("HANS_BACKEND_MEDIADB_PORT", default="9000")
    return _backend_mediadb_port.lower()


def get_backend_mediadb_user():
    """Get HAnS backend mediadb user
    :return: str backend mediadb user
    """
    _backend_mediadb_user = os.environ.get("HANS_BACKEND_MEDIADB_ROOT_USER", default="minio")
    return _backend_mediadb_user


def get_backend_mediadb_password():
    """Get HAnS backend mediadb password
    :return: str backend mediadb password
    """
    _backend_mediadb_password = os.environ.get("HANS_BACKEND_MEDIADB_ROOT_PASSWORD", default="minio123")
    return _backend_mediadb_password


# METADB


def get_backend_metadb_host():
    """Get HAnS backend metadb host
    :return: str backend metadb host
    """
    _backend_metadb_hostname = os.environ.get("HANS_BACKEND_METADB_HOST", default="metadb")
    return _backend_metadb_hostname.lower()


def get_backend_metadb_port():
    """Get HAnS backend metadb port
    :return: str backend metadb port
    """
    _backend_metadb_port = os.environ.get("HANS_BACKEND_METADB_PORT", default="27017")
    return _backend_metadb_port.lower()


def get_backend_metadb_user():
    """Get HAnS backend metadb user
    :return: str backend metadb user
    """
    _backend_metadb_user = os.environ.get("HANS_BACKEND_METADB_ROOT_USER", default="root")
    return _backend_metadb_user


def get_backend_metadb_password():
    """Get HAnS backend metadb password
    :return: str backend metadb password
    """
    _backend_metadb_password = os.environ.get("HANS_BACKEND_METADB_ROOT_PASSWORD", default="password")
    return _backend_metadb_password


def get_backend_metadb_database():
    """Get HAnS backend metadb database
    :return: str backend metadb database
    """
    _backend_metadb_password = os.environ.get("HANS_BACKEND_METADB_DATABASE", default="meta")
    return _backend_metadb_password


# OPENSEARCH


def get_backend_opensearch_host():
    """Get HAnS backend opensearch host
    :return: str backend opensearch host
    """
    _backend_opensearch_hostname = os.environ.get("HANS_BACKEND_OPENSEARCH_HOST", default="searchengine")
    return _backend_opensearch_hostname.lower()


def get_backend_opensearch_port():
    """Get HAnS backend opensearch port
    :return: str backend opensearch port
    """
    _backend_opensearch_port = os.environ.get("HANS_BACKEND_OPENSEARCH_PORT", default="9200")
    return _backend_opensearch_port.lower()


def get_backend_opensearch_user():
    """Get HAnS backend opensearch user
    :return: str backend opensearch user
    """
    _backend_opensearch_user = os.environ.get("HANS_BACKEND_OPENSEARCH_ROOT_USER", default="admin")
    return _backend_opensearch_user


def get_backend_opensearch_password():
    """Get HAnS backend opensearch password
    :return: str backend opensearch password
    """
    _backend_opensearch_password = os.environ.get("HANS_BACKEND_OPENSEARCH_ROOT_PASSWORD", default="admin")
    return _backend_opensearch_password


def get_backend_opensearch_vector_size():
    """Get HAnS backend opensearch vector size
    :return: int backend opensearch vector size
    """
    _backend_opensearch_vector_size = os.environ.get("HANS_BACKEND_OPENSEARCH_VECTOR_SIZE", default=1024)
    return _backend_opensearch_vector_size


# HANS ML SERVICES ORCHESTRATOR


def get_ml_service_orchestrator_host():
    """Get HAnS ml-service orchestrator host
    :return: str ml-service orchestrator host
    """
    _ml_service_orchestrator_hostname = os.environ.get(
        "HANS_ML_SERVICE_ORCHESTRATOR_HOST", default="host.docker.internal"
    )
    return _ml_service_orchestrator_hostname.lower()


def get_ml_service_orchestrator_port():
    """Get HAnS ml-service orchestrator port
    :return: str ml-service orchestrator port
    """
    _ml_service_orchestrator_port = os.environ.get("HANS_ML_SERVICE_ORCHESTRATOR_PORT", default="8035")
    return _ml_service_orchestrator_port.lower()


def get_ml_service_orchestrator_user():
    """Get HAnS ml-service orchestrator user
    :return: str ml-service orchestrator user
    """
    _ml_service_orchestrator_user = os.environ.get("HANS_ML_SERVICE_ORCHESTRATOR_USER", default="admin")
    return _ml_service_orchestrator_user


def get_ml_service_orchestrator_password():
    """Get HAnS ml-service orchestrator password
    :return: str ml-service orchestrator password
    """
    _ml_service_orchestrator_password = os.environ.get("HANS_ML_SERVICE_ORCHESTRATOR_PASSWORD", default="admin")
    return _ml_service_orchestrator_password


def get_ml_service_orchestrator_llm_flag():
    """Get HAnS ml service llm orchestrator use flag
    :return: bool True if enabled, False otherwise
    """
    _ml_service_orchestrator_llm_flag = os.environ.get("HANS_ML_SERVICE_ORCHESTRATOR_LLM", default="False")
    val = _ml_service_orchestrator_llm_flag.lower()
    if val == "true":
        return True
    elif val == "false":
        return False
    else:
        return False


def get_ml_service_orchestrator_vllm_flag():
    """Get HAnS ml service vllm orchestrator use flag
    :return: bool True if enabled, False otherwise
    """
    _ml_service_orchestrator_vllm_flag = os.environ.get("HANS_ML_SERVICE_ORCHESTRATOR_VLLM", default="False")
    val = _ml_service_orchestrator_vllm_flag.lower()
    if val == "true":
        return True
    elif val == "false":
        return False
    else:
        return False


def get_ml_service_orchestrator_rllm_flag():
    """Get HAnS ml service rllm orchestrator use flag
    :return: bool True if enabled, False otherwise
    """
    _ml_service_orchestrator_rllm_flag = os.environ.get("HANS_ML_SERVICE_ORCHESTRATOR_RLLM", default="False")
    val = _ml_service_orchestrator_rllm_flag.lower()
    if val == "true":
        return True
    elif val == "false":
        return False
    else:
        return False


def get_ml_service_orchestrator_translation_flag():
    """Get HAnS ml service tranlation orchestrator use flag
    :return: bool True if enabled, False otherwise
    """
    _ml_service_orchestrator_translation_flag = os.environ.get(
        "HANS_ML_SERVICE_ORCHESTRATOR_TRANSLATION", default="False"
    )
    val = _ml_service_orchestrator_translation_flag.lower()
    if val == "true":
        return True
    elif val == "false":
        return False
    else:
        return False


def get_ml_service_orchestrator_embedding_flag():
    """Get HAnS ml service tranlation orchestrator use flag
    :return: bool True if enabled, False otherwise
    """
    _ml_service_orchestrator_embedding_flag = os.environ.get("HANS_ML_SERVICE_ORCHESTRATOR_EMBEDDING", default="False")
    val = _ml_service_orchestrator_embedding_flag.lower()
    if val == "true":
        return True
    elif val == "false":
        return False
    else:
        return False


def get_ml_service_orchestrator_llm_route():
    """Get HAnS ml-service orchestrator route to llm
    :return: str ml-service orchestrator route to llm
    """
    _ml_service_orchestrator_llm_route = os.environ.get("HANS_ML_SERVICE_ORCHESTRATOR_LLM_ROUTE", default="llm_service")
    return _ml_service_orchestrator_llm_route.lower()


def get_ml_service_orchestrator_vllm_route():
    """Get HAnS ml-service orchestrator route to vllm
    :return: str ml-service orchestrator route to vllm
    """
    _ml_service_orchestrator_vllm_route = os.environ.get(
        "HANS_ML_SERVICE_ORCHESTRATOR_VLLM_ROUTE", default="vllm_service"
    )
    return _ml_service_orchestrator_vllm_route.lower()


def get_ml_service_orchestrator_rllm_route():
    """Get HAnS ml-service orchestrator route to rllm
    :return: str ml-service orchestrator route to rllm
    """
    _ml_service_orchestrator_rllm_route = os.environ.get(
        "HANS_ML_SERVICE_ORCHESTRATOR_RLLM_ROUTE", default="rllm_service"
    )
    return _ml_service_orchestrator_rllm_route.lower()


def get_ml_service_orchestrator_translation_route():
    """Get HAnS ml-service orchestrator route to translation service
    :return: str ml-service orchestrator route to translation service
    """
    _ml_service_orchestrator_translation_route = os.environ.get(
        "HANS_ML_SERVICE_ORCHESTRATOR_TRANSLATION_ROUTE", default="translation_service"
    )
    return _ml_service_orchestrator_translation_route.lower()


def get_ml_service_orchestrator_embedding_route():
    """Get HAnS ml-service orchestrator route to embedding service
    :return: str ml-service orchestrator route to embedding service
    """
    _ml_service_orchestrator_embedding_route = os.environ.get(
        "HANS_ML_SERVICE_ORCHESTRATOR_EMBEDDING_ROUTE", default="embedding_service"
    )
    return _ml_service_orchestrator_embedding_route.lower()


# HANS ML SERVICES LLM


def get_ml_service_llm_host():
    """Get HAnS ml-service llm host
    :return: str ml-service llm host
    """
    _ml_service_llm_hostname = os.environ.get("HANS_ML_SERVICE_LLM_HOST", default="host.docker.internal")
    return _ml_service_llm_hostname.lower()


def get_ml_service_llm_port():
    """Get HAnS ml-service llm port
    :return: str ml-service llm port
    """
    _ml_service_llm_port = os.environ.get("HANS_ML_SERVICE_LLM_PORT", default="8093")
    return _ml_service_llm_port.lower()


def get_ml_service_llm_user():
    """Get HAnS ml-service llm user
    :return: str ml-service llm user
    """
    _ml_service_llm_user = os.environ.get("HANS_ML_SERVICE_LLM_USER", default="admin")
    return _ml_service_llm_user


def get_ml_service_llm_password():
    """Get HAnS ml-service llm password
    :return: str ml-service llm password
    """
    _ml_service_llm_password = os.environ.get("HANS_ML_SERVICE_LLM_PASSWORD", default="admin")
    return _ml_service_llm_password


def get_ml_service_llm_model_id():
    """Get HAnS ml-service llm model id
    :return: str ml-service llm model id
    """
    _ml_service_llm_model_id = os.environ.get(
        "HANS_ML_SERVICE_LLM_MODEL_ID", default="mistralai/Mixtral-8x7B-Instruct-v0.1"
    )
    return _ml_service_llm_model_id


# HANS ML SERVICES VLLM


def get_ml_service_vllm_host():
    """Get HAnS ml-service vllm host
    :return: str ml-service vllm host
    """
    _ml_service_vllm_hostname = os.environ.get("HANS_ML_SERVICE_VLLM_HOST", default="host.docker.internal")
    return _ml_service_vllm_hostname.lower()


def get_ml_service_vllm_port():
    """Get HAnS ml-service vllm port
    :return: str ml-service vllm port
    """
    _ml_service_vllm_port = os.environ.get("HANS_ML_SERVICE_VLLM_PORT", default="8092")
    return _ml_service_vllm_port.lower()


def get_ml_service_vllm_user():
    """Get HAnS ml-service vllm user
    :return: str ml-service vllm user
    """
    _ml_service_vllm_user = os.environ.get("HANS_ML_SERVICE_VLLM_USER", default="admin")
    return _ml_service_vllm_user


def get_ml_service_vllm_password():
    """Get HAnS ml-service vllm password
    :return: str ml-service vllm password
    """
    _ml_service_vllm_password = os.environ.get("HANS_ML_SERVICE_VLLM_PASSWORD", default="admin")
    return _ml_service_vllm_password


def get_ml_service_vllm_model_id():
    """Get HAnS ml-service vllm model id
    :return: str ml-service vllm model id
    """
    _ml_service_vllm_model_id = os.environ.get("HANS_ML_SERVICE_VLLM_MODEL_ID", default="mistralai/Pixtral-12B-2409")
    return _ml_service_vllm_model_id


# HANS ML SERVICES LLM REASONING


def get_ml_service_llm_reasoning_host():
    """Get HAnS ml-service llm reasoning host
    :return: str ml-service llm reasoning host
    """
    _ml_service_llm_hostname = os.environ.get("HANS_ML_SERVICE_LLM_REASONING_HOST", default="host.docker.internal")
    return _ml_service_llm_hostname.lower()


def get_ml_service_llm_reasoning_port():
    """Get HAnS ml-service llm reasoning port
    :return: str ml-service llm reasoning port
    """
    _ml_service_llm_port = os.environ.get("HANS_ML_SERVICE_LLM_REASONING_PORT", default="8090")
    return _ml_service_llm_port.lower()


def get_ml_service_llm_reasoning_user():
    """Get HAnS ml-service llm reasoning user
    :return: str ml-service llm reasoning user
    """
    _ml_service_llm_user = os.environ.get("HANS_ML_SERVICE_LLM_REASONING_USER", default="admin")
    return _ml_service_llm_user


def get_ml_service_llm_reasoning_password():
    """Get HAnS ml-service llm reasoning password
    :return: str ml-service llm reasoning password
    """
    _ml_service_llm_password = os.environ.get("HANS_ML_SERVICE_LLM_REASONING_PASSWORD", default="admin")
    return _ml_service_llm_password


def get_ml_service_llm_reasoning_model_id():
    """Get HAnS ml-service llm reasoning model id
    :return: str ml-service llm reasoning model id
    """
    _ml_service_llm_model_id = os.environ.get(
        "HANS_ML_SERVICE_LLM_REASONING_MODEL_ID", default="NousResearch/DeepHermes-3-Mistral-24B-Preview"
    )
    return _ml_service_llm_model_id


# HANS ML SERVICES EMBEDDING


def get_ml_service_embedding_host():
    """Get HAnS ml-service embedding host
    :return: str ml-service embedding host
    """
    _ml_service_embedding_hostname = os.environ.get("HANS_ML_SERVICE_EMBEDDING_HOST", default="host.docker.internal")
    return _ml_service_embedding_hostname.lower()


def get_ml_service_embedding_port():
    """Get HAnS ml-service embedding port
    :return: str ml-service embedding port
    """
    _ml_service_embedding_port = os.environ.get("HANS_ML_SERVICE_EMBEDDING_PORT", default="8087")
    return _ml_service_embedding_port.lower()


def get_ml_service_embedding_user():
    """Get HAnS ml-service embedding user
    :return: str ml-service embedding user
    """
    _ml_service_embedding_user = os.environ.get("HANS_ML_SERVICE_EMBEDDING_USER", default="admin")
    return _ml_service_embedding_user


def get_ml_service_embedding_password():
    """Get HAnS ml-service embedding password
    :return: str ml-service embedding password
    """
    _ml_service_embedding_password = os.environ.get("HANS_ML_SERVICE_EMBEDDING_PASSWORD", default="admin")
    return _ml_service_embedding_password


def get_ml_service_embedding_model_id():
    """Get HAnS ml-service embedding model id
    :return: str ml-service embedding model id
    """
    _ml_service_embedding_model_id = os.environ.get(
        "HANS_ML_SERVICE_EMBEDDING_MODEL_ID", default="mixedbread-ai/deepset-mxbai-embed-de-large-v1"
    )
    return _ml_service_embedding_model_id


# HANS ML SERVICES TRANSLATION


def get_ml_service_translation_host():
    """Get HAnS ml-service translation host
    :return: str ml-service translation host
    """
    _ml_service_translation_hostname = os.environ.get(
        "HANS_ML_SERVICE_TRANSLATION_HOST", default="host.docker.internal"
    )
    return _ml_service_translation_hostname.lower()


def get_ml_service_translation_port():
    """Get HAnS ml-service translation port
    :return: str ml-service translation port
    """
    _ml_service_translation_port = os.environ.get("HANS_ML_SERVICE_TRANSLATION_PORT", default="8087")
    return _ml_service_translation_port.lower()


def get_ml_service_translation_user():
    """Get HAnS ml-service translation user
    :return: str ml-service translation user
    """
    _ml_service_translation_user = os.environ.get("HANS_ML_SERVICE_TRANSLATION_USER", default="admin")
    return _ml_service_translation_user


def get_ml_service_translation_password():
    """Get HAnS ml-service translation password
    :return: str ml-service translation password
    """
    _ml_service_translation_password = os.environ.get("HANS_ML_SERVICE_TRANSLATION_PASSWORD", default="admin")
    return _ml_service_translation_password


def get_ml_service_translation_model_id():
    """Get HAnS ml-service translation model id
    :return: str ml-service translation model id
    """
    _ml_service_translation_model_id = os.environ.get(
        "HANS_ML_SERVICE_TRANSLATION_MODEL_ID", default="google/madlad400-7b-mt"
    )
    return _ml_service_translation_model_id
