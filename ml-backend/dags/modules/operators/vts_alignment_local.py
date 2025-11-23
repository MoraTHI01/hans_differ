#!/usr/bin/env python
"""
Video-to-Slides (vts) alignment based on https://github.com/tomrance/MaViPoLS
"""
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator
import requests
import json


def vts_alignment_local(
    download_video_data,
    download_video_data_key,
    download_video_data_filename,
    download_video_data_filename_key,
    download_slides_images_data,
    download_slides_images_data_key,
    download_asr_locale_data,
    download_asr_locale_data_key,
    download_transcript_de_data,
    download_transcript_de_data_key,
    download_transcript_en_data,
    download_transcript_en_data_key,
    download_meta_data,
    download_meta_urn_key,
    config,
):
    """
    Align video and slides.

    :param str dag: The Airflow DAG where the operator is executed.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id

    :param str download_video_data: XCOM Data which contains video urn.
    :param str download_video_data_key: XCOM Data key to used to determine the download video url.

    :param str download_video_data_filename: XCOM Data used to determine the video filename.
    :param str download_video_data_filename_key: XCOM Data key used to determine the video filename.

    :param str download_slides_images_data: XCOM Data which contains slides_images urn.
    :param str download_slides_images_data_key: XCOM Data key to used to determine the download the slides_images urn.

    :param str download_asr_locale_data: XCOM Data which contains asr_locale.
    :param str download_asr_locale_data_key: XCOM Data key to used to determine the download the asr_locale.

    :param str download_transcript_de_data: XCOM Data which contains transcript_de urn.
    :param str download_transcript_de_data_key: XCOM Data key to used to determine the download the transcript_de urn.

    :param str download_transcript_en_data: XCOM Data which contains transcript_en urn.
    :param str download_transcript_en_data_key: XCOM Data key to used to determine the download the transcript_en urn.

    :param str download_meta_data: XCOM data containing URN for the meta data.
    :param str download_meta_urn_key: XCOM Data key to used to determine the URN for the meta data.

    :param dict config: Configuration

    :return: xcom result
    """
    import cv2
    import json
    import tempfile
    import os
    import numpy as np
    import pytesseract
    import requests
    from io import BytesIO
    from PIL import Image
    from transformers import AutoImageProcessor, SwiftFormerModel
    from tqdm import tqdm
    from sentence_transformers import SentenceTransformer
    from airflow.exceptions import AirflowFailException
    from connectors.connector_provider import connector_provider
    from modules.operators.connections import get_assetdb_temp_config
    from modules.operators.transfer import HansType
    from modules.operators.xcom import get_data_from_xcom
    from modules.operators.vts_alignment_helpers import create_video_frames, calculate_dp_with_jumps, store_results
    from modules.operators.vts_alignment_helpers import (
        extract_features_from_images,
        compute_similarity_matrix,
        gradient_descent_with_adam,
    )

    print("Strting local alignment!", flush=True)

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()

    # Configure connector_provider and connect assetdb_temp_connector
    connector_provider.configure({"assetdb_temp": assetdb_temp_config})

    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

    # Load slides meta data
    slides_meta_urn_base = get_data_from_xcom(download_slides_images_data, [download_slides_images_data_key])
    slides_meta_urn = slides_meta_urn_base + "/slides.meta.json"
    slides_meta_data = assetdb_temp_connector.get_object(slides_meta_urn)
    if "500 Internal Server Error" in slides_meta_data.data.decode("utf-8"):
        raise AirflowFailException()
    slides_meta_dict = json.loads(slides_meta_data.data)
    slides_meta_data.close()
    slides_meta_data.release_conn()

    # Get asr locale to dertermine correct transcript
    asr_locale = get_data_from_xcom(download_asr_locale_data, [download_asr_locale_data_key])

    transcript_data = download_transcript_de_data
    transcript_data_key = download_transcript_de_data_key
    if asr_locale.lower() == "de":
        transcript_data = download_transcript_de_data
        transcript_data_key = download_transcript_de_data_key
    elif asr_locale.lower() == "en":
        transcript_data = download_transcript_en_data
        transcript_data_key = download_transcript_en_data_key

    transcript_urn = get_data_from_xcom(transcript_data, [transcript_data_key])
    transcript_response = assetdb_temp_connector.get_object(transcript_urn)
    if "500 Internal Server Error" in transcript_response.data.decode("utf-8"):
        raise AirflowFailException()
    transcript_dict = json.loads(transcript_response.data)
    transcript_response.close()
    transcript_response.release_conn()

    # Load metadata File
    metadata_urn = get_data_from_xcom(download_video_data, [download_meta_urn_key])
    meta_response = assetdb_temp_connector.get_object(metadata_urn)
    if "500 Internal Server Error" in meta_response.data.decode("utf-8"):
        raise AirflowFailException()

    meta_data = json.loads(meta_response.data)
    meta_response.close()
    meta_response.release_conn()

    # Configure
    autoimage_name = "MBZUAI/swiftformer-xs"
    if "autoimage_name" in config:
        autoimage_name = config["autoimage_name"]
    sentence_model_name = "sentence-transformers/distiluse-base-multilingual-cased"
    if "sentence_model_name" in config:
        sentence_model_name = config["sentence_model_name"]
    jump_penalty = 0.1
    if "jump_penalty" in config:
        jump_penalty = config["jump_penalty"]
    merge_method = "max"
    if "merge_method" in config:
        merge_method = config["merge_method"]

    print("Load models", flush=True)

    # Loads the sentence transformer model
    sentence_model = SentenceTransformer(sentence_model_name)

    # Loads the image transformer model (e.g. Swiftformer class)
    image_processor = AutoImageProcessor.from_pretrained(autoimage_name)
    image_model = SwiftFormerModel.from_pretrained(autoimage_name)

    jump_penality_str = str(jump_penalty)
    jump_penality_string = jump_penality_str.replace(".", "comma")

    print("Parse audio intervals and sentences", flush=True)

    interval_list = [0.0]
    sentences_list = ["Start"]
    for res_item in transcript_dict["result"]:
        start_seconds = res_item["interval"][0]
        end_seconds = res_item["interval"][1]
        middle = (end_seconds + start_seconds) / 2
        interval_list.append(middle)
        sentences_list.append(res_item["transcript_formatted"])

    print("Create video frames", flush=True)
    video_url = get_data_from_xcom(download_meta_data, [download_video_data_key])
    # Send a GET request to the URL
    response = requests.get(video_url)
    video_path = None
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Save the content to a file
        # Create a temporary file using NamedTemporaryFile
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            # Write the content to the temporary file
            temp_file.write(response.content)
            video_path = temp_file.name
        print("Video file downloaded successfully.", flush=True)
    else:
        print(f"Failed to download video file. Status code: {response.status_code}", flush=True)
        raise AirflowFailException()

    frames = create_video_frames(video_path, interval_list)
    os.remove(video_path)

    video_filename = get_data_from_xcom(download_video_data_filename, [download_video_data_filename_key])

    print("Load images in 720p", flush=True)
    # "page": {"start": 1, "end": 53}
    start_page = int(slides_meta_dict["page"]["start"])
    if start_page < 1:
        start_page = 1
    end_page = int(slides_meta_dict["page"]["end"])

    if start_page == 1 and end_page == 1:
        print("Only single slide in lecture: Return default alignment")
        result_dict = {"0.0": 1}
        store_results(
            assetdb_temp_connector,
            slides_meta_urn_base,
            slides_meta_urn,
            slides_meta_dict,
            start_page,
            end_page,
            result_dict,
        )
        return json.dumps({"result": result_dict})

    max_width = 720
    fin_img_width = 0
    fin_img_height = 0
    slides_text = []
    slides_images_np = []
    for i in range(start_page, end_page + 1):
        slide_file_urn = slides_meta_urn_base + f"/{str(i)}.png"
        print(f"Loading image: {slide_file_urn}")
        presigned_url = assetdb_temp_connector.gen_presigned_url(slide_file_urn)
        response = requests.get(presigned_url)
        img_path = None
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Save the content to a file
            # Create a temporary file using NamedTemporaryFile
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                # Write the content to the temporary file
                temp_file.write(response.content)
                img_path = temp_file.name
            print("Image file downloaded successfully.", flush=True)
        else:
            print(f"Failed to download image file. Status code: {response.status_code}", flush=True)
            raise AirflowFailException()
        pil_image = Image.open(img_path)
        original_width, original_height = pil_image.size
        if original_width > max_width:
            new_width = max_width
            new_height = int((max_width / original_width) * original_height)
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        np_array = np.array(pil_image)
        slides_images_np.append(np_array)
        # Track current resolution
        fin_img_width, fin_img_height = pil_image.size

        slide_json_urn = slides_meta_urn_base + f"/{str(i)}.meta.json"
        slides_json_resp = assetdb_temp_connector.get_object(slide_json_urn)
        if "500 Internal Server Error" in slides_json_resp.data.decode("utf-8"):
            raise AirflowFailException()
        slides_json = json.loads(slides_json_resp.data)
        slides_text.append(slides_json["text"])
        os.remove(img_path)
        print("Image loaded")

    print("Get audio and slides text features")
    # Vectorize sentences
    audio_features = sentence_model.encode(sentences_list, convert_to_tensor=True)
    text_features = sentence_model.encode(slides_text, convert_to_tensor=True)

    similarity_matrix_audio = compute_similarity_matrix(audio_features, text_features)

    ### optimal path regarding audio features is calculated:
    optimal_path_audio, _ = calculate_dp_with_jumps(similarity_matrix_audio, jump_penalty)

    print("Get image features")

    # Resize frames to match PDF image dimensions
    resized_frames = [
        cv2.resize(frame, (fin_img_width, fin_img_height)) for frame in tqdm(frames, desc="video frames are resized")
    ]

    # images are processed by selected image processor
    pdf_images_processed = [
        image_processor(image, return_tensors="pt") for image in tqdm(slides_images_np, desc="pdf images are processed")
    ]
    resized_frames_processed = [
        image_processor(image, return_tensors="pt") for image in tqdm(resized_frames, desc="video frames are processed")
    ]

    # calculate image features
    features_pdf = np.array(extract_features_from_images(pdf_images_processed, image_model))
    features_frames = np.array(extract_features_from_images(resized_frames_processed, image_model))

    similarity_matrix_image = compute_similarity_matrix(features_frames, features_pdf)

    ### optimal path regarding image features is calulcated:
    optimal_path_image, _ = calculate_dp_with_jumps(similarity_matrix_image, jump_penalty)

    print("Get video OCR text")

    frame_texts = [
        pytesseract.image_to_string(frame, lang="eng+ell+equ+deu")
        for frame in tqdm(frames, desc="text is extracted from video frames")
    ]
    frame_features = sentence_model.encode(frame_texts, convert_to_tensor=True)

    similarity_matrix_ocr = compute_similarity_matrix(frame_features, text_features)

    ### optimal path regarding ocr features is calculated:
    optimal_path_ocr, _ = calculate_dp_with_jumps(similarity_matrix_ocr, jump_penalty)

    result_dict_ocr = {}
    for chunk_index in optimal_path_ocr:
        result_dict_ocr[interval_list[chunk_index[0]]] = chunk_index[1] + 1

    result_dict_audio = {}
    for chunk_index in optimal_path_audio:
        result_dict_audio[interval_list[chunk_index[0]]] = chunk_index[1] + 1

    result_dict_image = {}
    for chunk_index in optimal_path_image:
        result_dict_image[interval_list[chunk_index[0]]] = chunk_index[1] + 1

    print("Calculate result")
    if merge_method == "mean":
        similarity_matrix_merged = np.mean(
            (similarity_matrix_ocr, similarity_matrix_audio, similarity_matrix_image), axis=0
        )
        optimal_path, _ = calculate_dp_with_jumps(similarity_matrix_merged, jump_penalty)

        result_dict = {}
        for chunk_index in optimal_path:
            result_dict[interval_list[chunk_index[0]]] = chunk_index[1] + 1

    elif merge_method == "max":
        similarity_matrix_merged = np.max(
            (similarity_matrix_ocr, similarity_matrix_audio, similarity_matrix_image), axis=0
        )

        optimal_path, _ = calculate_dp_with_jumps(similarity_matrix_merged, jump_penalty)

        result_dict = {}
        for chunk_index in optimal_path:
            result_dict[interval_list[chunk_index[0]]] = chunk_index[1] + 1

    elif merge_method == "all":
        similarity_matrix_merged = np.mean(
            (similarity_matrix_ocr, similarity_matrix_audio, similarity_matrix_image), axis=0
        )
        optimal_path, _ = calculate_dp_with_jumps(similarity_matrix_merged, jump_penalty)

        result_dict = {}
        for chunk_index in optimal_path:
            result_dict[interval_list[chunk_index[0]]] = chunk_index[1] + 1

        similarity_matrix_merged = np.max(
            (similarity_matrix_ocr, similarity_matrix_audio, similarity_matrix_image), axis=0
        )
        optimal_path, _ = calculate_dp_with_jumps(similarity_matrix_merged, jump_penalty)

        result_dict = {}
        for chunk_index in optimal_path:
            result_dict[interval_list[chunk_index[0]]] = chunk_index[1] + 1

        ## weighted sum through gradient descent:
        matrices = [similarity_matrix_ocr, similarity_matrix_audio, similarity_matrix_image]

        optimal_weights = gradient_descent_with_adam(matrices, jump_penalty)
        print("Optimal Weights:", optimal_weights)

        similarity_matrix_merged = (
            optimal_weights[0] * similarity_matrix_ocr
            + optimal_weights[1] * similarity_matrix_audio
            + optimal_weights[2] * similarity_matrix_image
        )
        optimal_path, _ = calculate_dp_with_jumps(similarity_matrix_merged, jump_penalty)

        result_dict = {}
        for chunk_index in optimal_path:
            result_dict[interval_list[chunk_index[0]]] = chunk_index[1] + 1

    ## weighted sum through gradient descent:
    elif merge_method == "weighted_sum":
        matrices = [similarity_matrix_ocr, similarity_matrix_audio, similarity_matrix_image]

        optimal_weights = gradient_descent_with_adam(matrices, jump_penalty, num_iterations=50)
        print("Optimal Weights:", optimal_weights)

        similarity_matrix_merged = (
            optimal_weights[0] * similarity_matrix_ocr
            + optimal_weights[1] * similarity_matrix_audio
            + optimal_weights[2] * similarity_matrix_image
        )
        optimal_path, _ = calculate_dp_with_jumps(similarity_matrix_merged, jump_penalty)

        result_dict = {}
        for chunk_index in optimal_path:
            result_dict[interval_list[chunk_index[0]]] = chunk_index[1] + 1

    store_results(
        assetdb_temp_connector,
        slides_meta_urn_base,
        slides_meta_urn,
        slides_meta_dict,
        start_page,
        end_page,
        result_dict,
    )
    return json.dumps({"result": result_dict})


