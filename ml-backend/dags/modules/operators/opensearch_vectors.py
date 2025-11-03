#!/usr/bin/env python
"""
Opensearch operators for document preparation.
"""
import uuid
from os import access
from urllib.request import urlopen
from airflow import DAG
import requests
from airflow.operators.python import PythonVirtualenvOperator


# Specify minio version to be used in all PythonVirtualenvOperator
PIP_REQUIREMENT_MINIO = "minio"


def create_text_chunks(
    sentences: list[str], intervals: list[tuple[float, float]], min_chunk_words: int = 128, min_overlap_words: int = 32
) -> tuple[list[str], list[tuple[float, float]]]:
    chunks = []
    chunk_intervals = []
    current_chunk = ""
    i = 0
    previous_start = 0
    current_audio_start = None

    while i < len(sentences):
        if current_audio_start is None:
            current_audio_start = intervals[i][0]
        sentence = sentences[i]
        interval = intervals[i]
        current_chunk += f" {sentence}"
        if len(current_chunk.split()) >= min_chunk_words:
            # Chunk size reached
            chunks.append(current_chunk.strip())
            current_chunk = ""
            chunk_interval = (current_audio_start, interval[1])
            chunk_intervals.append(chunk_interval)
            current_audio_start = None  # set to None, so that it is re-set in the next iteration

            # How many sents do we need to go back to ensure overlap size?
            if len(sentences[i].split()) >= min_chunk_words:
                # The last sentence of the previous chunk is already a chunk, thus do not start with this as overlap
                i += 1
            else:
                overlap_size = len(sentences[i].split())
                while overlap_size < min_overlap_words and i > previous_start + 1:
                    i -= 1  # go one sentence back and add to overlap
                    overlap_size += len(sentences[i].split())
            previous_start = i
        else:
            i += 1
    # Add the remaining chunk if any
    if current_chunk:
        chunks.append(current_chunk.strip())
        last_interval = (current_audio_start, intervals[-1][1])
        chunk_intervals.append(last_interval)
    assert len(chunks) == len(chunk_intervals), "Chunks and intervals have different lengths"
    print("Chunks:")
    for n, chunk in enumerate(chunks):
        itv = chunk_intervals[n]
        print(f"- Chunk {n} [{itv[0]} : {itv[1]}]: {chunk}")
    return chunks, chunk_intervals


def create_vectors(chunks: list[str], tei_url: str, request_batch_size: int = 64) -> list[list[float]]:
    # Call embedding service to create chunk vectors
    all_embeddings = []
    for i in range(0, len(chunks), request_batch_size):
        print(f"***** Batch process chunks {i} to {i + request_batch_size} with highest id {len(chunks) - 1}")
        batch = chunks[i : i + request_batch_size]
        payload = {"inputs": batch}
        response = requests.post(tei_url, json=payload)
        embeddings_data = response.json()
        all_embeddings.extend(embeddings_data)
    return all_embeddings
    # opensearch_client = get_opensearch_client()


