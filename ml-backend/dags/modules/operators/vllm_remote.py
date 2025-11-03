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

# Specify minio version to be used in all PythonVirtualenvOperator
PIP_REQUIREMENT_MINIO = "minio"


def markdown_to_plain_text(markdown_text):
    """
    Convert markdown to plain text
    """
    from markdown import markdown
    from bs4 import BeautifulSoup

    # Convert Markdown to HTML
    html = markdown(markdown_text)
    # Use BeautifulSoup to parse HTML and extract text
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()


def remove_urls(text):
    """
    Remove urls from a text
    """
    import re

    # Remove URLs that start with http or https
    return re.sub(r"http[s]?://\S+", "", text)


def find_frequent_words(text):
    """
    Find frequent words in text
    """
    import re

    # Remove punctuation and split into words
    cleaned_text = remove_urls(text)
    return re.findall(r"\b(?!http|https)\w+\b", cleaned_text)


def find_all_urls(text):
    """
    Find urls in text
    """
    import re

    # Find all URLs using re.findall
    fin_text = text.replace("http:", " http:").replace("https:", " https:")
    urls = re.findall(r"(https?://[^\s]+)", fin_text)
    return urls


def is_url_valid(url):
    """
    Function to check if a URL is valid
    """
    import requests

    try:
        response = requests.get(url, timeout=5)
        # Check if the status code is in the 2xx range (success)
        return 200 <= response.status_code < 300
    except requests.RequestException:
        # If there is any exception, treat the URL as invalid
        return False


def extract_tld(url):
    """
    Parse top level domain from url
    """
    from urllib.parse import urlparse

    domain = urlparse(url).netloc
    domain_parts = domain.split(".")

    if len(domain_parts) >= 2:
        return ".".join(domain_parts[-2:])
    return domain


def classify_url(url):
    """
    Function to classify URL based on domain

    :return str Url class string: 'videos', 'science', 'news', 'wiki',
    'pictures', 'social' or 'other'
    """
    from modules.operators.vllm_remote import extract_tld

    domain = extract_tld(url)
    video_sites = [
        "youtube.com",
        "vimeo.com",
        "dailymotion.com",
        "twitch.tv",
        "netflix.com",
        "hulu.com",
        "primevideo.com",
        "disneyplus.com",
        "hbomax.com",
        "peacocktv.com",
        "crunchyroll.com",
        "funimation.com",
        "veoh.com",
        "bilibili.com",
        "metacafe.com",
        "odyssey.com",
        "rumble.com",
        "vudu.com",
        "tiktok.com",
        "viki.com",
        "ard.de",
        "zdf.de",
        "3sat.de",
        "ardmediathek.de",
        "arte.tv",
    ]
    science_sites = [
        "springer.com",
        "nature.com",
        "sciencedirect.com",
        "wiley.com",
        "nih.gov",
        "plos.org",
        "ieee.org",
        "jstor.org",
        "arxiv.org",
        "researchgate.net",
        "mdpi.com",
        "biorxiv.org",
        "sci-hub.se",
        "doaj.org",
        "frontiersin.org",
        "hindawi.com",
        "oup.com",
        "cambridge.org",
        "tandfonline.com",
        "acs.org",
    ]
    news_sites = [
        "cnn.com",
        "bbc.co.uk",
        "nytimes.com",
        "theguardian.com",
        "reuters.com",
        "washingtonpost.com",
        "forbes.com",
        "foxnews.com",
        "huffpost.com",
        "latimes.com",
        "aljazeera.com",
        "ft.com",
        "bloomberg.com",
        "euronews.com",
        "independent.co.uk",
        "sky.com",
        "thetimes.co.uk",
        "deutsche-welle.com",
        "theverge.com",
        "vox.com",
        "spiegel.de",
        "faz.net",
        "welt.de",
        "taz.de",
        "bild.de",
        "zeit.de",
        "handelsblatt.com",
        "sueddeutsche.de" "tagesschau.de",
        "tagesspiegel.de",
        "br.de",
    ]
    image_sites = [
        "flickr.com",
        "imgur.com",
        "shutterstock.com",
        "unsplash.com",
        "pexels.com",
        "depositphotos.com",
        "photobucket.com",
        "500px.com",
        "adobe.com",
        "canva.com",
        "stock.adobe.com",
        "dreamstime.com",
        "istockphoto.com",
        "gettyimages.com",
        "freepik.com",
        "visualhunt.com",
        "burst.shopify.com",
        "pixabay.com",
        "nature.com",
    ]
    social_sites = [
        "instagram.com",
        "facebook.com",
        "twitter.com",
        "pinterest.com",
        "snapchat.com",
        "tiktok.com",
        "flickr.com",
        "tumblr.com",
        "vk.com",
        "reddit.com",
        "linkedin.com",
        "weibo.com",
        "foursquare.com",
        "ello.co",
        "dscout.com",
        "imgur.com",
        "500px.com",
    ]
    wiki_sites = [
        "wikihow.com",
        "wikimedia.org",
        "wikia.com",
        "infogalactic.com",
        "citizendium.org",
        "everipedia.org",
        "scholarpedia.org",
        "encarta.msn.com",
        "brittanica.com",
        "simple.wikipedia.org",
        "wikipedia.org",
        "starwiki.net",
        "memory-alpha.org",
        "fandom.com",
        "openstreetmap.org",
        "wikitravel.org",
    ]

    if domain in video_sites:
        return "videos"
    elif domain in science_sites:
        return "science"
    elif domain in news_sites:
        return "news"
    elif domain in wiki_sites:
        return "wiki"
    elif domain in image_sites:
        return "pictures"
    elif domain in social_sites:
        return "social"
    else:
        return "other"