def op_vts_alignment_local(
    dag,
    dag_id,
    task_id_suffix,
    download_video_data,
    download_video_data_key,
    download_video_data_filename,
    download_video_data_filename_key,
    download_slides_images_data,
    download_slides_images_data_key,
    download_asr_locale_data,
    download_asr_locale_data_key,
    download_transcript_de_data,
    download_transcript_de_data_key,
    download_transcript_en_data,
    download_transcript_en_data_key,
    download_meta_data,
    download_meta_urn_key,
    config,
) -> PythonVirtualenvOperator:
    """
    Provides PythonVirtualenvOperator for aligning video and slides.
    Patches the slides.meta.json artefact from download_slides_images_data

    :param str dag: The Airflow DAG where the operator is executed.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id

    :param str download_video_data: XCOM Data which contains video urn.
    :param str download_video_data_key: XCOM Data key to used to determine the download video url.

    :param str download_video_data_filename: XCOM Data used to determine the video filename.
    :param str download_video_data_filename_key: XCOM Data key used to determine the video filename.

    :param str download_slides_images_data: XCOM Data which contains slides_images urn.
    :param str download_slides_images_data_key: XCOM Data key to used to determine the download the slides_images urn.

    :param str download_asr_locale_data: XCOM Data which contains asr_locale.
    :param str download_asr_locale_data_key: XCOM Data key to used to determine the download the asr_locale.

    :param str download_transcript_de_data: XCOM Data which contains transcript_de urn.
    :param str download_transcript_de_data_key: XCOM Data key to used to determine the download the transcript_de urn.

    :param str download_transcript_en_data: XCOM Data which contains transcript_en urn.
    :param str download_transcript_en_data_key: XCOM Data key to used to determine the download the transcript_en urn.

    :param str download_meta_data: XCOM data containing URN for the meta data.
    :param str download_meta_urn_key: XCOM Data key to used to determine the URN for the meta data.

    :param dict config: Configuration for algorithm

    :return: DockerOperator for performing topic segmentation
    """
    from modules.operators.xcom import gen_task_id

    # # configure number of cpus/threads, large-v2 model needs ~10GB (V)RAM
    # config = dict() if config is None else config
    # # num_cpus = config.get("num_cpus", 4)

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_vts_alignment_local", task_id_suffix),
        python_callable=vts_alignment_local,
        op_args=[
            download_video_data,
            download_video_data_key,
            download_video_data_filename,
            download_video_data_filename_key,
            download_slides_images_data,
            download_slides_images_data_key,
            download_asr_locale_data,
            download_asr_locale_data_key,
            download_transcript_de_data,
            download_transcript_de_data_key,
            download_transcript_en_data,
            download_transcript_en_data_key,
            download_meta_data,
            download_meta_urn_key,
            config,
        ],
        requirements=[
            "/opt/hans-modules/dist/hans_shared_modules-0.1-py3-none-any.whl",
            "eval-type-backport",
            "numpy",
            "transformers",
            "sentence-transformers",
            "tqdm",
            "opencv-python",
            "pillow",
            "pytesseract",
            "torch",
            "scipy",
        ],
        # pip_install_options=["--force-reinstall"],
        python_version="3",
        dag=dag,
    )
