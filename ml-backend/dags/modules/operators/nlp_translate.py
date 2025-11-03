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


# Specify minio version to be used in all PythonVirtualenvOperator
PIP_REQUIREMENT_MINIO = "minio"


def gen_payload(prompt):
    """
    Generate payload for request to translation service
    :param str prompt: the user message (prompt)
    :returns dict payload
    """
    return {"inputs": prompt, "parameters": {"max_new_tokens": 512}}


def split_text_into_chunks(text, sentences_per_chunk=4):
    """
    Split text into sentence chunks
    """
    import re

    # List of known abbreviations with periods
    abbreviations = [
        "Mr.",
        "Mrs.",
        "Ms.",
        "Dr.",
        "Prof.",
        "Capt.",
        "Col.",
        "Gen.",
        "Rev.",
        "Lt.",
        "Sgt.",
        "St.",
        "Jr.",
        "Sr.",
        "Co.",
        "Inc.",
        "Ltd.",
        "etc.",
        "Hr.",
        "Fr.",
        "Herr",
        "Frau",
        "u.a.",
        "z.B.",
        "d.h.",
        "i.d.R.",
        "i.e.",
        "u.s.w.",
    ]
    # Define a regular expression pattern to match sentence endings
    sentence_endings = re.compile(r"([.!?])\s+")
    # Initialize an empty list to store sentences
    sentences = []
    start = 0
    # Iterate over the text to find sentence-ending punctuation
    for match in sentence_endings.finditer(text):
        # Extract the sentence-ending character and following space
        end_punct = match.group(1)
        next_char_index = match.end()
        # Get the potential sentence
        sentence = text[start:next_char_index].strip()
        # Check if the preceding token is an abbreviation
        if any(sentence.endswith(abbrev) for abbrev in abbreviations):
            continue
        # Otherwise, consider this a sentence boundary
        sentences.append(sentence)
        start = next_char_index
    # Add any remaining text as the last sentence
    remaining_text = text[start:].strip()
    if remaining_text:
        sentences.append(remaining_text)
    # Initialize the list to store chunks
    chunks = []
    # Group sentences into chunks of the specified number of sentences
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk = " ".join(sentences[i : i + sentences_per_chunk])
        chunks.append(chunk)
    return chunks


def translate_iter(headers, url, content, source_language, target_language):
    """
    Translate long texts
    """
    import requests

    partial_message = ""
    text_arr = split_text_into_chunks(content.strip(), 4)
    for idx, sentence in enumerate(text_arr):
        if len(sentence) > 0:
            prompt = "<2" + target_language + "> " + sentence
            payload = gen_payload(prompt)
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            print("Response status code:", response.status_code)
            print("Response content:", response.content)
            partial_message += response.json()["generated_text"].rsplit("</s>")[0] + " "
    return partial_message.strip()


def request_translation_service(url: str, text: str, source_language: str, target_language: str) -> dict:
    headers = {"Content-Type": "application/json"}
    print(f"Sending request to translation service: {url}")
    return {"result": translate_iter(headers, url, text, source_language, target_language)}


def nlp_translate_remote(
    source_language,
    target_language,
    download_data,
    download_data_key,
    upload_data,
    upload_data_key,
    use_orchestrator=False,
):
    """
    Creates a remote request to a translation service.

    :param str source_language: Source language for translation, could be 'de' or 'en'.
    :param str target_language: Target language for translation, could be 'de' or 'en'.

    :param str download_data: XCOM Data which contains download url for llm json result.
    :param str download_data_key: XCOM Data key to used to determine the download url.

    :param str upload_data: XCOM Data which contains upload url.
    :param str upload_data_key: XCOM Data key to used to determine the upload url.

    :param bool use_orchestrator: Orchestrator between client and service: client <-> orchestrator <-> service , default: False, values: True, False
    """
    import json
    import requests
    from io import BytesIO
    from airflow.exceptions import AirflowFailException
    from modules.connectors.connector_provider import connector_provider
    from modules.operators.connections import get_assetdb_temp_config, get_connection_config
    from modules.operators.xcom import get_data_from_xcom
    from modules.operators.nlp_translate import request_translation_service

    # Get llm remote config
    conn_config = get_connection_config("nlp_translate_remote")
    schema = conn_config["schema"]
    host = conn_config["host"]
    port = str(conn_config["port"])

    url_base = schema + "://" + host + ":" + port
    if use_orchestrator is True:
        url_demand = url_base + "/demand_trl_service"
        url_info = url_base + "/info"
        # TODO: call demand and check availability with info until LLM is available
        url = url_base + "/trl_service/generate"
    else:
        url = url_base + "/generate"

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()

    # Configure connector_provider and connect assetdb_temp_connector
    connector_provider.configure({"assetdb_temp": assetdb_temp_config})
    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

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
                item["title"] = request_translation_service(url, item["title"], source_language, target_language)[
                    "result"
                ]
            if "summary" in item.keys():
                item["summary"] = request_translation_service(url, item["summary"], source_language, target_language)[
                    "result"
                ]
    elif data_type == "ShortSummaryResult" or data_type == "SummaryResult":
        print(f"Start translating {data_type}")
        for item in data["result"]:
            if "summary" in item.keys():
                item["summary"] = request_translation_service(url, item["summary"], source_language, target_language)[
                    "result"
                ]
    elif data_type == "QuestionnaireResult":
        for item in data["result"]:
            if "questionnaire" in item.keys():
                for grade in ["easy", "medium", "difficult"]:
                    for questionitem in item["questionnaire"][grade]:
                        questionitem["mcq"]["question"] = request_translation_service(
                            url, questionitem["mcq"]["question"], source_language, target_language
                        )["result"]
                        questionitem["mcq"]["correct_answer_explanation"] = request_translation_service(
                            url, questionitem["mcq"]["correct_answer_explanation"], source_language, target_language
                        )["result"]
                        for answeritem in questionitem["mcq"]["answers"]:
                            answeritem["answer"] = request_translation_service(
                                url, answeritem["answer"], source_language, target_language
                            )["result"]
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
    use_orchestrator=False,
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
    :param bool use_orchestrator: Orchestrator between client and service: client <-> orchestrator <-> service , default: False, values: True, False

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
            use_orchestrator,
        ],
        requirements=[PIP_REQUIREMENT_MINIO],
        python_version="3",
        dag=dag,
    )