def cleanup_text(text):
    """
    Cleanup text
    """
    if text.endswith("```"):
        text = text.replace("```markdown", "")
        text = text.rstrip("```")
    text = text.replace("\n", " ")
    text = text.replace("   ", " ")
    text = text.replace("  ", " ")
    return text.strip()


def cleanup_markdown(text):
    """
    Cleanup markdown
    """
    if text.endswith("\n```"):
        text = text.replace("```markdown\n", "")
        text = text.rstrip("\n```")
    elif text.endswith("```"):
        text = text.replace("```markdown", "")
        text = text.rstrip("```")
    return text


def gen_embeddings(tei_url, text):
    """Get text embeddings"""
    import time
    import requests

    print("Generate text embeddings")
    start_time = time.time()
    payload = {"inputs": text}
    response = requests.post(tei_url, json=payload)
    end_time = time.time()
    el_time = end_time - start_time
    print(f"Elapsed time: {el_time:.2f} seconds")
    return response.json()[0]


def do_prompt_single(client, model, prompt, img_input, max_tokens=8192):
    """
    Prompt vllm with single image
    """
    import time

    start_time = time.time()
    chat_completion_from_base64 = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": img_input}}],
            }
        ],
        model=model,
        max_tokens=max_tokens,
        n=1,
        timeout=120.0,
    )
    end_time = time.time()
    el_time = end_time - start_time
    print(f"Elapsed time: {el_time:.2f} seconds", flush=True)
    if len(chat_completion_from_base64.choices) > 0:
        return chat_completion_from_base64.choices[0].message.content
    return None


