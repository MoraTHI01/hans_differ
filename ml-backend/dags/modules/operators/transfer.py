#!/usr/bin/env python
"""
Transfer operators.
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


class HansType(Enum):
    """
    Fetch mode to generate pre signed url
    """

    INVALID = 0
    AUDIO = 1  # The raw audio file extracted from PODCAST/VIDEO
    ASR_RESULT = 2  # The ASR result corresponding to AUDIO
    MARKER = 3
    MEDIA = 4  # output dash stream
    META_DATA = 5
    PODCAST = 6  # input audio file
    SEARCH_DATA = 7
    SLIDES = 8
    SLIDES_TEXT_BOUNDARY_BOXES = 9  # mapping of text and boundary boxes in slides
    TIMESTAMPS = 10
    THUMBNAILS_MEDIA = 11
    THUMBNAILS_LECTURER = 12
    TRANSCRIPT = 13  # The transcript corresponding to AUDIO
    VIDEO = 14  # input video file
    SUBTITLE = 15  # subtitle VTT file
    ASR_RESULT_DE = 16  # The ASR result corresponding to AUDIO
    ASR_RESULT_EN = 17  # The ASR result corresponding to AUDIO
    SUBTITLE_DE = 18  # The subtitles VTT file in German corresponding to AUDIO
    SUBTITLE_EN = 19  # The subtitles VTT file in English corresponding to AUDIO
    TRANSCRIPT_DE = 20  # The transcript in German corresponding to AUDIO
    TRANSCRIPT_EN = 21  # The transcript in English corresponding to AUDIO
    SHORT_SUMMARY_RESULT_DE = 22  # The short summary in German corresponding to SUBTITLE_DE/TRANSCRIPT_DE
    SHORT_SUMMARY_RESULT_EN = 23  # The short summary in English corresponding to SUBTITLE_EN/TRANSCRIPT_EN
    SUMMARY_RESULT_DE = 24  # The short summary in German corresponding to SUBTITLE_DE/TRANSCRIPT_DE
    SUMMARY_RESULT_EN = 25  # The short summary in English corresponding to SUBTITLE_EN/TRANSCRIPT_EN
    TOPIC_RESULT_DE = 26  # The segmented topic result in German corresponding to SUBTITLE_DE/TRANSCRIPT_DE
    TOPIC_RESULT_EN = 27  # The segmented topic result in English corresponding to SUBTITLE_EN/TRANSCRIPT_EN
    SEARCH_TRIE_DE = 28  # Search trie for auto completion in German
    SEARCH_TRIE_EN = 29  # Search trie for auto completion in English
    TOPIC_RESULT_RAW = 30  # The topical segmentation of the original English subtitles, without topic names
    QUESTIONNAIRE_RESULT_DE = 31  # The questionnaire in German for each topic result corresponding to TOPIC_RESULT_DE
    QUESTIONNAIRE_RESULT_EN = 32  # The questionnaire in English for each topic result corresponding to TOPIC_RESULT_EN
    SEARCH_DATA_VECTORS = 33  # The lecture chunks incl. vectors
    SEARCH_SLIDE_DATA_VECTOR = 34  # The slides chunks incl. vectors stored in SLIDES_IMAGES_FOLDER as json, e.g. 1.json
    SLIDES_IMAGES_FOLDER = 35  # Converted slide images main folder in bucket
    SLIDES_IMAGES_META = 36  # Based on SEARCH_SLIDE_DATA_VECTOR but includes aggregated cleaned text, markdown, words, urls urls_classified for all slides, 'slides.meta.json'
    SLIDE_IMAGE_DATA = 37  # Converted slide image png in SLIDES_IMAGES_FOLDER, e.g. 1.png
    SLIDE_IMAGE_META = 38  # Based on SEARCH_SLIDE_DATA_VECTOR but includes cleaned text, markdown, words, urls for single slide, e.g. 1.meta.json
    KEYWORDS_RESULT = 39  # The keywords extracted from the slides
    SLIDES_TRIE = 40  # Search trie for auto completion search in slides
    SEARCH_SUMMARY_DATA_VECTOR = 41  # Video vector based on long summary (+tei)
    SPECIAL = 128

    @staticmethod
    def get_file_extension(hans_type):
        """
        Get file extension for a HAnS type

        :param HansType hans_type: HAnS type
        :return: str File extension, e.g. '.json' for HAnS type ASR_RESULT
        """
        hans_type_to_file_extension = {
            HansType.INVALID: "",
            HansType.AUDIO: ".wav",
            HansType.ASR_RESULT: ".json",
            HansType.ASR_RESULT_DE: ".json",
            HansType.ASR_RESULT_EN: ".json",
            HansType.MARKER: ".json",
            HansType.MEDIA: "",
            HansType.META_DATA: ".json",
            HansType.PODCAST: ".mp3",
            HansType.SEARCH_DATA: ".json",
            HansType.SEARCH_DATA_VECTORS: ".json",
            HansType.SEARCH_SLIDE_DATA_VECTOR: ".json",
            HansType.SEARCH_SUMMARY_DATA_VECTOR: ".json",
            HansType.SHORT_SUMMARY_RESULT_DE: ".json",
            HansType.SHORT_SUMMARY_RESULT_EN: ".json",
            HansType.SUMMARY_RESULT_DE: ".json",
            HansType.SUMMARY_RESULT_EN: ".json",
            HansType.SLIDES: ".pdf",
            HansType.SLIDES_TEXT_BOUNDARY_BOXES: ".json",
            HansType.SLIDES_TRIE: ".json",
            HansType.SLIDES_IMAGES_FOLDER: "",
            HansType.SLIDES_IMAGES_META: ".json",
            HansType.SLIDE_IMAGE_DATA: ".png",
            HansType.SLIDE_IMAGE_META: ".json",
            HansType.KEYWORDS_RESULT: ".json",
            HansType.TIMESTAMPS: ".json",
            HansType.THUMBNAILS_MEDIA: "",
            HansType.THUMBNAILS_LECTURER: ".png",
            HansType.TOPIC_RESULT_RAW: ".json",
            HansType.TOPIC_RESULT_DE: ".json",
            HansType.TOPIC_RESULT_EN: ".json",
            HansType.QUESTIONNAIRE_RESULT_DE: ".json",
            HansType.QUESTIONNAIRE_RESULT_EN: ".json",
            HansType.TRANSCRIPT: ".json",
            HansType.TRANSCRIPT_DE: ".json",
            HansType.TRANSCRIPT_EN: ".json",
            HansType.VIDEO: ".mp4",
            HansType.SUBTITLE: ".vtt",
            HansType.SUBTITLE_DE: ".vtt",
            HansType.SUBTITLE_EN: ".vtt",
            HansType.SEARCH_TRIE_DE: ".json",
            HansType.SEARCH_TRIE_EN: ".json",
            HansType.SPECIAL: "",
        }
        return hans_type_to_file_extension[hans_type]

    @staticmethod
    def get_mime_type(hans_type):
        """
        Get mimetype for a HAnS type

        :param HansType hans_type: HAnS type
        :return: str mimetype, e.g. 'application/json' for HAnS type ASR_RESULT
        """
        hans_type_to_mimetype = {
            HansType.INVALID: "application/octet-stream",
            HansType.AUDIO: "audio/wav",
            HansType.ASR_RESULT: "application/json",
            HansType.ASR_RESULT_DE: "application/json",
            HansType.ASR_RESULT_EN: "application/json",
            HansType.MARKER: "application/json",
            HansType.MEDIA: "application/octet-stream",
            HansType.META_DATA: "application/json",
            HansType.PODCAST: "audio/mpeg",
            HansType.SEARCH_DATA: "application/json",
            HansType.SEARCH_DATA_VECTORS: "application/json",
            HansType.SEARCH_SLIDE_DATA_VECTOR: "application/json",
            HansType.SEARCH_SUMMARY_DATA_VECTOR: "application/json",
            HansType.SHORT_SUMMARY_RESULT_DE: "application/json",
            HansType.SHORT_SUMMARY_RESULT_EN: "application/json",
            HansType.SUMMARY_RESULT_DE: "application/json",
            HansType.SUMMARY_RESULT_EN: "application/json",
            HansType.SLIDES: "application/pdf",
            HansType.SLIDES_TEXT_BOUNDARY_BOXES: "application/json",
            HansType.SLIDES_TRIE: "application/json",
            HansType.SLIDES_IMAGES_FOLDER: "",
            HansType.SLIDES_IMAGES_META: "application/json",
            HansType.SLIDE_IMAGE_DATA: "image/png",
            HansType.SLIDE_IMAGE_META: "application/json",
            HansType.KEYWORDS_RESULT: "application/json",
            HansType.TIMESTAMPS: "application/json",
            HansType.THUMBNAILS_MEDIA: "image/png",
            HansType.THUMBNAILS_LECTURER: "image/png",
            HansType.TOPIC_RESULT_RAW: "application/json",
            HansType.TOPIC_RESULT_DE: "application/json",
            HansType.TOPIC_RESULT_EN: "application/json",
            HansType.QUESTIONNAIRE_RESULT_DE: "application/json",
            HansType.QUESTIONNAIRE_RESULT_EN: "application/json",
            HansType.TRANSCRIPT: "application/json",
            HansType.TRANSCRIPT_DE: "application/json",
            HansType.TRANSCRIPT_EN: "application/json",
            HansType.VIDEO: "video/mp4",
            HansType.SUBTITLE: "text/vtt",
            HansType.SUBTITLE_DE: "text/vtt",
            HansType.SUBTITLE_EN: "text/vtt",
            HansType.SEARCH_TRIE_DE: "application/json",
            HansType.SEARCH_TRIE_EN: "application/json",
            HansType.SPECIAL: "application/octet-stream",
        }
        return hans_type_to_mimetype[hans_type]


class Artefact:
    """
    Artefact
    Data structure used to publish data to backend
    """

    parent_dag_id = None
    taskgroup_id = None
    operator_id = None
    artefact_id = None
    hans_type = None
    archive_database = None
    archive_bucket = None
    archive_urn = None
    destination_database = None
    destination_bucket = None
    destination_urn = None
    is_folder = False

    def __init__(
        self,
        parent_dag_id,
        taskgroup_id,
        operator_id,
        artefact_id,
        hans_type: HansType,
        archive_database,
        archive_bucket,
        destination_database,
        destination_bucket,
        is_folder=False,
    ):
        """
        Initialization

        :param str parent_dag_id: Id of the parent dag, e.g. 'parent_dag.dag_id' of the task group and operator
        :param str taskgroup_id: Task group name, which contains the operator
        :param str operator_id: Operator id, id of the operator who provided the artefact
        :param str artefact_id: Artefact id, usually refers to an url on assetdb-temp, e.g. 'video_dash_url'
        :param str hans_type: HAnS type, e.g. 'video'
        :param str archive_database: Name of the database on ml-backend to archive the artefact
        :param str archive_bucket: Name of the bucket in the archive database on ml-backend to store the artefact
        :param str destination_database: Name of the database on backend to store the artefact
        :param str destination_bucket: Name of the bucket in the database on backend to store the artefact
        :param bool is_folder: Specify if the artefact id is pointing to a folder with multiple files, default: False
        """
        self.parent_dag_id = parent_dag_id
        self.taskgroup_id = taskgroup_id
        self.operator_id = operator_id
        self.artefact_id = artefact_id
        self.hans_type = hans_type
        self.archive_database = archive_database
        self.archive_bucket = archive_bucket
        self.destination_database = destination_database
        self.destination_bucket = destination_bucket
        self.is_folder = is_folder


# TRANSFER FILES FROM BACKEND TO ML-BACKEND


def get_remote_config(ext_output_config_json):
    """Helper to get remote config

    :param str ext_output_config_json: JSON containing CONN_ID's with the keys backend and frontend.
    :return: tuple conn_hans_backend, conn_hans_frontend
    """
    import ast
    from airflow.hooks.base_hook import BaseHook
    from airflow.exceptions import AirflowFailException

    ext_backend_config = ast.literal_eval(ext_output_config_json)

    # Get CONN_ID's for frontend and backend
    ext_backend_conn_id = "error"
    ext_frontend_conn_id = "error"
    for item in ext_backend_config:
        if "backend" in item:
            ext_backend_conn_id = item["backend"]
        if "frontend" in item:
            ext_frontend_conn_id = item["frontend"]

    # Resolve CONN_ID's to airflow connection
    conn_hans_backend = BaseHook.get_connection(ext_backend_conn_id)
    conn_hans_frontend = BaseHook.get_connection(ext_frontend_conn_id)

    print("Backend: " + conn_hans_backend.host)
    print("Frontend: " + conn_hans_frontend.host)
    return (conn_hans_backend, conn_hans_frontend)


def gen_url_with_conn(conn, url):
    """
    Helper to create url using conn
    """
    result_url = conn.schema + "://" + conn.host
    port = str(conn.port)
    if port != "":
        result_url += ":" + port
    result_url += url
    return result_url


def authenticate_on_frontend(conn_hans_frontend):
    """Authenticate on frontend

    :param dict conn_hans_frontend: JSON containing credentials for frontend.

    :return: dict Auth headers of frontend api for future requests
    """
    import requests
    from airflow.exceptions import AirflowFailException
    from modules.operators.transfer import gen_url_with_conn

    # Authenticate on frontend and receive JWT access token
    login_url = gen_url_with_conn(conn_hans_frontend, "/api/login")

    print("Login on: " + login_url)
    login_response = requests.get(login_url, auth=(conn_hans_frontend.login, conn_hans_frontend.password))
    try:
        login_response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Error during login on HAnS frontend at " + login_url)
        raise AirflowFailException()

    j = login_response.json()
    print(j)
    return {"accept": "application/json", "Authorization": "Bearer " + j["access_token"]}


def download_and_store_local(ext_metadb_urn, ext_input_files_json, ext_output_config_json):
    """
    Downloads all external media files and stores them in assetsdb-temp.

    It downloads the meta data using ext_metadb_urn and stores it as a file in assetsdb-temp.
    It downloads all input files from the HAnS backend and stores them in the assetsdb-temp.
    It uses the provided CONN_ID's in the ext_output_config_json to connect to the HAnS backend.

    :param str ext_metadb_urn: URN for the meta data.
    :param str ext_input_files_json: JSON containing all input files.
    :param str ext_output_config_json: JSON containing CONN_ID's with the keys backend and frontend.

    :return: str Flat json structure each key starts with hans type and the value type
    """
    import ast
    import json
    import requests
    from airflow.hooks.base_hook import BaseHook
    from airflow.exceptions import AirflowFailException
    from io import BytesIO
    from urllib.request import urlopen
    from modules.connectors.connector_provider import connector_provider
    from modules.connectors.minio_connector import MinioConnectorFetchUrlMode
    from modules.connectors.storage_connector import StorageConnector
    from modules.operators.connections import get_assetdb_temp_config
    from modules.operators.storage import create_url
    from modules.operators.transfer import HansType
    from modules.operators.transfer import get_remote_config
    from modules.operators.transfer import authenticate_on_frontend
    from modules.operators.transfer import gen_url_with_conn

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()
    temp_database = assetdb_temp_config["host"]
    temp_bucket = assetdb_temp_config["bucket"]

    # Configure connector_provider
    connector_provider.configure({"assetdb_temp": assetdb_temp_config})

    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

    # Parse input files
    ext_file_dict = ast.literal_eval(ext_input_files_json)
    # Parse output config
    (conn_hans_backend, conn_hans_frontend) = get_remote_config(ext_output_config_json)

    # Authenticate on frontend and receive JWT access token
    headers_api = authenticate_on_frontend(conn_hans_frontend)

    # Download and store meta data in assetdb-temp
    # Fetch meta data by urn from frontend api
    print("MetaDB urn: " + ext_metadb_urn)
    metadb_uuid = StorageConnector.get_uuid_from_urn(ext_metadb_urn)
    api_request_meta_data = gen_url_with_conn(conn_hans_frontend, "/api/getMetaData?urn=" + ext_metadb_urn)
    metadata_response = requests.get(api_request_meta_data, headers=headers_api)

    metadata_urn = StorageConnector.create_urn(
        temp_database, temp_bucket, metadb_uuid, HansType.get_file_extension(HansType.META_DATA)
    )
    meta_minio = {"X-Amz-Meta-Filename": metadb_uuid + HansType.get_file_extension(HansType.META_DATA)}
    print("MetaDB response code: " + str(metadata_response.status_code))

    if metadata_response.status_code != 200:
        print("Error downloading meta db meta data!")
        raise AirflowFailException()
    if "500 Internal Server Error" in metadata_response.content.decode("utf-8"):
        print("Error downloading meta db meta data!")
        raise AirflowFailException()

    try:
        metadata_response_json = metadata_response.json()
    except requests.exceptions.JSONDecodeError:
        print("Error parsing meta db meta data!")
        raise AirflowFailException()

    if not "result" in metadata_response_json:
        print("Error parsing meta db meta data, no result!")
        raise AirflowFailException()

    metadata_response_json = metadata_response_json["result"]
    print("MetaDB response data:")
    print(metadata_response_json)
    metadata_str = json.dumps(metadata_response_json)

    stream_bytes = BytesIO(bytes(metadata_str, "UTF-8"))
    (success, object_name) = assetdb_temp_connector.put_object(
        metadata_urn, stream_bytes, HansType.get_mime_type(HansType.META_DATA), meta_minio
    )
    if not success:
        print("Error uploading meta db meta data to assetdb-temp!")
        raise AirflowFailException()

    result_json = []
    result_json.append({"meta_urn": metadata_urn})

    # Download and store each input file in assetdb-temp
    for item in ext_file_dict:
        print("Transfering item with urn: " + item["urn"])

        # Fetch download url from urn from frontend api
        api_request_url = gen_url_with_conn(conn_hans_frontend, "/api/getUrl?urn=" + item["urn"] + "&mode=download")
        print(f"Downloading from url: {api_request_url}")
        response = requests.get(api_request_url, headers=headers_api, verify=False)
        response_data = response.json()
        access_url = response_data["result"]["url"]

        # TODO do we need a gateway/reverse proxy on the airflow system
        # to translate to outside servers here?
        if "localhost" in access_url:
            access_url = access_url.replace("localhost", conn_hans_backend.host)
        real_backend_host_url = json.loads(conn_hans_backend.extra)["host_url"]
        real_url_host = conn_hans_backend.schema + "://" + real_backend_host_url
        if real_url_host in access_url:
            access_url = access_url.replace(
                real_url_host, "http://" + conn_hans_backend.host + ":" + str(conn_hans_backend.port)
            )
        print("Download file URL: " + access_url)

        # Open stream for direct transfer
        data = urlopen(access_url)

        # Create urn to store item in assetdb-temp
        temp_urn = temp_database + ":" + temp_bucket + ":" + item["urn"].rsplit(":", 1)[-1]
        # temp_urn = item['urn'].replace("assetdb:raw:", temp_database + ":" + temp_bucket + ":")
        print("Upload file urn: " + temp_urn)

        metaMinio = {"X-Amz-Meta-Filename": item["filename"], "X-Amz-Meta-Language": item["locale"]}
        result = assetdb_temp_connector.put_object_unknown_size(temp_urn, data, metaMinio)
        print(f"Transfered item to urn: {result}")
        hans_type_url = item["hans-type"] + "_url"
        json_text = create_url(hans_type_url, temp_urn, MinioConnectorFetchUrlMode.DOWNLOAD)
        result_json.append(json.loads(json_text))
        result_json.append({item["hans-type"] + "_urn": temp_urn})
        result_json.append({item["hans-type"] + "_filename": item["filename"]})
        result_json.append({item["hans-type"] + "_locale": item["locale"]})
        result_json.append({item["hans-type"] + "_type": item["mime-type"]})

    # implicit XCOM push
    return json.dumps(result_json)


def op_download_and_store_local(
    dag, dag_id, task_id_suffix, ext_metadb_urn, ext_input_files_json, ext_output_config_json
):
    """
    Provides PythonVirtualenvOperator to transfer all external media files from backend
    to the airflow assetdb-temp local storage.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str ext_metadb_urn: URN for the meta data.
    :param str ext_input_files_json: JSON containing all input files.
    :param str ext_output_config_json: JSON containing CONN_ID's with the keys backend and frontend.

    :return: PythonVirtualenvOperator Operator to transfer files from HAnS backend to assetdb-temp
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_download_and_store_local", task_id_suffix),
        python_callable=download_and_store_local,
        op_args=[ext_metadb_urn, ext_input_files_json, ext_output_config_json],
        requirements=[PIP_REQUIREMENT_MINIO, "eval-type-backport", "requests"],
        python_version="3",
        dag=dag,
    )


