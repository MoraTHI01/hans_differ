#!/usr/bin/env python
"""
Video-to-Slides (vts) alignment based on https://github.com/andererka/MaViLS
"""
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator
import requests
import json


PIP_REQUIREMENT_MINIO = "minio"


def calculate_dp_with_jumps(similarity_matrix, jump_penalty, linearity_penalty=0.0000001):
    """calculates the decision matrix D according to a similarity matrix and a jump penality

    Args:
        similarity_matrix (numpy matrix): matrix containing similarity scores for each pair of video frame and lecture slide
        jump_penalty (float): jump penality for punsihing large jumps back and forth within a lecture

    Returns:
        list, matrix: list of indices to follow for an optimized sequence of slide numbers, decision matrix D
    """
    import numpy as np
    from tqdm import tqdm

    rows, cols = similarity_matrix.shape
    print("rows and cols", rows, cols)
    # dp matrix is initalized with 0s
    dp = np.zeros((rows + 1, cols + 1))
    path = {}
    max_index = 0

    # go through every row and column
    for i in tqdm(range(1, rows + 1), desc="go through similarity matrix to calculate dp matrix"):  # frame chunks
        for j in range(1, cols + 1):  # number of slide pages
            # initalize max value with minus infinity:
            max_value = -np.inf
            for k in range(1, cols + 1):
                # jump penality should be scaled by size of jump between last index and current:
                if (k < j) and abs(k - j) > 0:  # penality is higher if jump is backward compared to forward
                    jump_penalty_scaled = jump_penalty * abs(k - j) * 2
                elif (k > j) and abs(k - j) > 0:
                    jump_penalty_scaled = jump_penalty * abs(k - j)
                else:
                    jump_penalty_scaled = 0
                expected_frame_index = 1 + (rows / (cols - 1)) * i
                linearity_penalty_scaled = linearity_penalty * abs(k - expected_frame_index)
                current_value = (
                    similarity_matrix[i - 1][k - 1]
                    - linearity_penalty_scaled
                    - (jump_penalty_scaled if k != j else 0)
                    + dp[i - 1][k]
                )
                if current_value > max_value:
                    max_value = current_value
                    max_index = k
            dp[i][j] = max_value
            path[(i, j)] = (i - 1, max_index)

    # trace back paths to find the one with the highest correlation:
    max_score = -np.inf
    optimal_end = 0
    for j in range(1, cols + 1):
        if dp[rows][j] > max_score:
            max_score = dp[rows][j]
            optimal_end = j

    optimal_path = []
    i, j = rows, optimal_end
    while i > 0:
        optimal_path.append((i - 1, path[(i, j)][1] - 1))
        i, j = path[(i, j)]

    return list(reversed(optimal_path)), dp


def compute_similarity_matrix(embeddings1, embeddings2):
    """Computes matrix with cosine similarity values between every embedding entry

    Args:
        embeddings1 (_embedding_): _feature embeddings, e.g. sentence transformer embedding or image vectorizer_
        embeddings2 (_embedding_): _feature embeddings, e.g. sentence transformer embedding or image vectorizer_

    Returns:
        _numpy matrix_: _similarity matrix with cosine similarity values_
    """
    import numpy as np
    from scipy.spatial.distance import cosine

    # Initialize an empty matrix with the appropriate size
    similarity_matrix = np.zeros((len(embeddings1), len(embeddings2)))

    # Iterate over each pair of embeddings and calculate cosine similarity
    for i, emb1 in enumerate(embeddings1):
        for j, emb2 in enumerate(embeddings2):
            # Cosine similarity is 1 - cosine distance
            similarity_matrix[i, j] = 1 - cosine(emb1, emb2)

    return similarity_matrix


def create_video_frames(video_path, interval_list):
    """Create video frames according to the time distances stored in interval_list

    Args:
        video_array np_array: Numpy array with video frames
        interval_list (_type_): _defines intervals of frames.
    """
    import cv2

    # Process videos and store frames
    frames = []  # Store frames
    timestamps = []  # Store timestamps of captured frames for debugging or verification
    print(f"Capture video: {video_path}")
    cap = cv2.VideoCapture(video_path)

    for interval in interval_list:
        # Set video position to the current interval time
        print(f"Current interval: {interval}")
        interval_msec = interval * 1000
        print(f"Current interval msec: {interval_msec}")
        cap.set(cv2.CAP_PROP_POS_MSEC, interval_msec)

        ret, frame = cap.read()  # Read the frame at the current interval

        if not ret:
            print(f"Failed to capture frame at {interval} seconds.")
            # in case capture fails, append frames with last frame in order to get equal length for arrays later on
            frames.append(frames[-1])
            continue

        frames.append(frame)  # Append the successfully captured frame to the frames list
        current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000  # Current time in seconds
        timestamps.append(current_time)  # Append the timestamp for debugging

        # For debugging: Save frames as images (optional)
        # cv2.imwrite('../frame_images/{}.png'.format(str(len(frames))), frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])

    cap.release()  # Release the video capture object
    print(f"Captured timestamps: {timestamps}")
    return frames


