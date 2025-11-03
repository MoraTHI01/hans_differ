from dataclasses import dataclass
import requests
from typing import Optional, Union

from airflow.operators.python import PythonVirtualenvOperator


PIP_REQUIREMENT_MINIO = "minio"


def slides_to_images(
    download_data,
    download_data_key,
    download_data_filename,
    download_data_filename_key,
    download_meta_data,
    download_meta_urn_key,
    upload_data_slides_images,
    upload_data_key_slides_images,
    dpi=150,
):
    """
    Converting PDF slides to PNG images for usage with VLLMs.

    :param str download_data: XCOM Data which contains PDF slides urn.
    :param str download_data_key: XCOM Data key to used to determine the download slides urn.

    :param str download_data_filename: XCOM Data used to determine the PDF filename.
    :param str download_data_filename_key: XCOM Data key used to determine the PDF filename.

    :param str download_meta_data: XCOM data containing URN for the meta data.
    :param str download_meta_urn_key: XCOM Data key to used to determine the URN for the meta data.

    :param str upload_data_slides_images: XCOM Data which contains upload url for the slides image files.
    :param str upload_data_key_slides_images: XCOM Data key to used to determine the the slides image files url.

    :param int dpi Dots per inch for converting PDF to images, default: 150.

    :return: DockerOperator for performing topic segmentation
    """
    import base64
    import json
    import time
    import requests
    from copy import deepcopy
    from io import BytesIO
    from pdf2image import convert_from_bytes
    from airflow.exceptions import AirflowFailException
    from modules.connectors.connector_provider import connector_provider
    from modules.operators.connections import get_assetdb_temp_config
    from modules.operators.transfer import HansType
    from modules.operators.xcom import get_data_from_xcom
    from modules.connectors.minio_connector import MinioConnectorFetchUrlMode

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()

    # Configure connector_provider and connect assetdb_temp_connector
    connector_provider.configure({"assetdb_temp": assetdb_temp_config})

    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

    # Load slides
    slides_urn = get_data_from_xcom(download_data, [download_data_key])
    slides_response = assetdb_temp_connector.get_object(slides_urn)
    # if "500 Internal Server Error" in slides_response.data.decode("utf-8"):
    #    raise AirflowFailException()

    # Get slides filename
    slides_filename = get_data_from_xcom(download_data_filename, [download_data_filename_key])
    print("Filename: " + slides_filename)

    # Load metadata File
    metadata_urn = get_data_from_xcom(download_meta_data, [download_meta_urn_key])
    meta_response = assetdb_temp_connector.get_object(metadata_urn)
    if "500 Internal Server Error" in meta_response.data.decode("utf-8"):
        raise AirflowFailException()

    meta_data = json.loads(meta_response.data)
    meta_response.close()
    meta_response.release_conn()

    # Slides upload base urn
    slides_images_base_urn = get_data_from_xcom(upload_data_slides_images, [upload_data_key_slides_images])
    # uuid = slides_images_base_urn.rsplit(":")[-1]

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
    entry_meta_data["filename"] = slides_filename

    # Convert to images
    images = convert_from_bytes(
        slides_response.data, dpi=dpi, thread_count=8
    )  # Set dpi to desired resolution, e.g., 300
    stored_jsons = []
    stored_pngs = []
    for i, image in enumerate(images):
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        slide_image_entry = deepcopy(entry_meta_data)
        slide_image_entry["lecture_id"] = "<undefined>"  # will be added when inserting entry in vector index
        slide_image_entry["chunk_id"] = "<undefined>"  # will be added when inserting entry in vector index
        slide_image_entry["chunk_start"] = -1.0  # will be added by vts alignment
        slide_image_entry["chunk_end"] = -1.0  # will be added by vts alignment
        slide_image_entry["chunk_index"] = i
        slide_image_entry["page_number"] = i + 1
        slide_image_entry["data"] = f"data:image/png;base64,{img_str}"

        data = json.dumps(slide_image_entry).encode("utf-8")
        stream_bytes = BytesIO(data)
        slides_json_urn = slides_images_base_urn + f"/{i + 1}.json"
        (success, object_name_json) = assetdb_temp_connector.put_object(
            slides_json_urn,
            stream_bytes,
            HansType.get_mime_type(HansType.SEARCH_SLIDE_DATA_VECTOR),
            {"Content-Type": HansType.get_mime_type(HansType.SEARCH_SLIDE_DATA_VECTOR)},
        )
        if not success:
            print(f"Error storing image {i + 1}.json")
            raise AirflowFailException()
        stored_jsons.append(slides_json_urn)

        buffered_img = BytesIO()
        image.save(buffered_img, format="PNG")
        img_file_name = f"/{i + 1}.png"
        slides_png_urn = slides_images_base_urn + img_file_name
        buffered_img.seek(0)
        presigned_url = assetdb_temp_connector.gen_presigned_url(slides_png_urn, MinioConnectorFetchUrlMode.UPLOAD)
        headers = {"Content-Type": HansType.get_mime_type(HansType.SLIDE_IMAGE_DATA)}
        response = requests.put(presigned_url, data=buffered_img, headers=headers)
        # Check the response status
        if response.status_code == 200:
            print("Image uploaded successfully!")
        else:
            print(f"Failed to upload image {img_file_name}. Status code: {response.status_code}")
            print(response.text)
            raise AirflowFailException()
        stored_pngs.append(slides_png_urn)

    return json.dumps({"result": {"vectors": stored_jsons, "images": stored_pngs}})


def op_slides_to_images(
    dag,
    dag_id,
    task_id_suffix,
    download_data,
    download_data_key,
    download_data_filename,
    download_data_filename_key,
    download_meta_data,
    download_meta_urn_key,
    upload_data_slides_images,
    upload_data_key_slides_images,
    dpi=150,
) -> PythonVirtualenvOperator:
    """
    Provides PythonVirtualenvOperator for converting PDF slides to PNG images.

    :param str dag: The Airflow DAG where the operator is executed.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id

    :param str download_data: XCOM Data which contains PDF slides urn.
    :param str download_data_key: XCOM Data key to used to determine the download slides urn.

    :param str download_data_filename: XCOM Data used to determine the PDF filename.
    :param str download_data_filename_key: XCOM Data key used to determine the PDF filename.

    :param str download_meta_data: XCOM data containing URN for the meta data.
    :param str download_meta_urn_key: XCOM Data key to used to determine the URN for the meta data.

    :param str upload_data_slides_images: XCOM Data which contains upload url for the slides image files.
    :param str upload_data_key_slides_images: XCOM Data key to used to determine the the slides image files url.

    :param int dpi Dots per inch for converting PDF to images, default: 150.

    :return: DockerOperator for performing topic segmentation
    """
    from modules.operators.xcom import gen_task_id

    # # configure number of cpus/threads, large-v2 model needs ~10GB (V)RAM
    # config = dict() if config is None else config
    # # num_cpus = config.get("num_cpus", 4)

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_slides_to_images", task_id_suffix),
        python_callable=slides_to_images,
        op_args=[
            download_data,
            download_data_key,
            download_data_filename,
            download_data_filename_key,
            download_meta_data,
            download_meta_urn_key,
            upload_data_slides_images,
            upload_data_key_slides_images,
            dpi,
        ],
        requirements=[PIP_REQUIREMENT_MINIO, "eval-type-backport", "pdf2image"],
        python_version="3",
        dag=dag,
    )