# TRANSFER FILE FROM ML-BACKEND TO BACKEND


def create_upload_url(conn_hans_frontend, auth_header, conn_hans_backend, urn):
    """
    Helper to create upload url on HAnS backend to upload data

    :param BaseHook.Connection conn_hans_frontend: Connection to HAnS frontend
    :param dict auth_header: Authentication header for HAnS frontend
    :param BaseHook.Connection conn_hans_backend: Connection to HAnS backend
    :param str urn: URN to be used to create the upload url
    """
    import requests
    from urllib.parse import quote
    from airflow.exceptions import AirflowFailException
    from modules.operators.transfer import gen_url_with_conn

    api_request_url = gen_url_with_conn(conn_hans_frontend, "/api/getUrl?urn=" + quote(urn) + "&mode=upload")
    print(f"api_request_url: {api_request_url}")
    response = requests.get(api_request_url, headers=auth_header)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Error creating upload url for urn " + urn)
        raise AirflowFailException()

    response_data = response.json()
    access_url = response_data["result"]["url"]

    # TODO do we need a gateway/reverse proxy on the airflow system
    # to translate to outside servers here?
    if "localhost" in access_url:
        access_url = access_url.replace("localhost", conn_hans_backend.host)
    print("Upload file URL to HAnS backend: " + access_url)
    return access_url


