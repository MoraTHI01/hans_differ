#!/usr/bin/env python
"""
Airflow task groups for media conversion.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import pendulum

from airflow import DAG
from airflow.exceptions import AirflowFailException
from airflow.utils.task_group import TaskGroup
from airflow.operators.empty import EmptyOperator


def media_converter_audio(parent_dag, dag_group_name_download_media_files, container_id):
    """
    Generate a media_converter_audio TaskGroup to be used in a DAG.

    :param DAG parent_dag: Parent DAG instance
    :param str dag_group_name_download_media_files: Task group name for download_media_files task group
    :param str container_id: Container Id for DockerOperator

    :return: TaskGroup to use in a DAG
    :rtype: airflow.utils.task_group.TaskGroup
    """
    with TaskGroup("media_converter_audio") as group1:
        # XCOM injection helper
        from modules.operators.xcom import inject_xcom_data

        # Create urn with new uuid for audio_raw on assetdb-temp
        from modules.operators.storage import op_create_new_urn_on_assetdbtemp

        t0 = op_create_new_urn_on_assetdbtemp(parent_dag, parent_dag.dag_id, "audio_raw_urn", "audio_raw_urn", ".wav")

        # Create url "audio_raw" using previous urn "audio_raw_urn" on assetdb-temp for upload
        from modules.operators.storage import op_create_url_by_xcom

        t1 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "audio_raw_url_upload",
            "audio_raw_url_upload",
            inject_xcom_data(
                parent_dag.dag_id, "media_converter_audio", "op_create_new_urn_on_assetdbtemp", "audio_raw_urn"
            ),
            "audio_raw_urn",
            "upload",
        )

        from modules.operators.docker_media import op_docker_media_converter_audio

        t2 = op_docker_media_converter_audio(
            parent_dag.dag_id,
            "convert_media_to_audio",
            container_id,
            inject_xcom_data(
                parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
            ),
            "video_url,podcast_url",
            "video_filename,podcast_filename",
            inject_xcom_data(
                parent_dag.dag_id, "media_converter_audio", "op_create_url_by_xcom", "audio_raw_url_upload"
            ),
            "audio_raw_url_upload",
        )
        t2.doc_md = """\
          #Media Converter Audio
          Convert video file to wav and save it in assetdb-temp.
          """

        # Create url "audio_raw" using previous urn "audio_raw_urn" on assetdb-temp for download
        from modules.operators.storage import op_create_url_by_xcom

        t3 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "audio_raw_url",
            "audio_raw_url",
            inject_xcom_data(
                parent_dag.dag_id, "media_converter_audio", "op_create_new_urn_on_assetdbtemp", "audio_raw_urn"
            ),
            "audio_raw_urn",
            "download",
        )

        t0 >> t1 >> t2 >> t3
    return group1


def media_converter_video(
    parent_dag, dag_group_name_download_media_files, container_id, do_video_encoding=True, config={}
):
    """
    Generate a media_converter_video TaskGroup to be used in a DAG.

    :param DAG parent_dag: Parent DAG instance
    :param str dag_group_name_download_media_files: Task group name for download_media_files task group
    :param str container_id: Container Id for DockerOperator

    :param bool do_video_encoding: Enable dash video stream encoding, default: True
    :param str config: Configuration for dash video stream encoding with keys: num_cpus, ram_limit_docker, use_gpu,
                       resolution 'full-hd' or 'hd', default: 'hd'.

    :return: TaskGroup to use in a DAG
    :rtype: airflow.utils.task_group.TaskGroup
    """
    resolution = "hd"
    if "resolution" in config:
        resolution = config["resolution"].lower()
    with TaskGroup("media_converter_video") as group2:
        # XCOM injection helper
        from modules.operators.xcom import inject_xcom_data

        if do_video_encoding is True:
            # Create urn with new uuid for audio_raw on assetdb-temp
            from modules.operators.storage import op_create_new_urn_on_assetdbtemp

            t0 = op_create_new_urn_on_assetdbtemp(parent_dag, parent_dag.dag_id, "video_dash_urn", "video_dash_urn")

            # Convert video to mpeg-dash streaming format
            from modules.operators.docker_media import op_docker_media_converter_video

            t1 = op_docker_media_converter_video(
                parent_dag.dag_id,
                "convert_media_for_streaming",
                container_id,
                inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
                ),
                "video_url",
                # Inject data of t0
                inject_xcom_data(
                    parent_dag.dag_id, "media_converter_video", "op_create_new_urn_on_assetdbtemp", "video_dash_urn"
                ),
                # Use hans_type of t0 to get xcom data
                "video_dash_urn",
                # Configuration of e.g. resolution 'hd' or 'full-hd'
                config=config,
            )
            t1.doc_md = """\
              #Media Converter Video
              Convert video file to MPEG-DASH chunk files and mpd file and save it in assetdb-temp.
              """

            # Create url "video_dash_url" using previous urn "video_thumb_urn" on assetdb-temp for download
            from modules.operators.storage import op_create_url_by_xcom

            t2 = op_create_url_by_xcom(
                parent_dag,
                parent_dag.dag_id,
                "video_dash_url",
                "video_dash_url",
                inject_xcom_data(
                    parent_dag.dag_id, "media_converter_video", "op_create_new_urn_on_assetdbtemp", "video_dash_urn"
                ),
                "video_dash_urn",
                "download",
            )

            [
                t0 >> t1 >> t2,
                _create_thumbnail(parent_dag, dag_group_name_download_media_files, container_id, resolution),
            ]
        else:
            _create_thumbnail(parent_dag, dag_group_name_download_media_files, container_id, resolution)

    return group2


def _create_thumbnail(parent_dag, dag_group_name_download_media_files, container_id, resolution):
    """
    Generate a create_thumbnail TaskGroup to be used in a DAG.
    Creates a thumbnail of a video file.

    :param DAG parent_dag: Parent DAG instance
    :param str dag_group_name_download_media_files: Task group name for download_media_files task group
    :param str container_id: Container Id for DockerOperator
    :param str resolution: Resolution of the thumbnail, 'full-hd' or 'hd', default: 'hd'.

    :return: TaskGroup to use in a DAG
    :rtype: airflow.utils.task_group.TaskGroup
    """
    # XCOM injection helper
    from modules.operators.xcom import inject_xcom_data

    # Create urn with new uuid for video_thumb on assetdb-temp
    from modules.operators.storage import op_create_new_urn_on_assetdbtemp

    t3 = op_create_new_urn_on_assetdbtemp(parent_dag, parent_dag.dag_id, "video_thumb_urn", "video_thumb_urn")

    from modules.operators.docker_media import op_docker_media_thumbnail_image

    t4 = op_docker_media_thumbnail_image(
        parent_dag.dag_id,
        "create_thumbnail_of_video",
        container_id,
        inject_xcom_data(
            parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
        ),
        "video_url",
        "video_filename",
        inject_xcom_data(
            parent_dag.dag_id, "media_converter_video", "op_create_new_urn_on_assetdbtemp", "video_thumb_urn"
        ),
        "video_thumb_urn",
        resolution,
    )
    t4.doc_md = """\
      #Media Thumbnail Images
      Creates a thumbnail image of a video file and thumbnail images every 10 seconds and saves them in assetdb-temp.
      """

    # Create url "video_thumb_url" using previous urn "video_thumb_urn" on assetdb-temp for download
    from modules.operators.storage import op_create_url_by_xcom

    t5 = op_create_url_by_xcom(
        parent_dag,
        parent_dag.dag_id,
        "video_thumb_url",
        "video_thumb_url",
        inject_xcom_data(
            parent_dag.dag_id, "media_converter_video", "op_create_new_urn_on_assetdbtemp", "video_thumb_urn"
        ),
        "video_thumb_urn",
        "download",
    )

    t3 >> t4 >> t5
