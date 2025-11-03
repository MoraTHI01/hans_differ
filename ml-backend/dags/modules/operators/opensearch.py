#!/usr/bin/env python
"""
Opensearch operators for document preparation.
"""
__author__ = "Christopher Simic"
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


def create_opensearch_document(
    asr_de_data,
    asr_de_data_key,
    asr_en_data,
    asr_en_data_key,
    asr_locale_data,
    asr_locale_key,
    download_data,
    download_meta_urn_key,
    opensearch_data,
    opensearch_urn_key,
):
    """
    Creates an opensearch document for the opensearch engine.

    :param str asr_de_data: XCOM data containing URN for the asr_result_de.json.
    :param str asr_de_data_key: XCOM Data key to used to determine the URN for the asr_result_de.json.
    :param str asr_en_data: XCOM data containing URN for the asr_result_en.json.
    :param str asr_en_data_key: XCOM Data key to used to determine the URN for the asr_result_en.json.
    :param str asr_locale_data: XCOM Data which contains the asr locale.
    :param str asr_locale_key: XCOM Data key to used to determine the asr locale.
    :param str download_data: XCOM data containing URN for the meta data.
    :param str download_meta_urn_key: XCOM Data key to used to determine the URN for the meta data.
    :param str opensearch_data: XCOM data containing URN for the upload of the opensearch document to assetdb-temp
    :param str opensearch_urn_key: XCOM Data key to used to determine the URN for the upload of the opensearch document.
    """
    import json
    import time
    from collections import Counter
    from io import BytesIO
    from airflow.exceptions import AirflowFailException
    from modules.connectors.connector_provider import connector_provider
    from modules.operators.connections import get_assetdb_temp_config
    from modules.operators.transfer import HansType
    from modules.operators.xcom import get_data_from_xcom

    # import nltk
    # from nltk.stem.snowball import SnowballStemmer
    # from nltk.corpus import stopwords
    # nltk.download('stopwords')
    # snowball = SnowballStemmer("german")

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()

    # Configure connector_provider and connect assetdb_temp_connector
    connector_provider.configure({"assetdb_temp": assetdb_temp_config})

    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

    # Get locale
    locale = get_data_from_xcom(asr_locale_data, [asr_locale_key])
    print("Locale: " + locale)

    # Load asr_result Files
    asr_de_urn = get_data_from_xcom(asr_de_data, [asr_de_data_key])
    asr_de_response = assetdb_temp_connector.get_object(asr_de_urn)
    if "500 Internal Server Error" in asr_de_response.data.decode("utf-8"):
        raise AirflowFailException()
    asr_de_json = json.loads(asr_de_response.data)
    asr_de_response.close()
    asr_de_response.release_conn()

    asr_en_urn = get_data_from_xcom(asr_en_data, [asr_en_data_key])
    asr_en_response = assetdb_temp_connector.get_object(asr_en_urn)
    if "500 Internal Server Error" in asr_en_response.data.decode("utf-8"):
        raise AirflowFailException()
    asr_en_json = json.loads(asr_en_response.data)
    asr_en_response.close()
    asr_en_response.release_conn()

    # Load metadata File
    metadata_urn = get_data_from_xcom(download_data, [download_meta_urn_key])
    meta_response = assetdb_temp_connector.get_object(metadata_urn)
    if "500 Internal Server Error" in meta_response.data.decode("utf-8"):
        raise AirflowFailException()

    meta_data = json.loads(meta_response.data)
    meta_response.close()
    meta_response.release_conn()

    # Create ASR result string
    stop_words = list()
    stop_words.append("")
    stop_words.append("<UNK>")

    word_list_de = []
    for sent in asr_de_json["result"]:
        for w in sent["words"]:
            if w["word"] not in stop_words:
                word_list_de.append(w["word"])
    transcr_de_str = " ".join(word_list_de)
    print(f"transcript de length: {len(transcr_de_str)}")

    word_list_en = []
    for sent in asr_en_json["result"]:
        for w in sent["words"]:
            if w["word"] not in stop_words:
                word_list_en.append(w["word"])
    transcr_en_str = " ".join(word_list_en)
    print(f"transcript en length: {len(transcr_en_str)}")

    json_data = {}
    json_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    json_data["title"] = meta_data["title"]
    json_data["course"] = meta_data["description"]["course"]
    json_data["course_acronym"] = meta_data["description"]["course_acronym"]
    json_data["faculty"] = meta_data["description"]["faculty"]
    json_data["faculty_acronym"] = meta_data["description"]["faculty_acronym"]
    json_data["university"] = meta_data["description"]["university"]
    json_data["university_acronym"] = meta_data["description"]["university_acronym"]
    json_data["language"] = meta_data["language"]
    json_data["tags"] = meta_data["tags"]
    json_data["lecturer"] = meta_data["description"]["lecturer"]
    json_data["semester"] = meta_data["description"]["semester"]
    json_data["asr_result_de"] = transcr_de_str
    json_data["asr_result_en"] = transcr_en_str

    # Store data
    data = json.dumps(json_data).encode("utf-8")
    stream_bytes = BytesIO(data)
    meta_minio = {}
    opensearch_document_urn = get_data_from_xcom(opensearch_data, [opensearch_urn_key])
    (success, object_name) = assetdb_temp_connector.put_object(
        opensearch_document_urn, stream_bytes, HansType.get_mime_type(HansType.SEARCH_DATA), meta_minio
    )
    if not success:
        print("Error uploading search_data to assetdb-temp!")
        raise AirflowFailException()

    return json.dumps({"result": object_name})


def op_create_opensearch_document(
    dag,
    dag_id,
    task_id_suffix,
    asr_de_data,
    asr_de_data_key,
    asr_en_data,
    asr_en_data_key,
    asr_locale_data,
    asr_locale_key,
    download_data,
    download_meta_urn_key,
    opensearch_data,
    opensearch_urn_key,
):
    """
    Provides PythonVirtualenvOperator to create an opensearch document on the assetdb-temp storage.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str asr_de_data: XCOM data containing URN for the asr_result_de.json.
    :param str asr_de_data_key: XCOM Data key to used to determine the URN for the asr_result_de.json.
    :param str asr_en_data: XCOM data containing URN for the asr_result_en.json.
    :param str asr_en_data_key: XCOM Data key to used to determine the URN for the asr_result_en.json.
    :param str asr_locale_data: XCOM Data which contains the asr locale.
    :param str asr_locale_key: XCOM Data key to used to determine the asr locale.
    :param str download_data: XCOM data containing URN for the meta data.
    :param str download_meta_urn_key: XCOM Data key to used to determine the URN for the meta data.
    :param str opensearch_data: XCOM data containing URN for the upload of the opensearch document to assetdb-temp
    :param str opensearch_urn_key: XCOM Data key to used to determine the URN for the upload of the opensearch document.

    :return: PythonVirtualenvOperator Operator to create opensearch document on the assetdb-temp storage.
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_create_opensearch_document", task_id_suffix),
        python_callable=create_opensearch_document,
        op_args=[
            asr_de_data,
            asr_de_data_key,
            asr_en_data,
            asr_en_data_key,
            asr_locale_data,
            asr_locale_key,
            download_data,
            download_meta_urn_key,
            opensearch_data,
            opensearch_urn_key,
        ],
        # requirements=[PIP_REQUIREMENT_MINIO, "eval-type-backport", 'nltk'],
        requirements=[PIP_REQUIREMENT_MINIO],
        python_version="3",
        dag=dag,
    )