def transfer_file_to_remote(assetdb_temp_connector, download_urn, upload_url, upload_headers, artefact):
    """
    Helper to transfer byte data from download url to upload url for an artefact.

    :param MinioConnector assetdb_temp_connector: Connector for assetdb-temp
    :param str download_url: Url to download data, e.g. from assetdb-temp
    :param str upload_url: Url to upload data, e.g. to assetdb on HAnS backend
    :param dict upload_headers: Headers for upload
    :param Artefact artefact: Artefact to be published.
    """
    import requests
    from airflow.exceptions import AirflowFailException
    from datetime import datetime
    from modules.operators.transfer import HansType

    download_response = assetdb_temp_connector.get_object(download_urn)
    if download_response is None:
        print("Error downloading from urn: " + download_urn)
        raise AirflowFailException()
    if not hasattr(download_response, "data"):
        print("Error downloading, data empty for urn: " + download_urn)
        raise AirflowFailException()
    response = None
    mime_type = HansType.get_mime_type(artefact.hans_type)
    if mime_type.lower() == "application/json":
        response = requests.put(upload_url, data=download_response.data, headers=upload_headers, allow_redirects=True)
    else:
        dt = datetime.now()
        # TODO: Refactor for large binary files, storing on FS is slow so byte buffer maybe? FS vs. RAM
        temp_file = "/tmp/temp" + str(dt.microsecond) + ".data"
        with open(temp_file, "wb") as f:
            f.write(download_response.data)
        response = requests.put(upload_url, data=open(temp_file, "rb"), headers=upload_headers, allow_redirects=True)
    if response is None:
        print("Error upload response empty! Artefact: " + artefact.artefact_id)
        raise AirflowFailException()
    try:
        response.raise_for_status()
        print("Upload data finished!", flush=True)
    except requests.exceptions.HTTPError as err:
        print("Error uploading artefact " + artefact.artefact_id)
        raise AirflowFailException()


