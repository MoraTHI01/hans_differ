#!/usr/bin/env python
"""
Local search operators for document preparation.
"""
__author__ = "Christopher Simic"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import json
from os import access
from urllib.request import urlopen
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator


def create_local_search_document(
    asr_de_data,
    asr_de_data_key,
    asr_en_data,
    asr_en_data_key,
    asr_locale_data,
    asr_locale_key,
    download_data,
    download_meta_urn_key,
    local_search_data_de,
    local_search_de_urn_key,
    local_search_data_en,
    local_search_en_urn_key,
):
    """
    Creates a local search document for the local search engine.

    :param str asr_de_data: XCOM data containing URN for the asr_result_de.json.
    :param str asr_de_data_key: XCOM Data key to used to determine the URN for the asr_result_de.json.
    :param str asr_en_data: XCOM data containing URN for the asr_result_en.json.
    :param str asr_en_data_key: XCOM Data key to used to determine the URN for the asr_result_en.json.
    :param str asr_locale_data: XCOM Data which contains the asr locale.
    :param str asr_locale_key: XCOM Data key to used to determine the asr locale.
    :param str download_data: XCOM data containing URN for the meta data.
    :param str download_meta_urn_key: XCOM Data key to used to determine the URN for the meta data.
    :param str local_search_data_de: XCOM data containing URN for the upload of the local search document to assetdb-temp
    :param str local_search_de_urn_key: XCOM Data key to used to determine the URN for the upload of the local search document.
    :param str local_search_data_en: XCOM data containing URN for the upload of the local search document to assetdb-temp
    :param str local_search_en_urn_key: XCOM Data key to used to entermine the URN for the upload of the local search document.
    """
    import sys
    import json
    import time
    from collections import Counter
    from io import BytesIO
    from airflow.exceptions import AirflowFailException
    from connectors.connector_provider import connector_provider
    from modules.operators.connections import get_assetdb_temp_config
    from modules.operators.transfer import HansType
    from modules.operators.xcom import get_data_from_xcom

    class Trie:

        def __init__(self):
            self.trie = {"children": {}}

        def _insert(self, word: str) -> dict:
            current = self.trie
            for i, char in enumerate(word, 1):
                if char not in current["children"]:
                    current["children"][char] = {"children": {}}

                current = current["children"][char]

                if i == len(word):
                    current["word"] = word

            return current

        def insert_word(self, word: str, index: int, interval: [int, int]) -> dict:
            node = self._insert(word=word.lower())

            if "occurences" not in node:
                node["occurences"] = []

            node["occurences"].append({"word": word, "index": index, "interval": interval})

            return node

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
    transcript_de_json = json.loads(asr_de_response.data)
    asr_de_response.close()
    asr_de_response.release_conn()

    asr_en_urn = get_data_from_xcom(asr_en_data, [asr_en_data_key])
    asr_en_response = assetdb_temp_connector.get_object(asr_en_urn)
    if "500 Internal Server Error" in asr_en_response.data.decode("utf-8"):
        raise AirflowFailException()
    transcript_en_json = json.loads(asr_en_response.data)
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

    trie_de = Trie()
    trie_en = Trie()

    for sentence in transcript_de_json["result"]:
        for word in sentence["words"]:

            if not word["word"]:
                continue

            trie_de.insert_word(word=word["word"], index=word["index"], interval=word["interval"])

    for sentence in transcript_en_json["result"]:
        for word in sentence["words"]:

            if not word["word"]:
                continue

            trie_en.insert_word(word=word["word"], index=word["index"], interval=word["interval"])

    # Store data
    sys.setrecursionlimit(99000)  # Increase recursion depth
    data_de = json.dumps(trie_de.trie).encode("utf-8")
    stream_bytes = BytesIO(data_de)
    meta_minio = {}
    local_document_urn = get_data_from_xcom(local_search_data_de, [local_search_de_urn_key])
    (success, object_name) = assetdb_temp_connector.put_object(
        local_document_urn, stream_bytes, HansType.get_mime_type(HansType.SEARCH_TRIE_DE), meta_minio
    )
    if not success:
        print("Error uploading search_data to assetdb-temp!")
        raise AirflowFailException()

    data_en = json.dumps(trie_en.trie).encode("utf-8")
    stream_bytes = BytesIO(data_en)
    meta_minio = {}
    local_document_urn = get_data_from_xcom(local_search_data_en, [local_search_en_urn_key])
    (success, object_name) = assetdb_temp_connector.put_object(
        local_document_urn, stream_bytes, HansType.get_mime_type(HansType.SEARCH_TRIE_EN), meta_minio
    )
    if not success:
        print("Error uploading search_data to assetdb-temp!")
        raise AirflowFailException()
    return json.dumps({"result": object_name})


def op_create_local_search_document(
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
    local_search_data_de,
    local_search_de_urn_key,
    local_search_data_en,
    local_search_en_urn_key,
):
    """
    Provides PythonVirtualenvOperator to create an local search document on the assetdb-temp storage.

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
    :param str local_search_data_de: XCOM data containing URN for the upload of the local search document to assetdb-temp
    :param str local_search_de_urn_key: XCOM Data key to used to determine the URN for the upload of the local search document.
    :param str local_search_data_en: XCOM data containing URN for the upload of the local search document to assetdb-temp
    :param str local_search_en_urn_key: XCOM Data key to used to entermine the URN for the upload of the local search document.

    :return: PythonVirtualenvOperator Operator to create local search document on the assetdb-temp storage.
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_create_local_search_document", task_id_suffix),
        python_callable=create_local_search_document,
        op_args=[
            asr_de_data,
            asr_de_data_key,
            asr_en_data,
            asr_en_data_key,
            asr_locale_data,
            asr_locale_key,
            download_data,
            download_meta_urn_key,
            local_search_data_de,
            local_search_de_urn_key,
            local_search_data_en,
            local_search_en_urn_key,
        ],
        # requirements=[ "/opt/hans-modules/dist/hans_shared_modules-0.1-py3-none-any.whl", "eval-type-backport", 'nltk'],
        requirements=["/opt/hans-modules/dist/hans_shared_modules-0.1-py3-none-any.whl"],
        # pip_install_options=["--force-reinstall"],
        python_version="3",
        dag=dag,
    )
