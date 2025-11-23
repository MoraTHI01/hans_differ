#!/usr/bin/env python
"""
Vision LLM remote operators.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2024, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


from os import access
from urllib.request import urlopen
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator
import requests
import json


def create_vllm_messages(
    prompt_base, mode: str, context_data: str, meta_data: dict, img_input=None, fallback=False
) -> list[dict[str, str]]:
    from llm.helpers import gen_messages

    title = meta_data["title"]
    course = meta_data["description"]["course"]
    lang = "en"
    context_sentence = prompt_base.get_context_sentence(context_data, lang=lang)
    system_prompt = prompt_base.get_short_system_prompt(lang=lang)
    user_prompt = ""
    if mode == "ocr":
        if fallback is True:
            user_prompt = prompt_base.get_embedding_image_prompt_markdown()
        else:
            user_prompt = prompt_base.get_frame_extraction_prompt()
        print(f"User prompt: {user_prompt}", flush=True)
    else:
        raise AirflowFailException(f"Error: llm mode '{mode}' not supported!")
    return gen_messages(
        system_prompt=system_prompt, user_prompt=user_prompt, context_sentence=context_sentence, img_input=img_input
    )


def prompt_vllm_remote(
    mode,
    images_data,
    images_data_key,
    download_meta_data,
    download_meta_urn_key,
    upload_vllm_result_data,
    upload_vllm_result_urn_key,
    llm_configs={},
):
    """
    Creates a remote request to a VLLM using a specific mode.

    :param str mode: 'ocr'

    :param str images_data: XCOM data containing URN for the images data.
    :param str images_data_key: XCOM Data key to used to determine the URN for the images data.

    :param str download_meta_data: XCOM data containing URN for the meta data.
    :param str download_meta_urn_key: XCOM Data key to used to determine the URN for the meta data.

    :param str upload_vllm_result_data: XCOM data containing URN for the upload of the llm result to assetdb-temp
    :param str upload_vllm_result_urn_key: XCOM Data key to used to determine the URN for the upload of the llm result.

    :param dict llm_configs: Configurations for all llm models
    """
    import json
    import time
    import requests
    from collections import Counter
    from copy import deepcopy
    from io import BytesIO
    from airflow.exceptions import AirflowFailException
    from connectors.connector_provider import connector_provider
    from modules.operators.connections import get_assetdb_temp_config, get_connection_config
    from modules.operators.transfer import HansType
    from modules.operators.xcom import get_data_from_xcom
    from modules.operators.vllm_remote import create_vllm_messages
    from llm.prompt_base import PromptBase
    from llm.helpers import markdown_to_plain_text, detect_language
    from llm.helpers import cleanup_markdown, cleanup_text, find_words_not_urls
    from llm.helpers import find_all_urls, is_url_valid, classify_url

    # llm model and engine configuration
    prompt_base = PromptBase()

    # Get vllm remote config
    vllm_remote_config = get_connection_config("vllm_remote")
    vllm_remote_config["vllm_task"] = llm_configs["vllm_task"]
    vllm_remote_config["vllm_model_id"] = llm_configs["vllm_model_id"]

    # Get embeddings remote config
    embedding_remote_config = get_connection_config("embeddings_remote")
    embedding_remote_config["embedding_task"] = llm_configs["embedding_task"]
    embedding_remote_config["embedding_model_id"] = llm_configs["embedding_model_id"]

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()

    # Configure connector_provider
    connector_provider.configure(
        {
            "assetdb_temp": assetdb_temp_config,
            "vllm_remote_config": vllm_remote_config,
            "embedding_remote_config": embedding_remote_config,
        }
    )
    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

    # Connect to vllm
    vllm_connector = connector_provider.get_vllm_connector()
    vllm_connector.connect()

    # Connect to embeddings
    embedding_connector = connector_provider.get_embedding_connector()
    embedding_connector.connect()

    # Load metadata File
    metadata_urn = get_data_from_xcom(download_meta_data, [download_meta_urn_key])
    meta_response = assetdb_temp_connector.get_object(metadata_urn)
    if "500 Internal Server Error" in meta_response.data.decode("utf-8"):
        raise AirflowFailException()

    meta_data = json.loads(meta_response.data)
    meta_response.close()
    meta_response.release_conn()

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

    model = llm_configs["vllm_model_id"]  # "mistralai/Pixtral-12B-2409"
    print(f"Model: {model}")

    if mode == "ocr":
        # Load prepared image vector json files
        image_base_urn = get_data_from_xcom(images_data, [images_data_key])
        images_slides_data_files = assetdb_temp_connector.list_objects(image_base_urn)
        sorted_slides_data_files = []
        for obj in images_slides_data_files:
            filepath = str(obj.object_name)
            name_with_fext = filepath.split("/", maxsplit=1)[-1]
            if name_with_fext.endswith(".json") and not name_with_fext.endswith(".meta.json"):
                sorted_slides_data_files.append(name_with_fext)
        sorted_slides_data_files = sorted(sorted_slides_data_files, key=lambda x: int(x.split(".")[0]))
        stored_jsons = []
        stored_meta_jsons = []
        all_valid_urls = []
        all_words = []
        full_text = ""
        last_slide_filename = ""
        last_slide_page = 0
        prev_language = meta_data["language"]
        for name_with_fext in sorted_slides_data_files:
            download_urn = image_base_urn + "/" + name_with_fext
            img_vector_data = assetdb_temp_connector.get_object(download_urn)
            if "500 Internal Server Error" in img_vector_data.data.decode("utf-8"):
                raise AirflowFailException()
            img_vector_json = json.loads(img_vector_data.data)
            slide_filename = img_vector_json["filename"]
            last_slide_filename = slide_filename
            slide_page_number = img_vector_json["page_number"]
            last_slide_page = slide_page_number
            print(f"File: {slide_filename}, Page: {slide_page_number}", flush=True)
            messages = create_vllm_messages(
                prompt_base, mode, context_data=None, meta_data=meta_data, img_input=img_vector_json["data"]
            )
            result_ex = vllm_connector.query_vllm(messages=messages)
            while result_ex is None:
                result_ex = vllm_connector.query_vllm(messages=messages)
            markdown_text = cleanup_markdown(result_ex.strip())
            clean_text = cleanup_text(markdown_to_plain_text(markdown_text))
            print(f"Text: {clean_text}", flush=True)
            fq_words = find_words_not_urls(clean_text)
            word_counts = Counter(fq_words)
            frequent_words = {word: count for word, count in word_counts.items() if count > 16}
            if len(frequent_words) > 0:
                result_ex = vllm_connector.query_vllm(messages=messages)
                while result_ex is None:
                    result_ex = vllm_connector.query_vllm(messages=messages)
                markdown_text = result_ex.strip()
                clean_text = cleanup_text(markdown_to_plain_text(markdown_text))
                print(f"Text (2nd time): {clean_text}", flush=True)
                fq_words = find_words_not_urls(clean_text)
            print(f"Words: {fq_words}", flush=True)

            # Gen embeddings
            embeddings_data_text = embedding_connector.gen_embedding_for_text(markdown_text)
            print("Text embedded", flush=True)
            img_vector_json["chunk_text"] = markdown_text
            is_multimodal = embedding_connector.is_multimodal()
            if is_multimodal is True:
                embeddings_data_image = embedding_connector.gen_embedding_for_image(img_vector_json["data"])
                print("Image embedded", flush=True)
                # This will be stored in vector db
                img_vector_json["embedding"] = embeddings_data_image
            else:
                # This will be stored in vector db
                img_vector_json["embedding"] = embeddings_data_text
            print("Detecting urls", flush=True)
            urls = find_all_urls(clean_text)
            print(f"Urls: {urls}", flush=True)
            valid_urls = [url for url in urls if is_url_valid(url)]
            print(f"Valid urls: {valid_urls}", flush=True)
            # TODO: update existing file
            stream_bytes = BytesIO(json.dumps(img_vector_json).encode("utf-8"))
            mime_type = HansType.get_mime_type(HansType.SEARCH_SLIDE_DATA_VECTOR)
            meta_minio = {"Content-Type": mime_type}
            (success, object_name) = assetdb_temp_connector.put_object(
                download_urn, stream_bytes, mime_type, meta_minio
            )
            if not success:
                print(f"Error uploading llm result for {mode} on url {download_urn} to assetdb-temp!")
                raise AirflowFailException()
            stored_jsons.append(download_urn)
            print(f"Patched file with markdown text and vector: {download_urn}", flush=True)
            # TODO: create page meta file json, 1.json to 1.meta.json
            page_meta_file_data = deepcopy(img_vector_json)
            page_meta_file_data["markdown"] = markdown_text
            page_meta_file_data["text"] = clean_text
            page_meta_file_data["words"] = fq_words
            page_meta_file_data["urls"] = valid_urls
            page_meta_file_data["embedding_text"] = embeddings_data_text
            if is_multimodal is True:
                page_meta_file_data["embedding_image"] = embeddings_data_image
            page_meta_file_data["urls_by_class"] = {}
            for url in valid_urls:
                key = classify_url(url)
                if key not in page_meta_file_data["urls_by_class"]:
                    page_meta_file_data["urls_by_class"][key] = []
                if url not in page_meta_file_data["urls_by_class"][key]:
                    page_meta_file_data["urls_by_class"][key].append(url)
            if len(clean_text.strip()) > 0:
                page_meta_file_data["language"] = detect_language(clean_text)
                prev_language = page_meta_file_data["language"]
            else:
                page_meta_file_data["language"] = prev_language
            full_text += clean_text + " "
            all_valid_urls += [item for item in valid_urls if item not in all_valid_urls]
            all_words += [item for item in fq_words if item not in all_words]
            stream_bytes = BytesIO(json.dumps(page_meta_file_data).encode("utf-8"))
            mime_type = HansType.get_mime_type(HansType.SLIDE_IMAGE_META)
            meta_minio = {"Content-Type": mime_type}
            upload_meta_urn = download_urn.replace(".json", ".meta.json")
            (success, object_name) = assetdb_temp_connector.put_object(
                upload_meta_urn, stream_bytes, mime_type, meta_minio
            )
            if not success:
                print(f"Error uploading llm result for {mode} on url {upload_meta_urn} to assetdb-temp!")
                raise AirflowFailException()
            stored_meta_jsons.append(upload_meta_urn)
            print(f"Added meta file with markdown, clean text, words, and urls: {upload_meta_urn}", flush=True)
            print("Done\n", flush=True)
        upload_meta_slides = image_base_urn + "/slides.meta.json"
        page_meta_file_data = deepcopy(entry_meta_data)
        page_meta_file_data["filename"] = last_slide_filename
        page_meta_file_data["page"] = {"start": 1, "end": last_slide_page}
        page_meta_file_data["urls"] = all_valid_urls
        page_meta_file_data["urls_by_class"] = {}
        for url in all_valid_urls:
            key = classify_url(url)
            if key not in page_meta_file_data["urls_by_class"]:
                page_meta_file_data["urls_by_class"][key] = []
            if url not in page_meta_file_data["urls_by_class"][key]:
                page_meta_file_data["urls_by_class"][key].append(url)
        page_meta_file_data["words"] = all_words
        if len(full_text.strip()) > 0:
            page_meta_file_data["language"] = detect_language(full_text)
        else:
            page_meta_file_data["language"] = prev_language
        page_meta_file_data["text"] = full_text.strip()
        stream_bytes = BytesIO(json.dumps(page_meta_file_data).encode("utf-8"))
        mime_type = HansType.get_mime_type(HansType.SLIDES_IMAGES_META)
        meta_minio = {"Content-Type": mime_type}
        (success, object_name) = assetdb_temp_connector.put_object(
            upload_meta_slides, stream_bytes, mime_type, meta_minio
        )
        if not success:
            print(f"Error uploading llm result for {mode} on url {upload_meta_slides} to assetdb-temp!")
            raise AirflowFailException()
        stored_meta_jsons.append(upload_meta_slides)

    return json.dumps({"result": {"vectors": stored_jsons, "meta": stored_meta_jsons}})


def op_vllm_remote_prompt(
    dag,
    dag_id,
    task_id_suffix,
    mode,
    images_data,
    images_data_key,
    download_meta_data,
    download_meta_urn_key,
    upload_vllm_result_data,
    upload_vllm_result_urn_key,
    llm_configs={},
):
    """
    Provides PythonVirtualenvOperator to request a VLLM using a specific prompt template mode.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str mode: 'ocr'

    :param str images_data: XCOM data containing URN for the images data.
    :param str images_data_key: XCOM Data key to used to determine the URN for the images data.

    :param str download_meta_data: XCOM data containing URN for the meta data.
    :param str download_meta_urn_key: XCOM Data key to used to determine the URN for the meta data.

    :param str upload_vllm_result_data: XCOM data containing URN for the upload of the llm result to assetdb-temp
    :param str upload_vllm_result_urn_key: XCOM Data key to used to determine the URN for the upload of the llm result.

    :param dict llm_configs: Configurations for all llm models

    :return: PythonVirtualenvOperator Operator to create opensearch document on the assetdb-temp storage.
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_vllm_remote_prompt", task_id_suffix),
        python_callable=prompt_vllm_remote,
        op_args=[
            mode,
            images_data,
            images_data_key,
            download_meta_data,
            download_meta_urn_key,
            upload_vllm_result_data,
            upload_vllm_result_urn_key,
            llm_configs,
        ],
        requirements=["/opt/hans-modules/dist/hans_shared_modules-0.1-py3-none-any.whl", "eval-type-backport"],
        # pip_install_options=["--force-reinstall"],
        python_version="3",
        dag=dag,
    )