def download_and_store_remote(ext_output_config_json, artefact, artefact_download_data, final_uuid):
    """
    Downloads a file from assetdb-temp and transfers it to HAnS backend database

    It uses the provided CONN_ID's in the ext_output_config_json to connect to the HAnS backend.

    :param str ext_output_config_json: JSON containing CONN_ID's with the keys backend and frontend.


    :param Artefact artefact: Artefact to be published.
    :param str artefact_download_data: XCOM Data which contains download url for Artefact.
    :param str final_uuid: Upload UUID of the artefact on the HAnS backend.

    :return: str JSON for XCOM with the key 'result'
    """
    import json
    import requests
    from airflow.exceptions import AirflowFailException
    from io import BytesIO
    from modules.connectors.connector_provider import connector_provider
    from modules.connectors.storage_connector import StorageConnector
    from modules.operators.connections import get_assetdb_temp_config
    from modules.operators.transfer import HansType
    from modules.operators.transfer import get_remote_config, create_upload_url
    from modules.operators.transfer import transfer_file_to_remote
    from modules.operators.transfer import authenticate_on_frontend
    from modules.operators.xcom import get_data_from_xcom

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()

    # Configure connector_provider and connect assetdb_temp_connector
    connector_provider.configure({"assetdb_temp": assetdb_temp_config})

    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

    # Parse output config
    (conn_hans_backend, conn_hans_frontend) = get_remote_config(ext_output_config_json)

    # Authenticate on frontend and receive JWT access token
    headers_api = authenticate_on_frontend(conn_hans_frontend)

    print("Artefact id: " + artefact.artefact_id)

    items = []
    if artefact.is_folder:
        artefact_urn = get_data_from_xcom(artefact_download_data, [artefact.artefact_id])
        print("Artefact folder urn: " + artefact_urn)
        objects = assetdb_temp_connector.list_objects(artefact_urn)
        for obj in objects:
            filepath = str(obj.object_name)
            name_with_fext = filepath.split("/", maxsplit=1)[-1]
            arr = name_with_fext.rsplit(".", maxsplit=1)
            name_without_fext = arr[0]
            fext = arr[-1]
            download_urn = artefact_urn + "/" + name_with_fext
            mime_type = HansType.get_mime_type(artefact.hans_type)
            upload_headers = {"content-type": "application/json"}
            if "mpd" in fext:
                upload_headers["content-type"] = "application/dash+xml"
            elif "m4s" in fext:
                upload_headers["content-type"] = "video/mp4"
            else:
                upload_headers["content-type"] = mime_type
            item = {
                "download_urn": download_urn,
                "uuid": final_uuid + "/" + name_without_fext,
                "file_ext": "." + fext,
                "upload_headers": upload_headers,
            }
            items.append(item)
    else:
        download_urn = get_data_from_xcom(artefact_download_data, [artefact.artefact_id])
        if download_urn is None:
            print("Could not get data from xcom for artefact id")
            raise AirflowFailException()
        fext = HansType.get_file_extension(artefact.hans_type)
        mime_type = HansType.get_mime_type(artefact.hans_type)
        upload_headers = {"content-type": "application/json"}
        if "mpd" in fext:
            upload_headers["content-type"] = "application/dash+xml"
        elif "m4s" in fext:
            upload_headers["content-type"] = "video/mp4"
        else:
            upload_headers["content-type"] = mime_type
        item = {"download_urn": download_urn, "uuid": final_uuid, "file_ext": fext, "upload_headers": upload_headers}
        items.append(item)

    artefact_urn = None
    for item in items:
        print("Download file URN on assetdb-temp: " + str(item["download_urn"]))

        # Create upload url
        urn = StorageConnector.create_urn(
            artefact.destination_database, artefact.destination_bucket, item["uuid"], item["file_ext"]
        )
        upload_url = create_upload_url(conn_hans_frontend, headers_api, conn_hans_backend, urn)
        real_backend_host_url = json.loads(conn_hans_backend.extra)["host_url"]
        real_url_host = conn_hans_backend.schema + "://" + real_backend_host_url
        if real_url_host in upload_url:
            upload_url = upload_url.replace(
                real_url_host, "http://" + conn_hans_backend.host + ":" + str(conn_hans_backend.port)
            )

        transfer_file_to_remote(
            assetdb_temp_connector, item["download_urn"], upload_url, item["upload_headers"], artefact
        )
        # if artefact.is_folder and "mpd" in item["file_ext"]:
        artefact_urn = urn
        # elif not artefact.is_folder:
        #    artefact_urn = urn

    if artefact_urn is None:
        print("Error artefact_urn is empty for hans_type: " + artefact.hans_type.name.lower())
        raise AirflowFailException()

    # implicit XCOM push
    return json.dumps({artefact.hans_type.name.lower(): artefact_urn})


