#!/usr/bin/env python
"""
Operators to create closed captions based on WebVTT
which will be added to mpeg-dash mpd file.
For WebVTT see https://www.w3.org/TR/webvtt1/
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


from os import access
from urllib.request import urlopen
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator


# Specify minio version to be used in all PythonVirtualenvOperator
PIP_REQUIREMENT_MINIO = "minio"


def create_closed_captions(transcript_data, transcript_data_key, dash_data, dash_urn_key):
    """
    Creates an closed captions in WebVTT format and appends them to
    mpeg-dash mpd file on assetdb-temp.

    :param str transcript_data: XCOM data containing URN for the asr_result_normalized.json aka transcript.
    :param str transcript_data_key: XCOM Data key to used to determine the URN for the asr_result_normalized.json.
    :param str dash_data: XCOM Data which contains the URN of the mpeg-dash mpd file.
    :param str dash_urn_key: XCOM Data key to used to determine the URN of the mpeg-dash mpd file.
    """
    import json
    from io import BytesIO
    from airflow.exceptions import AirflowFailException
    from modules.connectors.connector_provider import connector_provider
    from modules.operators.connections import get_assetdb_temp_config
    from modules.operators.transfer import HansType
    from modules.operators.xcom import get_data_from_xcom

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()

    # Configure connector_provider and connect assetdb_temp_connector
    connector_provider.configure({"assetdb_temp": assetdb_temp_config})

    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

    return json.dumps({"result": "finished"})


def op_create_closed_captions(
    dag, dag_id, task_id_suffix, transcript_data, transcript_data_key, dash_data, dash_urn_key
):
    """
    Provides PythonVirtualenvOperator to create closed captions of the transcript and append them to dash mpd file.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str transcript_data: XCOM data containing URN for the asr_result_normalized.json aka transcript.
    :param str transcript_data_key: XCOM Data key to used to determine the URN for the asr_result_normalized.json.
    :param str dash_data: XCOM Data which contains the URN of the mpeg-dash mpd file.
    :param str dash_urn_key: XCOM Data key to used to determine the URN of the mpeg-dash mpd file.

    :return: PythonVirtualenvOperator Operator to create closed captions of the transcript and append them to dash mpd file.
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_create_closed_captions", task_id_suffix),
        python_callable=create_closed_captions,
        op_args=[transcript_data, transcript_data_key, dash_data, dash_urn_key],
        requirements=[PIP_REQUIREMENT_MINIO, "eval-type-backport", "nltk"],
        python_version="3",
        dag=dag,
    )
