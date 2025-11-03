from dataclasses import dataclass
import requests
from typing import Optional, Union

from airflow.operators.python import PythonVirtualenvOperator


PIP_REQUIREMENT_MINIO = "minio"


@dataclass
class RawSegment:
    result_index: int
    interval: tuple[float, float]
    text: str

    def update_end(self, end: float):
        self.interval = (self.interval[0], end)


@dataclass
class TopicResultRaw:
    type: str = "TopicResultRaw"
    language: str = "UNK"
    result: Optional[list[RawSegment]] = None


def define_segmentation_config(video_dur: Union[float, int]) -> dict:
    """Define segmentation config (min/max segment dur) based on video duration."""
    min_dur = max(120, int(video_dur / 10))  # min 2 min, or a tenth of the full video
    if video_dur < 600:
        times_min = 2
    elif video_dur < 3600:
        times_min = 3
    else:
        times_min = 4
    max_dur = min(1200, int(times_min * min_dur))  # max 20 min, or {2,3,4} times the min duration
    print(
        f"***** Use segmentation control: {round(min_dur / 60, 1)} min - {round(max_dur / 60, 1)} min "
        f"| Video duration: {round(video_dur / 60, 1)} min"
    )
    return {"max_segment_dur": max_dur, "min_segment_dur": min_dur, "harmonic_distribution": True}


def run_topic_segmentation(sentences: list[str], intervals: list[tuple[float, float]], url: str) -> TopicResultRaw:
    if len(sentences) < 5:
        # If there is an empty transcript or < 5 sentence, segmentation does not make sense.
        # Treat transcript as one segment instead.
        text = " ".join(sentences)
        video_segment = RawSegment(result_index=0, text=text, interval=(intervals[0][0], intervals[-1][1]))
        topic_result = TopicResultRaw(result=[video_segment])
        return topic_result
    payload_config = define_segmentation_config(intervals[-1][1])
    payload = {"text": sentences, "intervals": intervals, "language": "en"} | payload_config
    print(f"***** Sending request to topic segmentation service: {url} with payload: {payload}", flush=True)
    response = requests.post(url, json=payload)
    print("***** Response status code:", response.status_code, flush=True)
    print("***** Response content:", response.content, flush=True)
    resp_segments = response.json()["result"]
    segments = []
    for idx, resp_segment in enumerate(resp_segments):
        segment_text = resp_segment["text"]
        segment_interval = resp_segment["interval"]
        segment = RawSegment(result_index=idx, text=segment_text, interval=segment_interval)
        segments.append(segment)
    topic_result = TopicResultRaw(result=segments)
    return topic_result


def call_segmentation_service(
    download_data, download_data_key, upload_data_topic_result, upload_data_key_topic_result, use_orchestrator=False
):
    import json
    from dataclasses import asdict
    from io import BytesIO
    from airflow.exceptions import AirflowFailException
    from modules.connectors.connector_provider import connector_provider
    from modules.operators.connections import get_assetdb_temp_config, get_connection_config
    from modules.operators.transfer import HansType
    from modules.operators.xcom import get_data_from_xcom
    from modules.operators.topic_segmentation_remote import run_topic_segmentation

    # Get llm remote config
    config = get_connection_config("topic_segmentation_remote")
    schema = config["schema"]
    ts_host = config["host"]
    ts_port = str(config["port"])

    url_base = schema + "://" + ts_host + ":" + ts_port
    if use_orchestrator is True:
        url_demand = url_base + "/demand_topic_segmentation_service"  # Todo: verify url defined by orchestrator
        url_info = url_base + "/info"
        # TODO: call demand and check availability with info until TS service is available
        url = url_base + "/topic_segmentation_service/segment"
    else:
        url = url_base + "/segment"

    print("***** TS URL:", url, flush=True)

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()
    # Configure connector_provider and connect assetdb_temp_connector
    print("***** AssetDB-temp config:", assetdb_temp_config, flush=True)
    connector_provider.configure({"assetdb_temp": assetdb_temp_config})
    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    print("***** AssetDB-temp connector", assetdb_temp_connector, flush=True)
    assetdb_temp_connector.connect()

    # Load EN transcript json file
    print("***** Download data key:", download_data_key, flush=True)
    print("***** Download data:", download_data, flush=True)
    data_urn = get_data_from_xcom(download_data, [download_data_key])
    print("***** VTT data urn:", data_urn, flush=True)
    data_response = assetdb_temp_connector.get_object(data_urn)
    if "500 Internal Server Error" in data_response.data.decode("utf-8"):
        raise AirflowFailException()
    transcript_en_json = json.loads(data_response.data)
    data_response.close()
    data_response.release_conn()

    # Run topic segmentation on transcript sentences and intervals
    sentences_en = [
        s["transcript_formatted"].strip() for s in transcript_en_json["result"] if s["transcript_formatted"].strip()
    ]
    intervals = [s["interval"] for s in transcript_en_json["result"] if s["transcript_formatted"].strip()]
    print("***** Sentences:", sentences_en, flush=True)
    print("***** Intervals:", intervals, flush=True)
    assert len(sentences_en) == len(intervals), "Sentences and intervals have different lengths"
    print(f"***** Num sents transcript EN: {len(sentences_en)}")
    topic_result = run_topic_segmentation(sentences_en, intervals, url)
    topic_result = asdict(topic_result)
    print("***** Topic result dict:", topic_result)

    # Upload raw topic result
    stream_bytes = BytesIO(json.dumps(topic_result).encode("utf-8"))
    meta_minio = {}
    upload_ts_result_urn = get_data_from_xcom(upload_data_topic_result, [upload_data_key_topic_result])
    mime_type = HansType.get_mime_type(HansType.TOPIC_RESULT_RAW)

    print("***** Upload TS result URN:", upload_ts_result_urn, flush=True)
    (success, object_name) = assetdb_temp_connector.put_object(
        upload_ts_result_urn, stream_bytes, mime_type, meta_minio
    )
    print("***** AssetDB-temp upload success:", success, flush=True)
    print("***** AssetDB-temp upload object name:", object_name, flush=True)
    if not success:
        print(f"***** Error uploading TopicResultRaw on url {upload_ts_result_urn} to assetdb-temp!", flush=True)
        raise AirflowFailException()

    return json.dumps({"result": object_name})


def op_topic_segmentation_remote(
    dag,
    dag_id,
    task_id_suffix,
    download_data,
    download_data_key,
    upload_data_topic_result,
    upload_data_key_topic_result,
) -> PythonVirtualenvOperator:
    """
    Provides PythonVirtualenvOperator for a remote topic segmentation service.
    The service is currently using an unsupervised, BERT-based algorithm.
    Creates a topic result file from the vtt file and saves it as topic_result.json in assetdb-temp.

    :param str dag: The Airflow DAG where the operator is executed.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id, values: asr_result, transcript
    :param str containerid: Suffix for the DockerOperator container_name.

    :param str download_data: XCOM Data which contains download urls.
    :param str download_data_key: XCOM Data key to used to determine the download url.

    :param str upload_data_topic_result: XCOM Data which contains upload url for topic result file.
    :param str upload_data_key_topic_result: XCOM Data key to used to determine the upload url.

    :return: DockerOperator for performing topic segmentation
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_topic_segmentation_remote", task_id_suffix),
        python_callable=call_segmentation_service,
        op_args=[download_data, download_data_key, upload_data_topic_result, upload_data_key_topic_result],
        requirements=[PIP_REQUIREMENT_MINIO],
        python_version="3",
        dag=dag,
    )