def op_download_and_store_remote(
    dag,
    dag_id,
    task_id_suffix,
    dag_group_name_download_media_files,
    download_data,
    ext_output_config_json,
    artefact,
    final_uuid,
):
    """
    Provides PythonVirtualenvOperator to transfer one artefact from
    airflow assetdb-temp local storage to HAnS backend.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str dag_group_name_download_media_files: Task group name for
    download_media_files task group
    :param str download_data: XCOM Data which contains download urls and urns for metadb.
    :param str ext_output_config_json: JSON containing CONN_ID's with the keys backend and frontend.

    :param Artefact artefact: Artefact to be published.
    :param str final_uuid: Upload UUID of the artefact on the HAnS backend.

    :return: PythonVirtualenvOperator Operator to transfer files from assetdb-temp to HAnS backend
    """
    from modules.operators.xcom import gen_task_id, inject_xcom_data

    if artefact.taskgroup_id == dag_group_name_download_media_files:
        return PythonVirtualenvOperator(
            task_id=gen_task_id(dag_id, "op_download_and_store_remote", task_id_suffix),
            python_callable=download_and_store_remote,
            op_args=[ext_output_config_json, artefact, download_data, final_uuid],
            requirements=[PIP_REQUIREMENT_MINIO, "eval-type-backport", "requests", "urllib3"],
            python_version="3",
            dag=dag,
        )
    else:
        return PythonVirtualenvOperator(
            task_id=gen_task_id(dag_id, "op_download_and_store_remote", task_id_suffix),
            python_callable=download_and_store_remote,
            op_args=[
                ext_output_config_json,
                artefact,
                inject_xcom_data(
                    artefact.parent_dag_id, artefact.taskgroup_id, artefact.operator_id, artefact.artefact_id
                ),
                final_uuid,
            ],
            requirements=[PIP_REQUIREMENT_MINIO, "eval-type-backport", "requests", "urllib3"],
            python_version="3",
            dag=dag,
        )


# TRANSFER META DATA AND PUBLISH FINALLY ON FRONTEND + BACKEND


def gen_publish_artefacts_xcom_data(parent_dag, dag_group_name_publish_artefacts, artefacts):
    """
    Helper to fetch XCOM data for artefacts
    op_download_and_store_remote tasks

    :param DAG parent_dag: Parent DAG instance
    :param str dag_group_name_publish_artefacts: Task group name for publish_artefacts task group
    :param str artefacts: List of artefacts to be published on backend

    :return: str XCOM data template
    """
    # XCOM injection helper
    from modules.operators.xcom import inject_xcom_data

    artefacts_xcom_data = []
    for artefact in artefacts:
        artefacts_xcom_data.append(
            inject_xcom_data(
                parent_dag.dag_id,
                dag_group_name_publish_artefacts,
                "op_download_and_store_remote",
                "publish_artefact_" + artefact.artefact_id,
            )
        )
    return artefacts_xcom_data


def gen_artefacts_xcom_data(artefacts):
    """
    Helper to fetch XCOM data for a list of artefacts

    :param DAG parent_dag: Parent DAG instance
    :param str artefacts: List of artefacts to be published on backend

    :return: str XCOM data template
    """
    # XCOM injection helper
    from modules.operators.xcom import inject_xcom_data

    artefacts_xcom_data = []
    for artefact in artefacts:
        artefacts_xcom_data.append(
            inject_xcom_data(artefact.parent_dag_id, artefact.taskgroup_id, artefact.operator_id, artefact.artefact_id)
        )
    return artefacts_xcom_data


