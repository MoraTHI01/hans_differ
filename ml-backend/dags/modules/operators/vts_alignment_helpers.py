#!/usr/bin/env python
"""
Video-to-Slides (vts) alignment helpers based on on https://github.com/tomrance/MaViPoLS
"""
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator
import requests
import json


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
    from modules.operators.vts_alignment_helpers import combine_similarity_matrices, calculate_dp_with_jumps

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
    from modules.operators.vts_alignment_helpers import objective_function

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


def frames_to_base64_png(frames):
    """
    Convert a list of OpenCV frames to a list of Base64‐encoded PNG strings.

    Args:
        frames (List[np.ndarray]): List of image arrays (BGR).

    Returns:
        List[str]: List of 'data:image/png;base64,...' strings.
    """
    import base64
    import cv2

    b64_images = []
    for frame in frames:
        # Encode the frame in PNG format
        success, buffer = cv2.imencode(".png", frame)
        if not success:
            raise RuntimeError("Failed to encode frame to PNG")
        # Convert the buffer to a Base64 string
        b64_str = base64.b64encode(buffer).decode("utf-8")
        # Prepend the data URL prefix (optional, but useful for HTML/JS)
        b64_images.append(f"data:image/png;base64,{b64_str}")
    return b64_images


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
    from modules.operators.vts_alignment_helpers import get_first_key_by_value

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
