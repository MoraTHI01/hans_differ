#!/usr/bin/env python
"""
Storage operators.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


from enum import Enum
from os import access
from urllib.request import urlopen
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator


# Specify minio version to be used in all PythonVirtualenvOperator
PIP_REQUIREMENT_MINIO = "minio"


# CREATE URL


def create_url(hans_type, urn, mode):
    """
    Creates an url for uploading a file in a bucket on a specific minio
    service, returns url for uploading the file.

    :param str hans_type: XCOM output key for the result url.
    :param str urn: Unique Resource Name (URN) on the storage system.
    :param str mode: Mode to access the generated url: 'download' or 'upload'

    :return: str JSON for XCOM containing the generated url with the hans_type as key.
    """
    import json
    from modules.connectors.connector_provider import connector_provider
    from modules.connectors.minio_connector import MinioConnectorFetchUrlMode
    from modules.operators.connections import get_assetdb_temp_config
    from airflow.exceptions import AirflowFailException

    if urn is None:
        raise AirflowFailException("Urn is empty!")

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()

    # Configure connector_provider
    connector_provider.configure({"assetdb_temp": assetdb_temp_config})

    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

    url_mode = MinioConnectorFetchUrlMode.DOWNLOAD
    if mode == "upload":
        url_mode = MinioConnectorFetchUrlMode.UPLOAD
    elif mode == "download":
        url_mode = MinioConnectorFetchUrlMode.DOWNLOAD

    url = assetdb_temp_connector.gen_presigned_url(urn, url_mode)
    # implicit XCOM push
    return json.dumps({hans_type: url})


def create_url_xcom(hans_type, xcom_data, xcom_data_urn_key, mode):
    """
    Creates an url for uploading a file in a bucket on a specific minio
    service, returns url for uploading the file.

    :param str hans_type: XCOM output key for the result url.
    :param str xcom_data: XCOM data containing the xcom_data_urn_key.
    :param str xcom_data_urn_key: Key to parse the Unique Resource Name (URN) form the XCOM data.
    :param str mode: Mode to access the generated url: 'download' or 'upload'

    :return: str JSON for XCOM containing the generated url with the hans_type as key.
    """
    from modules.operators.storage import create_url
    from modules.operators.xcom import get_data_from_xcom
    from airflow.exceptions import AirflowFailException

    # parse xcom data structure and return string value
    urn = get_data_from_xcom(xcom_data, [xcom_data_urn_key])

    # implicit XCOM push
    return create_url(hans_type, urn, mode)


def op_create_url(dag, dag_id, task_id_suffix, hans_type, database, bucket, file_name, file_extension, mode):
    """
    Provides PythonVirtualenvOperator to create a presigned url to
    download or upload a file on a specific minio storage system.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str hans_type: XCOM output key for the result url.

    :param str database: minio storage system database.
    :param str bucket: minio storage system bucket
    :param str file_name: Filename, usually an uuid
    :param str file_extension: File extension for the file
    :param str mode: Mode to access the generated url: 'download' or 'upload'

    :return: PythonVirtualenvOperator Operator to create a url on a specific minio storage system.
    """
    from modules.connectors.storage_connector import StorageConnector
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_create_url", task_id_suffix),
        python_callable=create_url,
        op_args=[hans_type, StorageConnector.create_urn(database, bucket, file_name, file_extension), mode],
        requirements=[PIP_REQUIREMENT_MINIO, "eval-type-backport", "datetime"],
        python_version="3",
        dag=dag,
    )


def op_create_url_by_urn(dag, dag_id, task_id_suffix, hans_type, urn, mode):
    """
    Provides PythonVirtualenvOperator to create a presigned url by a given urn to
    download or upload a file on a specific minio storage system.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str hans_type: XCOM output key for the result url.

    :param str urn: Unique Resource Name (URN) on the storage system.
    :param str mode: Mode to access the generated url: 'download' or 'upload'

    :return: PythonVirtualenvOperator Operator to create a url by urn
    on a specific minio storage system.
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_create_url_by_urn", task_id_suffix),
        python_callable=create_url,
        op_args=[hans_type, urn, mode],
        requirements=[PIP_REQUIREMENT_MINIO, "eval-type-backport", "datetime"],
        python_version="3",
        dag=dag,
    )