def publish(
    dag_id,
    ext_output_config_json,
    download_data,
    artefacts,
    artefacts_xcom_data,
    download_artefacts,
    download_artefacts_xcom_data,
    media_artefact,
    media_artefacts_xcom_data,
    multiple_files_artefacts,
    multiple_files_artefacts_xcom_data,
    meta_artefact,
    time_started,
):
    """
    Publish meta data by loading meta data from assetdb-temp and
    call frontend url with meta data to trigger publishing on HAnS frontend + backend.

    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.

    :param str ext_output_config_json: JSON containing CONN_ID's with the keys backend and frontend.
    :param str download_data: XCOM Data which contains download urls and urns for metadb.

    :param list artefacts: List of type Artefact which contains all already uploaded artefacts.
    :param list artefacts_xcom_data: List of XCOM data published by the op_download_and_store_remote for the artefacts.

    :param list download_artefacts: List of type Artefact which contains all already uploaded download_artefacts.
    :param list download_artefacts_xcom_data: List of XCOM data published by the op_download_and_store_remote for the download_artefacts.

    :param Artefact media_artefact: Artefact which contains the media data for publishing
    :param list media_artefacts_xcom_data: List of XCOM data published by the op_download_and_store_remote for the media_artefacts.

    :param Artefact multiple_files_artefacts: List of artefacts which contains the media thumbnails data, and slides images data
    :param list multiple_files_artefacts_xcom_data: List of XCOM data published by the op_download_and_store_remote for the multiple_files_artefacts.

    :param Artefact meta_artefact: Artefact which contains the meta data to be published.
    :param str time_started: Start time of the DAG added into meta data.

    :return: str JSON for XCOM with the key 'result'.
    """
    import json
    import requests
    from airflow.exceptions import AirflowFailException
    from datetime import datetime
    from modules.connectors.connector_provider import connector_provider
    from modules.connectors.storage_connector import StorageConnector
    from modules.operators.connections import get_assetdb_temp_config
    from modules.operators.transfer import HansType
    from modules.operators.transfer import get_remote_config
    from modules.operators.transfer import authenticate_on_frontend
    from modules.operators.xcom import get_data_from_xcom
    from modules.operators.transfer import gen_url_with_conn

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()

    # Configure connector_provider and connect assetdb_temp_connector
    connector_provider.configure({"assetdb_temp": assetdb_temp_config})

    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

    # Parse output config
    (conn_hans_backend, conn_hans_frontend) = get_remote_config(ext_output_config_json)

    # Authenticate on frontend and receive JWT access token
    headers_api = authenticate_on_frontend(conn_hans_frontend)

    # Update metadb data
    print("Artefact id: " + meta_artefact.artefact_id)
    metadb_urn = get_data_from_xcom(download_data, [meta_artefact.artefact_id])
    metadb_uuid = StorageConnector.get_uuid_from_urn(metadb_urn)
    print("MetaDB data urn on assetdb-temp: " + metadb_urn)

    meta_response = assetdb_temp_connector.get_object(metadb_urn)
    if "500 Internal Server Error" in meta_response.data.decode("utf-8"):
        print("Error fetching meta data")
        raise AirflowFailException()

    meta_data_in_str = meta_response.data.decode("utf-8")
    print("Meta data: " + meta_data_in_str)
    meta_data = json.loads(meta_data_in_str)

    artefacts = artefacts + [media_artefact] + multiple_files_artefacts
    artefacts_xcom_data = artefacts_xcom_data + media_artefacts_xcom_data + multiple_files_artefacts_xcom_data
    for artefact in artefacts:
        print(artefact.artefact_id)
        print(artefact.hans_type)
        meta_data_entry = artefact.hans_type.name.lower()
        print("Adding new meta data entry: " + meta_data_entry)
        artefact_destination_urn = None
        for xcom_data in artefacts_xcom_data:
            artefact_destination_urn = get_data_from_xcom(xcom_data, [meta_data_entry])
            if artefact_destination_urn is not None:
                break
        if artefact_destination_urn is None:
            print("Error artefact_destination_urn is empty for hans_type: " + artefact.hans_type.name)
            raise AirflowFailException()

        print("Value: " + artefact_destination_urn)
        if artefact.hans_type is HansType.THUMBNAILS_MEDIA:
            if not "thumbnails" in meta_data:
                meta_data["thumbnails"] = {}
            meta_data["thumbnails"]["media"] = artefact_destination_urn
        if artefact.hans_type is HansType.SLIDES_IMAGES_META:
            if not "slides_images_meta" in meta_data:
                meta_data["slides_images_meta"] = {}
            meta_data["slides_images_meta"] = artefact_destination_urn
        elif artefact.hans_type is HansType.THUMBNAILS_LECTURER:
            if not "thumbnails" in meta_data:
                meta_data["thumbnails"] = {}
            meta_data["thumbnails"]["lecturer"] = artefact_destination_urn
        else:
            meta_data[meta_data_entry] = artefact_destination_urn

    for artefact in download_artefacts:
        print(artefact.artefact_id)
        print(artefact.hans_type)
        meta_data_entry = artefact.hans_type.name.lower()
        print("Adding new meta data entry: " + meta_data_entry)
        artefact_destination_urn = None
        for xcom_data in download_artefacts_xcom_data:
            artefact_destination_urn = get_data_from_xcom(xcom_data, [meta_data_entry])
            if artefact_destination_urn is not None:
                break
        if artefact_destination_urn is None:
            print("Error artefact_destination_urn is empty for hans_type: " + artefact.hans_type.name)
            raise AirflowFailException()

        print("Value: " + artefact_destination_urn)
        if artefact.hans_type is HansType.THUMBNAILS_MEDIA:
            if not "thumbnails" in meta_data:
                meta_data["thumbnails"] = {}
            meta_data["thumbnails"]["media"] = artefact_destination_urn
        if artefact.hans_type is HansType.SLIDES_IMAGES_META:
            if not "slides_images_meta" in meta_data:
                meta_data["slides_images_meta"] = {}
            meta_data["slides_images_meta"] = artefact_destination_urn
        elif artefact.hans_type is HansType.THUMBNAILS_LECTURER:
            if not "thumbnails" in meta_data:
                meta_data["thumbnails"] = {}
            meta_data["thumbnails"]["lecturer"] = artefact_destination_urn
        else:
            meta_data[meta_data_entry] = artefact_destination_urn

    # Add additional versioning info and stats
    meta_data["airflow_info"] = {}
    meta_data["airflow_info"]["dag_id"] = dag_id
    meta_data["airflow_info"]["dag_version"] = str(dag_id).rsplit("_", maxsplit=1)[-1]
    meta_data["airflow_info"]["started"] = time_started
    now = datetime.now()
    meta_data["airflow_info"]["ended"] = now.strftime("%m_%d_%Y_%H_%M_%S")

    print("Final meta data:")
    meta_data_str = json.dumps(meta_data)
    print(meta_data_str)

    api_publish_url = gen_url_with_conn(conn_hans_frontend, "/api/publish")

    data = {"uuid": metadb_uuid, "data": meta_data_str, "from_package": False, "editing_progress": -1}
    headers = {"Content-Type": "application/json; charset=utf-8"}
    headers.update(headers_api)
    response = requests.post(api_publish_url, headers=headers, json=data)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Error publishing meta data on HAnS frontend " + conn_hans_frontend.host)
        print(err)
        raise AirflowFailException()

    # implicit XCOM push
    return json.dumps({"result": meta_data_str})