def extract_features_from_images(cv2_images, model):
    """extracts features of images according to a (transformer) model

    Args:
        cv2_images (_type_): _description_
        model (_type_): should be model that processes images like swiftformer

    Returns:
        list: list of features
    """
    import torch

    feature_list = []

    for img in cv2_images:
        # Predict and extract features
        with torch.no_grad():
            outputs = model(**img)
        last_hidden_states = outputs.last_hidden_state
        feature_list.append(last_hidden_states.view(-1).numpy().flatten())

    return feature_list


def combine_similarity_matrices(weights, matrices):
    """combine matrices according to weights as weigted sum

    Args:
        weights (list): list of floats
        matrices (list): list of matrices

    Returns:
        numpy matrix: combined matrix; weighted sum of matrices
    """
    import numpy as np

    combined_matrix = np.zeros_like(matrices[0])
    for weight, matrix in zip(weights, matrices):
        combined_matrix += weight * matrix
    return combined_matrix


def objective_function(weights, matrices, jump_penalty):
    """defines objective function for dynamic programming decision matrix

    Args:
        weights (list of floats): weights for weighted sum of matrices
        matrices (list): list of matrices
        jump_penalty (float): penality for jumps of non-consecutive slides

    Returns:
        numpy float: scoe of objective function
    """
    import numpy as np
    from modules.operators.vts_alignment import combine_similarity_matrices, calculate_dp_with_jumps

    combined_matrix = combine_similarity_matrices(weights, matrices)
    _, dp = calculate_dp_with_jumps(combined_matrix, jump_penalty)
    # Assuming the objective is to maximize the final value in the DP table
    final_score = np.max(dp[-1])
    return -final_score


def gradient_descent_with_adam(
    matrices, jump_penalty, learning_rate=0.001, num_iterations=50, beta1=0.9, beta2=0.999, epsilon=1e-8
):
    """calculate (numerical) gradient descent in order to find optimized weighted sum

    Args:
        matrices (_list): list of matrices
        jump_penalty (float): penality for jumps of non-consecutive slides
        learning_rate (float, optional): Defaults to 0.001.
        num_iterations (int, optional): number of iterations of gradient descent. Defaults to 50.
        beta1 (float, optional): constant to update first moment estimate. Defaults to 0.9.
        beta2 (float, optional): constant to update first moment estimate. Defaults to 0.999.
        epsilon (_type_, optional): Defaults to 1e-8.

    Returns:
        list: list of optimized weights
    """
    import numpy as np
    from modules.operators.vts_alignment import objective_function

    initial_weights = [1 / 3, 1 / 3, 1 / 3]
    weights = np.array(initial_weights)
    m = np.zeros_like(weights)  # First moment vector
    v = np.zeros_like(weights)  # Second moment vector
    t = 0  # Timestep

    for _ in range(num_iterations):
        grad = np.zeros_like(weights)
        for i in range(len(weights)):
            weights_plus = np.copy(weights)
            weights_minus = np.copy(weights)
            weights_plus[i] += epsilon
            weights_minus[i] -= epsilon
            grad[i] = (
                objective_function(weights_plus, matrices, jump_penalty)
                - objective_function(weights_minus, matrices, jump_penalty)
            ) / (2 * epsilon)

        t += 1  # Increment timestep
        m = beta1 * m + (1 - beta1) * grad  # Update biased first moment estimate
        v = beta2 * v + (1 - beta2) * (grad**2)  # Update biased second raw moment estimate
        m_hat = m / (1 - beta1**t)  # Compute bias-corrected first moment estimate
        v_hat = v / (1 - beta2**t)  # Compute bias-corrected second raw moment estimate

        # Update weights
        weights -= learning_rate * m_hat / (np.sqrt(v_hat) + epsilon)

        # Ensure weights are normalized and non-negative
        weights = np.maximum(weights, 0)
        weights /= np.sum(weights)

    return weights


def get_first_key_by_value(my_dict, target_value):
    """
    Get first key which matches a value from a dict
    """
    for key, value in my_dict.items():
        if value == target_value:
            return key
    return None