def op_create_url_by_xcom(dag, dag_id, task_id_suffix, hans_type, xcom_data, xcom_data_urn_key, mode):
    """
    Provides PythonVirtualenvOperator to create a presigned url by using
    xcom data (contains the urn) to download or upload a file on a specific minio storage system.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str hans_type: XCOM output key for the result url.

    :param str xcom_data: XCOM data containing the xcom_data_urn_key.
    :param str xcom_data_urn_key: Key to parse the Unique Resource Name (URN) form the XCOM data.
    :param str mode: Mode to access the generated url: 'download' or 'upload'

    :return: PythonVirtualenvOperator Operator to create a url by xcom data
    on a specific minio storage system.
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_create_url_by_xcom", task_id_suffix),
        python_callable=create_url_xcom,
        op_args=[hans_type, xcom_data, xcom_data_urn_key, mode],
        requirements=[PIP_REQUIREMENT_MINIO, "eval-type-backport", "datetime"],
        python_version="3",
        dag=dag,
    )


def op_create_url_on_assetdbtemp(dag, dag_id, task_id_suffix, hans_type, file_name, file_extension, mode):
    """
    Provides PythonVirtualenvOperator to create a url to download or upload a file
    on assetdb-temp minio service.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str hans_type: XCOM output key for the result url.

    :param str file_name: Filename, usually an uuid
    :param str file_extension: File extension for the file
    :param str mode: Mode to access the generated url: 'download' or 'upload'

    :return: PythonVirtualenvOperator Operator to create a url to download or upload a file
    on assetdb-temp minio service.
    """
    from modules.operators.connections import get_assetdb_temp_config
    from modules.connectors.storage_connector import StorageConnector
    from modules.operators.xcom import gen_task_id

    assetdb_temp_config = get_assetdb_temp_config()
    temp_database = assetdb_temp_config["host"]
    temp_bucket = assetdb_temp_config["bucket"]

    urn = StorageConnector.create_urn(temp_database, temp_bucket, file_name, file_extension)
    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_create_url_on_assetdbtemp", task_id_suffix),
        python_callable=create_url,
        op_args=[hans_type, urn, mode],
        requirements=[PIP_REQUIREMENT_MINIO, "eval-type-backport", "datetime"],
        python_version="3",
        dag=dag,
    )


# CREATE URN


def create_new_urn(hans_type, database, bucket, file_extension=""):
    """
    Creates an Unique Resource Name (URN) with a new Universally Unique Identifier (UUID).

    :param str hans_type: XCOM output key for the result url.
    :param str database: minio storage system database.
    :param str bucket: minio storage system bucket
    :param str file_extension: File extension for the file, default=''

    :return: str JSON for XCOM containing the generated urn with the hans_type as key.
    """
    import json
    from uuid import uuid4
    from modules.connectors.storage_connector import StorageConnector

    urn = StorageConnector.create_urn(database, bucket, str(uuid4()), file_extension)
    # implicit XCOM push
    return json.dumps({hans_type: urn})


def op_create_new_urn(dag, dag_id, task_id_suffix, hans_type, database, bucket, file_extension):
    """
    Provides PythonVirtualenvOperator to create an urn with a new uuid.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str hans_type: XCOM output key for the result url.

    :param str database: minio storage system database.
    :param str bucket: minio storage system bucket
    :param str file_extension: File extension for the file

    :return: PythonVirtualenvOperator Operator to create an urn with a new uuid.
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_create_new_urn", task_id_suffix),
        python_callable=create_new_urn,
        op_args=[hans_type, database, bucket, file_extension],
        requirements=[PIP_REQUIREMENT_MINIO, "eval-type-backport", "datetime"],
        python_version="3",
        dag=dag,
    )


def op_create_new_urn_on_assetdbtemp(dag, dag_id, task_id_suffix, hans_type, file_extension=""):
    """
    Provides PythonVirtualenvOperator to create an urn on assetdb-temp minio service.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str hans_type: XCOM output key for the result url.

    :param str file_extension: File extension for the file, default=''

    :return: PythonVirtualenvOperator Operator to create an urn on assetdb-temp minio service.
    """
    from modules.operators.connections import get_assetdb_temp_config
    from modules.operators.xcom import gen_task_id

    assetdb_temp_config = get_assetdb_temp_config()
    temp_database = assetdb_temp_config["host"]
    temp_bucket = assetdb_temp_config["bucket"]

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_create_new_urn_on_assetdbtemp", task_id_suffix),
        python_callable=create_new_urn,
        op_args=[hans_type, temp_database, temp_bucket, file_extension],
        requirements=[PIP_REQUIREMENT_MINIO, "eval-type-backport", "datetime"],
        python_version="3",
        dag=dag,
    )


# CLEANUP


def cleanup_assetdbtemp_bucket(bucketid):
    """
    Cleanup assetdb-temp bucket.

    :param str bucketid: Id name of the bucket

    :return: bool True if successful, False otherwise
    """
    import json
    from airflow.exceptions import AirflowFailException
    from modules.connectors.connector_provider import connector_provider
    from modules.operators.connections import get_assetdb_temp_config

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()
    archive_bucket = assetdb_temp_config[bucketid]

    # Configure connector_provider and connect assetdb_temp_connector
    connector_provider.configure({"assetdb_temp": assetdb_temp_config})

    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

    success = assetdb_temp_connector.delete_all_objects_in_bucket(archive_bucket)

    if not success:
        print(f"Error cleaning assetdb-temp {archive_bucket} bucket!")
        raise AirflowFailException()

    return json.dumps({"result": "Success"})


def op_cleanup_assetdbtemp_archive(dag, dag_id, task_id_suffix):
    """
    Provides PythonVirtualenvOperator to cleanup assetdb-temp archive bucket.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :return: PythonVirtualenvOperator Operator to cleanup assetdb-temp archive bucket.
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_cleanup_assetdbtemp_archive", task_id_suffix),
        python_callable=cleanup_assetdbtemp_bucket,
        op_args=["archive-bucket"],
        requirements=[PIP_REQUIREMENT_MINIO],
        python_version="3",
        dag=dag,
    )


def op_cleanup_assetdbtemp_assets_temp(dag, dag_id, task_id_suffix):
    """
    Provides PythonVirtualenvOperator to cleanup assetdb-temp assets-temp bucket.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :return: PythonVirtualenvOperator Operator to cleanup assetdb-temp assets-temp bucket.
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_cleanup_assetdbtemp_assets_temp", task_id_suffix),
        python_callable=cleanup_assetdbtemp_bucket,
        op_args=["bucket"],
        requirements=[PIP_REQUIREMENT_MINIO],
        python_version="3",
        dag=dag,
    )