def op_publish(
    dag,
    dag_id,
    task_id_suffix,
    ext_output_config_json,
    download_data,
    artefacts,
    artefacts_xcom_data,
    download_artefacts,
    download_artefacts_xcom_data,
    media_artefact,
    media_artefacts_xcom_data,
    multiple_files_artefacts,
    multiple_files_artefacts_xcom_data,
    meta_artefact,
    time_started,
):
    """
    Provides PythonVirtualenvOperator to publish final meta data
    and trigger the publish method on HAnS frontend.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str ext_output_config_json: JSON containing CONN_ID's with the keys backend and frontend.
    :param str download_data: XCOM Data which contains download urls and urns for metadb.

    :param list artefacts: List of type Artefact which contains all already uploaded artefacts.
    :param list artefacts_xcom_data: List of XCOM data published by the op_download_and_store_remote for the artefacts.

    :param list download_artefacts: List of type Artefact which contains all already uploaded download_artefacts.
    :param list download_artefacts_xcom_data: List of XCOM data published by the op_download_and_store_remote for the download_artefacts.

    :param Artefact media_artefact: Artefact which contains the media data for publishing
    :param list media_artefacts_xcom_data: List of XCOM data published by the op_download_and_store_remote for the media_artefacts.

    :param Artefact multiple_files_artefacts: List of artefacts which contains the media thumbnails data, and slides images data
    :param list multiple_files_artefacts_xcom_data: List of XCOM data published by the op_download_and_store_remote for the multiple_files_artefacts.

    :param Artefact meta_artefact: Artefact which contains the meta data to be published.
    :param str time_started: Start time of the DAG added into meta data.

    :return: PythonVirtualenvOperator Operator to publish final meta data.
    and trigger the publish method on HAnS frontend
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_publish", task_id_suffix),
        python_callable=publish,
        op_args=[
            dag_id,
            ext_output_config_json,
            download_data,
            artefacts,
            artefacts_xcom_data,
            download_artefacts,
            download_artefacts_xcom_data,
            media_artefact,
            media_artefacts_xcom_data,
            multiple_files_artefacts,
            multiple_files_artefacts_xcom_data,
            meta_artefact,
            time_started,
        ],
        requirements=[PIP_REQUIREMENT_MINIO, "eval-type-backport", "requests", "urllib3"],
        python_version="3",
        dag=dag,
    )


def publish_update(
    dag_id,
    ext_output_config_json,
    download_data,
    artefacts,
    artefacts_xcom_data,
    download_artefacts,
    download_artefacts_xcom_data,
    meta_artefact,
    time_started,
    editing_progress,
):
    """
    Publish meta data by loading meta data from assetdb-temp and
    call frontend url with meta data to trigger publishing on HAnS frontend + backend.

    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.

    :param str ext_output_config_json: JSON containing CONN_ID's with the keys backend and frontend.
    :param str download_data: XCOM Data which contains download urls and urns for metadb.

    :param list artefacts: List of type Artefact which contains all already uploaded artefacts.
    :param list artefacts_xcom_data: List of XCOM data published by the op_download_and_store_remote for the artefacts.

    :param list download_artefacts: List of type Artefact which contains all already uploaded download_artefacts.
    :param list download_artefacts_xcom_data: List of XCOM data published by the op_download_and_store_remote for the download_artefacts.

    :param Artefact meta_artefact: Artefact which contains the meta data to be published.
    :param str time_started: Start time of the DAG added into meta data.
    :param int editing_progress: Progress step on frontend to be set

    :return: str JSON for XCOM with the key 'result'.
    """
    import json
    import requests
    from airflow.exceptions import AirflowFailException
    from datetime import datetime
    from modules.connectors.connector_provider import connector_provider
    from modules.connectors.storage_connector import StorageConnector
    from modules.operators.connections import get_assetdb_temp_config
    from modules.operators.transfer import HansType
    from modules.operators.transfer import get_remote_config
    from modules.operators.transfer import authenticate_on_frontend
    from modules.operators.xcom import get_data_from_xcom
    from modules.operators.transfer import gen_url_with_conn

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()

    # Configure connector_provider and connect assetdb_temp_connector
    connector_provider.configure({"assetdb_temp": assetdb_temp_config})

    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

    # Parse output config
    (conn_hans_backend, conn_hans_frontend) = get_remote_config(ext_output_config_json)

    # Authenticate on frontend and receive JWT access token
    headers_api = authenticate_on_frontend(conn_hans_frontend)

    # Update metadb data
    print("Artefact id: " + meta_artefact.artefact_id)
    metadb_urn = get_data_from_xcom(download_data, [meta_artefact.artefact_id])
    metadb_uuid = StorageConnector.get_uuid_from_urn(metadb_urn)
    print("MetaDB data urn on assetdb-temp: " + metadb_urn)

    meta_response = assetdb_temp_connector.get_object(metadb_urn)
    if "500 Internal Server Error" in meta_response.data.decode("utf-8"):
        print("Error fetching meta data")
        raise AirflowFailException()

    meta_data_in_str = meta_response.data.decode("utf-8")
    print("Meta data: " + meta_data_in_str)
    meta_data = json.loads(meta_data_in_str)

    for artefact in artefacts:
        print(artefact.artefact_id)
        print(artefact.hans_type)
        meta_data_entry = artefact.hans_type.name.lower()
        print("Adding new meta data entry: " + meta_data_entry)
        artefact_destination_urn = None
        for xcom_data in artefacts_xcom_data:
            artefact_destination_urn = get_data_from_xcom(xcom_data, [meta_data_entry])
            if artefact_destination_urn is not None:
                break
        if artefact_destination_urn is None:
            print("Error artefact_destination_urn is empty for hans_type: " + artefact.hans_type.name)
            raise AirflowFailException()

        print("Value: " + artefact_destination_urn)
        meta_data[meta_data_entry] = artefact_destination_urn

    for artefact in download_artefacts:
        print(artefact.artefact_id)
        print(artefact.hans_type)
        meta_data_entry = artefact.hans_type.name.lower()
        print("Adding new meta data entry: " + meta_data_entry)
        artefact_destination_urn = None
        for xcom_data in download_artefacts_xcom_data:
            artefact_destination_urn = get_data_from_xcom(xcom_data, [meta_data_entry])
            if artefact_destination_urn is not None:
                break
        if artefact_destination_urn is None:
            print("Error artefact_destination_urn is empty for hans_type: " + artefact.hans_type.name)
            raise AirflowFailException()

        print("Value: " + artefact_destination_urn)
        meta_data[meta_data_entry] = artefact_destination_urn

    # Add additional versioning info and stats
    meta_data["airflow_info"] = {}
    meta_data["airflow_info"]["dag_id"] = dag_id
    meta_data["airflow_info"]["dag_version"] = str(dag_id).rsplit("_", maxsplit=1)[-1]
    meta_data["airflow_info"]["started"] = time_started
    now = datetime.now()
    meta_data["airflow_info"]["ended"] = now.strftime("%m_%d_%Y_%H_%M_%S")

    print("Final meta data:")
    meta_data_str = json.dumps(meta_data)
    print(meta_data_str)

    api_publish_url = gen_url_with_conn(conn_hans_frontend, "/api/publish-update")

    data = {"uuid": metadb_uuid, "data": meta_data_str, "from_package": False, "editing_progress": editing_progress}
    headers = {"Content-Type": "application/json; charset=utf-8"}
    headers.update(headers_api)
    print(f"Final publishing to: {api_publish_url}")
    try:
        response = requests.post(api_publish_url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Error publishing meta data on HAnS frontend " + conn_hans_frontend.host)
        print(err)
        raise AirflowFailException()

    # implicit XCOM push
    return json.dumps({"result": meta_data_str})


def op_publish_update(
    dag,
    dag_id,
    task_id_suffix,
    ext_output_config_json,
    download_data,
    artefacts,
    artefacts_xcom_data,
    download_artefacts,
    download_artefacts_xcom_data,
    meta_artefact,
    time_started,
    editing_progress,
):
    """
    Provides PythonVirtualenvOperator to publish final meta data
    and trigger the publish method on HAnS frontend.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str ext_output_config_json: JSON containing CONN_ID's with the keys backend and frontend.
    :param str download_data: XCOM Data which contains download urls and urns for metadb.

    :param list artefacts: List of type Artefact which contains all already uploaded artefacts.
    :param list artefacts_xcom_data: List of XCOM data published by the op_download_and_store_remote for the artefacts.

    :param list download_artefacts: List of type Artefact which contains all already uploaded download_artefacts.
    :param list download_artefacts_xcom_data: List of XCOM data published by the op_download_and_store_remote for the download_artefacts.

    :param Artefact meta_artefact: Artefact which contains the meta data to be published.
    :param str time_started: Start time of the DAG added into meta data.
    :param int editing_progress: Progress step on frontend to be set

    :return: PythonVirtualenvOperator Operator to publish final meta data.
    and trigger the publish method on HAnS frontend
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_publish_update", task_id_suffix),
        python_callable=publish_update,
        op_args=[
            dag_id,
            ext_output_config_json,
            download_data,
            artefacts,
            artefacts_xcom_data,
            download_artefacts,
            download_artefacts_xcom_data,
            meta_artefact,
            time_started,
            editing_progress,
        ],
        requirements=[PIP_REQUIREMENT_MINIO, "eval-type-backport", "requests", "urllib3"],
        python_version="3",
        dag=dag,
    )


# ARCHIVE ALL META DATA AND FILES FINALLY ON ASSETDB-TEMP ARCHIVE


