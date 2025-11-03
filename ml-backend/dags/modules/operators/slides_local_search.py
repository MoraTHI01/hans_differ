#!/usr/bin/env python
"""
Local search operators for sldies.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2024, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import json
from os import access
from urllib.request import urlopen
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator

# Specify minio version to be used in all PythonVirtualenvOperator
PIP_REQUIREMENT_MINIO = "minio"


def create_local_slides_search_trie(
    slides_images_data, slides_images_data_key, slides_trie_result_data, slides_trie_result_key
):
    """
    Create local search trie for slides on the assetdb-temp storage.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str slides_images_data: XCOM data containing URN for the slides.meta.json.
    :param str slides_images_data_key: XCOM Data key to used to determine the URN for the slides.meta.json.

    :param str slides_trie_result_data: XCOM data containing URN for the upload of the local search slides trie to assetdb-temp
    :param str slides_trie_result_key: XCOM Data key to used to determine the URN for the upload of the local search slides trie.

    :return: PythonVirtualenvOperator Operator to create local search for slides on the assetdb-temp storage.
    """
    import sys
    import json
    import time
    from collections import Counter
    from io import BytesIO
    from airflow.exceptions import AirflowFailException
    from modules.connectors.connector_provider import connector_provider
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
            node = self._insert(word=word)

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

    # Load slides.meta.json file
    slides_meta_urn_base = get_data_from_xcom(slides_images_data, [slides_images_data_key])
    slides_meta_urn = slides_meta_urn_base + "/slides.meta.json"
    slides_meta_response = assetdb_temp_connector.get_object(slides_meta_urn)
    if "500 Internal Server Error" in slides_meta_response.data.decode("utf-8"):
        raise AirflowFailException()
    slides_meta_json = json.loads(slides_meta_response.data)
    slides_meta_response.close()
    slides_meta_response.release_conn()

    slides_trie = Trie()
    print("Create slides search trie", flush=True)
    start_page = int(slides_meta_json["page"]["start"])
    if start_page < 1:
        start_page = 1
    end_page = int(slides_meta_json["page"]["end"])
    for i in range(start_page, end_page + 1):
        slide_meta_file_urn = slides_meta_urn_base + f"/{str(i)}.meta.json"
        slide_meta_response = assetdb_temp_connector.get_object(slide_meta_file_urn)
        if "500 Internal Server Error" in slide_meta_response.data.decode("utf-8"):
            raise AirflowFailException()
        slide_meta_json = json.loads(slide_meta_response.data)
        slide_meta_response.close()
        slide_meta_response.release_conn()
        curr_interval = [slide_meta_json["chunk_start"], slide_meta_json["chunk_end"]]
        for word in slide_meta_json["words"]:
            slides_trie.insert_word(word=word.lower(), index=i - 1, interval=curr_interval)

    # Store data
    sys.setrecursionlimit(99000)  # Increase recursion depth
    data_de = json.dumps(slides_trie.trie).encode("utf-8")
    stream_bytes = BytesIO(data_de)
    mime_type = HansType.get_mime_type(HansType.SLIDES_TRIE)
    meta_minio = {"Content-Type": mime_type}
    local_document_urn = get_data_from_xcom(slides_trie_result_data, [slides_trie_result_key])
    (success, object_name) = assetdb_temp_connector.put_object(local_document_urn, stream_bytes, mime_type, meta_minio)
    if not success:
        print("Error uploading slides search trie to assetdb-temp!")
        raise AirflowFailException()
    return json.dumps({"result": object_name})


def op_create_local_slides_search_trie(
    dag,
    dag_id,
    task_id_suffix,
    slides_images_data,
    slides_images_data_key,
    slides_trie_result_data,
    slides_trie_result_key,
):
    """
    Provides PythonVirtualenvOperator to create an local search for slides on the assetdb-temp storage.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str slides_images_data: XCOM data containing URN for the slides.meta.json.
    :param str slides_images_data_key: XCOM Data key to used to determine the URN for the slides.meta.json.

    :param str slides_trie_result_data: XCOM data containing URN for the upload of the local search slides trie to assetdb-temp
    :param str slides_trie_result_key: XCOM Data key to used to determine the URN for the upload of the local search slides trie.

    :return: PythonVirtualenvOperator Operator to create local search for slides on the assetdb-temp storage.
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_create_local_slides_search_trie", task_id_suffix),
        python_callable=create_local_slides_search_trie,
        op_args=[slides_images_data, slides_images_data_key, slides_trie_result_data, slides_trie_result_key],
        # requirements=[PIP_REQUIREMENT_MINIO, "eval-type-backport", 'nltk'],
        requirements=[PIP_REQUIREMENT_MINIO],
        python_version="3",
        dag=dag,
    )
