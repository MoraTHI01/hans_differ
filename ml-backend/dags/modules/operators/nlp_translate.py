#!/usr/bin/env python
"""
NLP translate remote operator.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2023, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


from os import access
from urllib.request import urlopen
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator
import requests
import json
import re


def nlp_translate_remote(
    source_language, target_language, download_data, download_data_key, upload_data, upload_data_key, llm_configs={}
):
    """
    Creates a remote request to a translation service.

    :param str source_language: Source language for translation, could be 'de' or 'en'.
    :param str target_language: Target language for translation, could be 'de' or 'en'.

    :param str download_data: XCOM Data which contains download url for llm json result.
    :param str download_data_key: XCOM Data key to used to determine the download url.

    :param str upload_data: XCOM Data which contains upload url.
    :param str upload_data_key: XCOM Data key to used to determine the upload url.

    :param dict llm_configs: Configurations for all llm models
    """
    import json
    import requests
    from io import BytesIO
    from airflow.exceptions import AirflowFailException
    from connectors.connector_provider import connector_provider
    from modules.operators.connections import get_assetdb_temp_config, get_connection_config
    from modules.operators.xcom import get_data_from_xcom

    # Get translation remote config
    translation_remote_config = get_connection_config("translation_remote")
    translation_remote_config["translation_task"] = llm_configs["translation_task"]
    translation_remote_config["translation_model_id"] = llm_configs["translation_model_id"]

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()

    # Configure connector_provider and connect assetdb_temp_connector
    connector_provider.configure(
        {"assetdb_temp": assetdb_temp_config, "translation_remote_config": translation_remote_config}
    )
    # Connect to assetdb temp
    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

    # Connect to translation service
    translation_connector = connector_provider.get_translation_connector()
    translation_connector.connect()

    # Load json File
    data_urn = get_data_from_xcom(download_data, [download_data_key])
    data_response = assetdb_temp_connector.get_object(data_urn)
    if "500 Internal Server Error" in data_response.data.decode("utf-8"):
        raise AirflowFailException()
    data = json.loads(data_response.data)
    data_response.close()
    data_response.release_conn()

    data_type = data["type"]
    print(f"LLM Datatype: {data_type}")
    if data_type == "TopicResult":
        print(f"Start translating {data_type}")
        for item in data["result"]:
            if "title" in item.keys():
                item["title"] = translation_connector.post_raw_translations(
                    source_language, target_language, [item["title"]]
                )[0]
            if "summary" in item.keys():
                item["summary"] = translation_connector.post_raw_translations(
                    source_language, target_language, [item["summary"]]
                )[0]
    elif data_type == "ShortSummaryResult" or data_type == "SummaryResult":
        print(f"Start translating {data_type}")
        for item in data["result"]:
            if "summary" in item.keys():
                item["summary"] = translation_connector.post_raw_translations(
                    source_language, target_language, [item["summary"]]
                )[0]
    elif data_type == "QuestionnaireResult":
        for item in data["result"]:
            if "questionnaire" in item.keys():
                for grade in ["easy", "medium", "difficult"]:
                    for questionitem in item["questionnaire"][grade]:
                        questionitem["mcq"]["question"] = translation_connector.post_raw_translations(
                            source_language, target_language, [questionitem["mcq"]["question"]]
                        )[0]
                        questionitem["mcq"]["correct_answer_explanation"] = translation_connector.post_raw_translations(
                            source_language, target_language, [questionitem["mcq"]["correct_answer_explanation"]]
                        )[0]
                        for answeritem in questionitem["mcq"]["answers"]:
                            answeritem["answer"] = translation_connector.post_raw_translations(
                                source_language, target_language, [answeritem["answer"]]
                            )[0]
    print("Result")
    data["language"] = target_language.strip().lower()
    print(data)

    stream_bytes = BytesIO(json.dumps(data).encode("utf-8"))
    meta_minio = {}
    upload_result_urn = get_data_from_xcom(upload_data, [upload_data_key])
    (success, object_name) = assetdb_temp_connector.put_object(
        upload_result_urn, stream_bytes, "application/json", meta_minio
    )
    if not success:
        print(f"Error uploading translation result for on url {upload_result_urn} to assetdb-temp!")
        raise AirflowFailException()

    return json.dumps({"result": object_name})


def op_nlp_translate_remote(
    dag,
    dag_id,
    task_id_suffix,
    source_language,
    target_language,
    download_data,
    download_data_key,
    upload_data,
    upload_data_key,
    llm_configs={},
):
    """
    Provides PythonVirtualenvOperator to request a translation service.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str source_language: Source language for translation, could be 'de' or 'en'.
    :param str target_language: Target language for translation, could be 'de' or 'en'.

    :param str download_data: XCOM Data which contains download url for llm json result.
    :param str download_data_key: XCOM Data key to used to determine the download url.

    :param str upload_data: XCOM Data which contains upload url.
    :param str upload_data_key: XCOM Data key to used to determine the upload url.
    :param dict llm_configs: Configurations for all llm models

    :return: PythonVirtualenvOperator Operator to create opensearch document on the assetdb-temp storage.
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_nlp_translate_remote", task_id_suffix),
        python_callable=nlp_translate_remote,
        op_args=[
            source_language,
            target_language,
            download_data,
            download_data_key,
            upload_data,
            upload_data_key,
            llm_configs,
        ],
        requirements=["/opt/hans-modules/dist/hans_shared_modules-0.1-py3-none-any.whl"],
        python_version="3",
        dag=dag,
    )