def archive_artefact_metadata(dag_id, assetdb_temp_connector, artefact, artefact_urn, target_urn, time_started):
    """
    Archives artefact meta data on archive bucket

    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param assetdb_temp_connector assetdb_temp_connector: Connector
    :param Artefact artefact: Artefact
    :param str artefact_urn: URN of the artefact
    :param str target_urn: Main URN on the archive bucket
    :param str time_started: Start time of the DAG added into meta data.

    :return: bool True if successful, False otherwise
    """
    import json
    from io import BytesIO
    from datetime import datetime

    artefact_file = artefact_urn.rsplit(":")[-1]
    destination_urn = target_urn + "/" + artefact_file + ".meta.json"
    print("Meta data will be stored using following urn: %s", destination_urn)
    # Store data
    now = datetime.now()
    json_data = {
        "artefact_id": artefact.artefact_id,
        "artefact_file": artefact_file,
        "archive_database": artefact.archive_database,
        "archive_bucket": artefact.archive_bucket,
        "destination_database": artefact.destination_database,
        "destination_bucket": artefact.destination_bucket,
        "hans_type": artefact.hans_type.name,
        "mime_type": HansType.get_mime_type(artefact.hans_type),
        "is_folder": artefact.is_folder,
        "airflow_info": {
            "dag_id": dag_id,
            "dag_version": str(dag_id).rsplit("_", maxsplit=1)[-1],
            "started": time_started,
            "ended": now.strftime("%m_%d_%Y_%H_%M_%S"),
        },
    }

    data = json.dumps(json_data).encode("utf-8")
    stream_bytes = BytesIO(data)
    meta_minio = {}
    (success, object_name) = assetdb_temp_connector.put_object(
        destination_urn, stream_bytes, "application/json", meta_minio
    )
    print("Artefact meta data stored: %s", object_name)
    return success


def archive_artefacts(
    dag_id, download_artefacts, download_artefacts_data, artefacts, artefacts_data, final_uuid, time_started
):
    """
    Archives artefacts from assetdb-temp assets-temp bucket to new
    object on archive bucket

    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param list(Artefact) download_artefacts: Download artefacts to be archived.
    :param str download_artefacts_data: XCOM Data which contains
    download urls and urns for each download Artefact.

    :param list(Artefact) artefacts: Artefacts to be archived.
    :param list(str) artefacts_data: List of XCOM Data which contains
    download url for each Artefact.

    :param str final_uuid: Combine UUID of the artefact on assetdb-temp archive bucket.
    :param str time_started: Start time of the DAG added into meta data.

    :return: str JSON for XCOM with the key 'result'
    """
    import json
    from airflow.exceptions import AirflowFailException
    from modules.connectors.connector_provider import connector_provider
    from modules.connectors.storage_connector import StorageConnector
    from modules.operators.connections import get_assetdb_temp_config
    from modules.operators.xcom import get_data_from_xcom
    from modules.operators.transfer import archive_artefact_metadata

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()
    temp_database = assetdb_temp_config["host"]
    archive_bucket = assetdb_temp_config["archive-bucket"]

    # Configure connector_provider and connect assetdb_temp_connector
    connector_provider.configure({"assetdb_temp": assetdb_temp_config})

    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

    # Create urn for assetdb-temp archive
    target_urn = StorageConnector.create_urn(temp_database, archive_bucket, final_uuid)

    # Combine source urn's
    source_artefact_urns = []

    for artefact in download_artefacts:
        print("Artefact id: " + artefact.artefact_id)
        artefact_urn = get_data_from_xcom(download_artefacts_data, [artefact.artefact_id])
        print("Artefact urn: " + artefact_urn)
        source_artefact_urns.append(artefact_urn)
        # create meta data artefact json on archive bucket
        archive_artefact_metadata(dag_id, assetdb_temp_connector, artefact, artefact_urn, target_urn, time_started)

    artefact_index = 0
    for artefact in artefacts:
        print("Artefact id: " + artefact.artefact_id)
        artefact_urn = get_data_from_xcom(artefacts_data[artefact_index], [artefact.artefact_id])
        print("Artefact urn: " + artefact_urn)
        source_artefact_urns.append(artefact_urn)
        # create meta data artefact json on archive bucket
        archive_artefact_metadata(dag_id, assetdb_temp_connector, artefact, artefact_urn, target_urn, time_started)
        artefact_index += 1

    success = assetdb_temp_connector.copy_objects(source_artefact_urns, target_urn)
    if not success:
        print("Error copying assetdb-temp objects to new archive object subfolder on assetdb-temp!")
        raise AirflowFailException()

    return json.dumps({"result": target_urn})


def op_archive_artefacts(
    dag, dag_id, task_id_suffix, download_artefacts, download_artefacts_data, artefacts, final_uuid, time_started
):
    """
    Provides PythonVirtualenvOperator to archive all artefacts from
    airflow assetdb-temp assets-temp bucket to new object on archive bucket.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param list(Artefact) download_artefacts: Download artefacts to be archived.
    :param str download_artefacts_data: XCOM Data which contains
    download urls and urns for each download Artefact.

    :param list(Artefact) artefacts: Artefacts to be archived.

    :param str final_uuid: Upload UUID of the artefact on the HAnS backend.
    :param str time_started: Start time of the DAG added into meta data.

    :return: PythonVirtualenvOperator Operator to combines files from assetdb-temp
    assets-temp bucket to new object on archive bucket
    """
    from modules.operators.xcom import gen_task_id, inject_xcom_data

    xcom_data_array = []
    for artefact in artefacts:
        xcom_data_array.append(
            inject_xcom_data(artefact.parent_dag_id, artefact.taskgroup_id, artefact.operator_id, artefact.artefact_id)
        )
    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_archive_artefacts", task_id_suffix),
        python_callable=archive_artefacts,
        op_args=[
            dag_id,
            download_artefacts,
            download_artefacts_data,
            artefacts,
            xcom_data_array,
            final_uuid,
            time_started,
        ],
        requirements=[PIP_REQUIREMENT_MINIO],
        python_version="3",
        dag=dag,
    )


def create_channel_package_upload_url(ext_output_config_json, uuid):
    """
    Provides channel package url to upload channel package

    :param str ext_output_config_json: JSON containing CONN_ID's with the keys backend and frontend.
    :param str uuid: Uuid of the channel package

    :return: str url to upload channel package.
    """
    import json
    from modules.operators.transfer import get_remote_config, create_upload_url
    from modules.operators.transfer import authenticate_on_frontend
    from modules.connectors.storage_connector import StorageConnector

    urn = StorageConnector.create_urn("assetdb", "packages", uuid, ".tar.gz")
    (conn_hans_backend, conn_hans_frontend) = get_remote_config(ext_output_config_json)
    # Authenticate on frontend and receive JWT access token
    headers_api = authenticate_on_frontend(conn_hans_frontend)
    url = create_upload_url(conn_hans_frontend, headers_api, conn_hans_backend, urn)
    return json.dumps({"result": url})


def op_create_channel_package_upload_url(dag, dag_id, task_id_suffix, ext_output_config_json, uuid):
    """
    Provides PythonVirtualenvOperator to create channel package url.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str ext_output_config_json: JSON containing CONN_ID's with the keys backend and frontend.
    :param str uuid: Channel package UUID.

    :return: PythonVirtualenvOperator Operator to transfer files from assetdb-temp to HAnS backend
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_create_channel_package_upload_url", task_id_suffix),
        python_callable=create_channel_package_upload_url,
        op_args=[ext_output_config_json, uuid],
        requirements=[PIP_REQUIREMENT_MINIO, "eval-type-backport", "requests", "urllib3"],
        python_version="3",
        dag=dag,
    )