def store_results(
    assetdb_temp_connector, slides_meta_urn_base, slides_meta_urn, slides_meta_dict, start_page, end_page, result_dict
):
    """
    Use result dict to patch slides.meta.json
    and single slides meta data e.g. 1.meta.json and 1.json
    """
    from io import BytesIO
    from modules.operators.transfer import HansType
    from airflow.exceptions import AirflowFailException
    from modules.operators.vts_alignment import get_first_key_by_value

    print("Patch slides.meta.json", flush=True)
    # Load slides meta data
    slides_meta_dict["alignment"] = result_dict
    stream_bytes = BytesIO(json.dumps(slides_meta_dict).encode("utf-8"))
    mime_type = HansType.get_mime_type(HansType.SLIDES_IMAGES_META)
    meta_minio = {"Content-Type": mime_type}
    (success, object_name) = assetdb_temp_connector.put_object(slides_meta_urn, stream_bytes, mime_type, meta_minio)
    if not success:
        print(f"Error patching alignment result on {slides_meta_urn} to assetdb-temp!")
        raise AirflowFailException()

    print("Patch slide vector data", flush=True)
    for i in range(start_page, end_page + 1):
        interval_str = get_first_key_by_value(result_dict, i)
        if interval_str is not None:
            # the 1.json file
            slide_meta_urn = slides_meta_urn_base + f"/{str(i)}.json"
            print(f"Patching {slide_meta_urn}", flush=True)
            slide_meta_response = assetdb_temp_connector.get_object(slide_meta_urn)
            if "500 Internal Server Error" in slide_meta_response.data.decode("utf-8"):
                raise AirflowFailException()
            slide_meta_dict = json.loads(slide_meta_response.data)
            slide_meta_response.close()
            slide_meta_response.release_conn()
            slide_meta_dict["chunk_start"] = float(interval_str)
            slide_meta_dict["chunk_end"] = -1.0  # ignored not needed for slides
            stream_bytes = BytesIO(json.dumps(slide_meta_dict).encode("utf-8"))
            mime_type = HansType.get_mime_type(HansType.SEARCH_SLIDE_DATA_VECTOR)
            meta_minio = {"Content-Type": mime_type}
            (success, object_name) = assetdb_temp_connector.put_object(
                slide_meta_urn, stream_bytes, mime_type, meta_minio
            )
            if not success:
                print(f"Error patching alignment interval start on {slide_meta_urn} to assetdb-temp!")
                raise AirflowFailException()
            # the 1.meta.json file
            slide_meta_urn = slides_meta_urn_base + f"/{str(i)}.meta.json"
            print(f"Patching {slide_meta_urn}", flush=True)
            slide_meta_response = assetdb_temp_connector.get_object(slide_meta_urn)
            if "500 Internal Server Error" in slide_meta_response.data.decode("utf-8"):
                raise AirflowFailException()
            slide_meta_dict = json.loads(slide_meta_response.data)
            slide_meta_response.close()
            slide_meta_response.release_conn()
            slide_meta_dict["chunk_start"] = float(interval_str)
            slide_meta_dict["chunk_end"] = -1.0  # ignored not needed for slides
            stream_bytes = BytesIO(json.dumps(slide_meta_dict).encode("utf-8"))
            mime_type = HansType.get_mime_type(HansType.SLIDE_IMAGE_META)
            meta_minio = {"Content-Type": mime_type}
            (success, object_name) = assetdb_temp_connector.put_object(
                slide_meta_urn, stream_bytes, mime_type, meta_minio
            )
            if not success:
                print(f"Error patching alignment interval start on {slide_meta_urn} to assetdb-temp!")
                raise AirflowFailException()


def vts_alignment(
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
    from modules.connectors.connector_provider import connector_provider
    from modules.operators.connections import get_assetdb_temp_config
    from modules.operators.transfer import HansType
    from modules.operators.xcom import get_data_from_xcom
    from modules.operators.vts_alignment import create_video_frames, calculate_dp_with_jumps, store_results
    from modules.operators.vts_alignment import (
        extract_features_from_images,
        compute_similarity_matrix,
        gradient_descent_with_adam,
    )

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


def op_vts_alignment(
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

    :param dict config: Configuration

    :return: DockerOperator for performing topic segmentation
    """
    from modules.operators.xcom import gen_task_id

    # # configure number of cpus/threads, large-v2 model needs ~10GB (V)RAM
    # config = dict() if config is None else config
    # # num_cpus = config.get("num_cpus", 4)

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_vts_alignment", task_id_suffix),
        python_callable=vts_alignment,
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
            PIP_REQUIREMENT_MINIO,
            "eval-type-backport",
            "numpy==1.26.4",
            "transformers==4.38.1",
            "sentence-transformers==2.3.1",
            "tqdm==4.66.2",
            "opencv-python==4.9.0.80",
            "pillow==10.2.0",
            "pytesseract==0.3.10",
            "torch==2.2.0",
            "scipy==1.12.0",
        ],
        python_version="3",
        dag=dag,
    )