def create_opensearch_vectors(
    transcript_en_data,
    transcript_en_data_key,
    asr_locale_data,
    asr_locale_key,
    download_data,
    download_meta_urn_key,
    opensearch_vectors_data,
    opensearch_vectors_urn_key,
    use_orchestrator=False,
):
    """
    Creates the opensearch vector entries (of one video) for the opensearch engine.

    :param str transcript_en_data: XCOM data containing URN for the normalized asr result en json.
    :param str transcript_en_data_key: XCOM Data key to used to determine the URN for the normalized asr result en json.
    :param str asr_locale_data: XCOM Data which contains the asr locale.
    :param str asr_locale_key: XCOM Data key to used to determine the asr locale.
    :param str download_data: XCOM data containing URN for the meta data.
    :param str download_meta_urn_key: XCOM Data key to used to determine the URN for the meta data.
    :param str opensearch_vectors_data: XCOM data containing URN for the upload of the opensearch document to assetdb-temp
    :param str opensearch_vectors_urn_key: XCOM Data key to used to determine the URN for the upload of the opensearch document.
    :param bool use_orchestrator: Whether to use inference orchestrator for text embedding service or not.
    """
    import json
    import time
    from collections import Counter
    from io import BytesIO
    from copy import deepcopy
    from airflow.exceptions import AirflowFailException
    from modules.connectors.connector_provider import connector_provider
    from modules.operators.connections import get_assetdb_temp_config, get_connection_config
    from modules.operators.transfer import HansType
    from modules.operators.xcom import get_data_from_xcom
    from modules.operators.opensearch_vectors import create_text_chunks, create_vectors

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()

    # Configure connector_provider and connect assetdb_temp_connector
    connector_provider.configure({"assetdb_temp": assetdb_temp_config})

    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

    # Get locale
    locale = get_data_from_xcom(asr_locale_data, [asr_locale_key])
    print("Locale: " + locale)

    transcript_en_urn = get_data_from_xcom(transcript_en_data, [transcript_en_data_key])
    transcript_en_response = assetdb_temp_connector.get_object(transcript_en_urn)
    if "500 Internal Server Error" in transcript_en_response.data.decode("utf-8"):
        raise AirflowFailException()
    transcript_en_json = json.loads(transcript_en_response.data)
    transcript_en_response.close()
    transcript_en_response.release_conn()

    # Load metadata File
    metadata_urn = get_data_from_xcom(download_data, [download_meta_urn_key])
    meta_response = assetdb_temp_connector.get_object(metadata_urn)
    if "500 Internal Server Error" in meta_response.data.decode("utf-8"):
        raise AirflowFailException()

    meta_data = json.loads(meta_response.data)
    meta_response.close()
    meta_response.release_conn()

    # Get text embedding service remote config
    tei_config = get_connection_config("text_embedding_remote")
    tei_schema = tei_config["schema"]
    tei_host = tei_config["host"]
    tei_port = str(tei_config["port"])

    tei_url_base = tei_schema + "://" + tei_host + ":" + tei_port
    if use_orchestrator is True:
        tei_url_demand = tei_url_base + "/demand_text_embedding_service"  # Todo: verify url defined by orchestrator
        tei_url_info = tei_url_base + "/info"
        # TODO: call demand and check availability with info until TEI service is available
        tei_url = tei_url_base + "/text_embedding_service/embed"
    else:
        tei_url = tei_url_base + "/embed"

    print("***** TEI URL:", tei_url, flush=True)

    sentences_en = [
        s["transcript_formatted"].strip() for s in transcript_en_json["result"] if s["transcript_formatted"].strip()
    ]
    intervals = [s["interval"] for s in transcript_en_json["result"] if s["transcript_formatted"].strip()]
    assert len(sentences_en) == len(intervals), "Sentences and intervals have different lengths"
    print(f"Num sents transcript EN: {len(sentences_en)}")

    entry_meta_data = dict()
    entry_meta_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    entry_meta_data["title"] = meta_data["title"]
    entry_meta_data["course"] = meta_data["description"]["course"]
    entry_meta_data["course_acronym"] = meta_data["description"]["course_acronym"]
    entry_meta_data["faculty"] = meta_data["description"]["faculty"]
    entry_meta_data["faculty_acronym"] = meta_data["description"]["faculty_acronym"]
    entry_meta_data["university"] = meta_data["description"]["university"]
    entry_meta_data["university_acronym"] = meta_data["description"]["university_acronym"]
    entry_meta_data["language"] = meta_data["language"]
    entry_meta_data["tags"] = meta_data["tags"]
    entry_meta_data["lecturer"] = meta_data["description"]["lecturer"]
    entry_meta_data["semester"] = meta_data["description"]["semester"]

    # Create vectors
    chunks, chunk_intervals = create_text_chunks(sentences_en, intervals)
    vectors = create_vectors(chunks, tei_url)
    assert len(chunks) == len(vectors), "Text chunks and vectors have different lengths"
    vector_entries = []
    for n, vector in enumerate(vectors):
        chunk = chunks[n]
        chunk_interval = chunk_intervals[n]
        vector_entry = deepcopy(entry_meta_data)
        vector_entry["lecture_id"] = "<undefined>"  # will be added when inserting entry in vector index
        vector_entry["chunk_id"] = "<undefined>"  # will be added when inserting entry in vector index
        vector_entry["chunk_index"] = n
        vector_entry["chunk_start"] = chunk_interval[0]
        vector_entry["chunk_end"] = chunk_interval[1]
        vector_entry["chunk_text"] = chunk
        vector_entry["embedding"] = vector
        vector_entries.append(vector_entry)

    # Store data
    data = json.dumps(vector_entries).encode("utf-8")
    stream_bytes = BytesIO(data)
    meta_minio = {}
    opensearch_vectors_urn = get_data_from_xcom(opensearch_vectors_data, [opensearch_vectors_urn_key])
    (success, object_name) = assetdb_temp_connector.put_object(
        opensearch_vectors_urn, stream_bytes, HansType.get_mime_type(HansType.SEARCH_DATA_VECTORS), meta_minio
    )
    if not success:
        print("Error uploading search_data_vectors to assetdb-temp!")
        raise AirflowFailException()

    return json.dumps({"result": object_name})


def op_create_opensearch_vectors(
    dag,
    dag_id,
    task_id_suffix,
    transcript_en_data,
    transcript_en_data_key,
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

    :param str transcript_en_data: XCOM data containing URN for the normalized asr result en json.
    :param str transcript_en_data_key: XCOM Data key to used to determine the URN for the normalized asr result en json.
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
        task_id=gen_task_id(dag_id, "op_create_opensearch_vectors", task_id_suffix),
        python_callable=create_opensearch_vectors,
        op_args=[
            transcript_en_data,
            transcript_en_data_key,
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
