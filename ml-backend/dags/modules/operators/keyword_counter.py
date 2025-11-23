from dataclasses import dataclass
import requests
from typing import Optional, Union

from airflow.operators.python import PythonVirtualenvOperator


def run_keyword_counter(keywords: list[str], transcript: str, min_count: int = 2) -> dict[str, int]:
    keyword_2_count = {}
    for keyword in keywords:
        count = transcript.count(keyword.lower())
        keyword_2_count[keyword] = count
    kws_to_remove = [kw for kw, count in keyword_2_count.items() if count < min_count]
    for keyword in kws_to_remove:
        keyword_2_count.pop(keyword)
    # Order keyword in dictionary by count
    keyword_2_count = dict(sorted(keyword_2_count.items(), key=lambda item: item[1], reverse=True))
    for kw, count in keyword_2_count.items():
        print(f"***** Keyword '{kw}': {count}")
    return keyword_2_count


def extend_keywords_with_counts(
    transcript_de_data,
    transcript_de_data_key,
    transcript_en_data,
    transcript_en_data_key,
    keyword_data,
    keyword_data_key,
):
    import json
    from io import BytesIO
    from airflow.exceptions import AirflowFailException
    from connectors.connector_provider import connector_provider
    from modules.operators.connections import get_assetdb_temp_config, get_connection_config
    from modules.operators.transfer import HansType
    from modules.operators.xcom import get_data_from_xcom
    from modules.operators.keyword_counter import run_keyword_counter

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()
    # Configure connector_provider and connect assetdb_temp_connector
    print("***** AssetDB-temp config:", assetdb_temp_config, flush=True)
    connector_provider.configure({"assetdb_temp": assetdb_temp_config})
    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    print("***** AssetDB-temp connector", assetdb_temp_connector, flush=True)
    assetdb_temp_connector.connect()

    # Load keywords json file
    print("***** Keyword data key:", keyword_data_key, flush=True)
    print("***** Keyword data:", keyword_data, flush=True)
    data_urn = get_data_from_xcom(keyword_data, [keyword_data_key])
    print("***** Keyword data urn:", data_urn, flush=True)
    data_response = assetdb_temp_connector.get_object(data_urn)
    if "500 Internal Server Error" in data_response.data.decode("utf-8"):
        raise AirflowFailException()
    keywords_result = json.loads(data_response.data)

    keyword_language = keywords_result["language"]
    if keyword_language == "de":
        print("***** Load DE transcript for keyword count")
        transcript_data = transcript_de_data
        transcript_data_key = transcript_de_data_key
    else:
        print("***** Load EN transcript for keyword count")
        transcript_data = transcript_en_data
        transcript_data_key = transcript_en_data_key

    # Load transcript json file
    data_urn = get_data_from_xcom(transcript_data, [transcript_data_key])
    data_response = assetdb_temp_connector.get_object(data_urn)
    if "500 Internal Server Error" in data_response.data.decode("utf-8"):
        raise AirflowFailException()
    transcript = json.loads(data_response.data)
    data_response.close()
    data_response.release_conn()

    # Count keywords in transcript
    keywords = keywords_result["keywords"]
    full_transcript = " ".join([s["transcript_formatted"].strip() for s in transcript["result"]])
    print("***** Full transcript:", full_transcript)
    keyword_2_count = run_keyword_counter(keywords, full_transcript.lower())
    keywords_result["keywords"] = keyword_2_count
    print("***** Final keyword dict with counts:", keyword_2_count)

    # Upload new json with keyword counts to assetdb-temp, replacing old one
    stream_bytes = BytesIO(json.dumps(keywords_result).encode("utf-8"))
    meta_minio = {}
    upload_result_urn = get_data_from_xcom(keyword_data, [keyword_data_key])
    mime_type = HansType.get_mime_type(HansType.KEYWORDS_RESULT)

    (success, object_name) = assetdb_temp_connector.put_object(upload_result_urn, stream_bytes, mime_type, meta_minio)
    print("***** AssetDB-temp upload success:", success, flush=True)
    print("***** AssetDB-temp upload object name:", object_name, flush=True)
    if not success:
        print(f"***** Error uploading extended Keywords on url {upload_result_urn} to assetdb-temp!", flush=True)
        raise AirflowFailException()

    return json.dumps({"result": object_name})


def op_keyword_counter(
    dag,
    dag_id,
    task_id_suffix,
    transcript_de_data,
    transcript_de_data_key,
    transcript_en_data,
    transcript_en_data_key,
    keyword_data,
    keyword_data_key,
) -> PythonVirtualenvOperator:
    """
    Provides PythonVirtualenvOperator for counting the previously extracted keywords.
    Loads the keywords from the keyword_data XCOM data and counts them in the transcript.
    Re-uploads the keywords with the counts to the assetdb-temp.

    :param str dag: The Airflow DAG where the operator is executed.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id, values: asr_result, transcript
    :param str containerid: Suffix for the DockerOperator container_name.

    :param str transcript_data: XCOM Data which contains data keys.
    :param str transcript_data_key: XCOM Data key which contains the transcript.

    :param str keyword_data: XCOM Data which contains data keys.
    :param str keyword_data_key: XCOM Data key which contains keywords.

    :return: DockerOperator for performing topic segmentation
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_keyword_counter", task_id_suffix),
        python_callable=extend_keywords_with_counts,
        op_args=[
            transcript_de_data,
            transcript_de_data_key,
            transcript_en_data,
            transcript_en_data_key,
            keyword_data,
            keyword_data_key,
        ],
        requirements=["/opt/hans-modules/dist/hans_shared_modules-0.1-py3-none-any.whl"],
        python_version="3",
        dag=dag,
    )