def prompt_vllm_remote(
    mode,
    images_data,
    images_data_key,
    download_meta_data,
    download_meta_urn_key,
    upload_vllm_result_data,
    upload_vllm_result_urn_key,
    use_orchestrator=False,
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

    :param bool use_orchestrator: Orchestrator between client and llm: client <-> orchestrator <-> llm , default: False, values: True, False
    """
    import json
    import time
    import requests
    from collections import Counter
    from copy import deepcopy
    from io import BytesIO
    from airflow.exceptions import AirflowFailException
    from modules.connectors.connector_provider import connector_provider
    from modules.operators.connections import get_assetdb_temp_config, get_connection_config
    from modules.operators.transfer import HansType
    from modules.operators.xcom import get_data_from_xcom
    from modules.operators.vllm_remote import do_prompt_single, gen_embeddings, markdown_to_plain_text
    from modules.operators.vllm_remote import cleanup_markdown, cleanup_text, find_frequent_words
    from modules.operators.vllm_remote import find_all_urls, is_url_valid, classify_url
    from openai import OpenAI
    from langdetect import DetectorFactory
    from langdetect import detect

    DetectorFactory.seed = 0

    # Get vllm remote config
    config = get_connection_config("vllm_remote")
    vllm_conn_type = config["conn_type"]
    vllm_schema = config["schema"]
    vllm_host = config["host"]
    vllm_port = str(config["port"])

    # Get text embedding service remote config
    tei_config = get_connection_config("text_embedding_remote")
    tei_conn_type = tei_config["conn_type"]
    tei_schema = tei_config["schema"]
    tei_host = tei_config["host"]
    tei_port = str(tei_config["port"])

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()

    # Configure connector_provider and connect assetdb_temp_connector
    connector_provider.configure({"assetdb_temp": assetdb_temp_config})
    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

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

    url_base = vllm_schema + "://" + vllm_host + ":" + vllm_port
    if use_orchestrator is True:
        url_demand = url_base + "/demand_vllm_service"
        url_info = url_base + "/info"
        # TODO: call demand and check availability with info until LLM is available
        url = url_base + "/vllm_service/v1"
    else:
        url = url_base + "/v1"

    tei_url_base = tei_schema + "://" + tei_host + ":" + tei_port
    if use_orchestrator is True:
        tei_url_demand = tei_url_base + "/demand_text_embedding_service"  # Todo: verify url defined by orchestrator
        tei_url_info = tei_url_base + "/info"
        # TODO: call demand and check availability with info until TEI service is available
        tei_url = tei_url_base + "/text_embedding_service/embed"
    else:
        tei_url = tei_url_base + "/embed"

    client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key="EMPTY",
        base_url=url,
    )
    model = "mistralai/Pixtral-12B-2409"

    if mode == "ocr":
        print(f"OCR using VLLM: {model}")
        extract_prompt = "Extract all text including all special terms, headings, footer, and captions without translation or interpretation in markdown format."
        max_tokens = 8192
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
            result_ex = do_prompt_single(client, model, extract_prompt, img_vector_json["data"], max_tokens)
            while result_ex is None:
                result_ex = do_prompt_single(client, model, extract_prompt, img_vector_json["data"], max_tokens)
            markdown_text = cleanup_markdown(result_ex.strip())
            clean_text = cleanup_text(markdown_to_plain_text(markdown_text))
            print(f"Text: {clean_text}", flush=True)
            fq_words = find_frequent_words(clean_text)
            word_counts = Counter(fq_words)
            frequent_words = {word: count for word, count in word_counts.items() if count > 16}
            if len(frequent_words) > 0:
                result_ex = do_prompt_single(client, model, extract_prompt, img_vector_json["data"], max_tokens)
                while result_ex is None:
                    result_ex = do_prompt_single(client, model, extract_prompt, img_vector_json["data"], max_tokens)
                markdown_text = result_ex.strip()
                clean_text = cleanup_text(markdown_to_plain_text(markdown_text))
                print(f"Text (2nd time): {clean_text}", flush=True)
                fq_words = find_frequent_words(clean_text)
            print(f"Words: {fq_words}", flush=True)
            # Gen embeddings
            embeddings_data_pdf = gen_embeddings(tei_url, markdown_text)
            print("Text embedded")
            urls = find_all_urls(clean_text)
            print(f"Urls: {urls}")
            valid_urls = [url for url in urls if is_url_valid(url)]
            print(f"Valid urls: {valid_urls}")
            img_vector_json["chunk_text"] = markdown_text
            img_vector_json["embedding"] = embeddings_data_pdf
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
            page_meta_file_data["urls_by_class"] = {}
            for url in valid_urls:
                key = classify_url(url)
                if key not in page_meta_file_data["urls_by_class"]:
                    page_meta_file_data["urls_by_class"][key] = []
                if url not in page_meta_file_data["urls_by_class"][key]:
                    page_meta_file_data["urls_by_class"][key].append(url)
            page_meta_file_data["language"] = detect(clean_text.strip())
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
        page_meta_file_data["language"] = detect(full_text.strip())
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
    use_orchestrator=False,
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

    :param bool use_orchestrator: Orchestrator between client and llm: client <-> orchestrator <-> llm , default: False, values: True, False

    :return: PythonVirtualenvOperator Operator to create opensearch document on the assetdb-temp storage.
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_llm_remote_prompt", task_id_suffix),
        python_callable=prompt_vllm_remote,
        op_args=[
            mode,
            images_data,
            images_data_key,
            download_meta_data,
            download_meta_urn_key,
            upload_vllm_result_data,
            upload_vllm_result_urn_key,
            use_orchestrator,
        ],
        requirements=[
            PIP_REQUIREMENT_MINIO,
            "eval-type-backport",
            "openai==1.47.0",
            "markdown",
            "beautifulsoup4",
            "langdetect",
        ],
        python_version="3",
        dag=dag,
    )
