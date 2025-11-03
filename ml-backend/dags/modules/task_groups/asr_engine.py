#!/usr/bin/env python
"""
Airflow task groups for speech recognition.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import pendulum
from enum import Enum

from airflow import DAG
from airflow.exceptions import AirflowConfigException
from airflow.utils.task_group import TaskGroup
from airflow.operators.empty import EmptyOperator


class AsrEngineOperator(Enum):
    """ASR Engine Operator
    Used to select operator for task group.
    """

    KALDI = 1
    MOD9 = 2
    NEMO = 3
    PYTORCH = 4
    SPEECHBRAIN = 5
    AMAZON = 6
    GOOGLE = 7
    MICROSOFT = 8
    NUANCE = 9
    OPENAI = 10
    WHISPER_S2T = 11
    SPECIAL = 128


def _get_engine_operator(param_engine):
    """
    Helper to get asr engine operator.

    :param str param_engine: Name of the ASR Engine Operator

    :return: AsrEngineOperator ASR Engine Operator if successful, None otherwise
    """
    try:
        result = AsrEngineOperator[param_engine.upper()]
        return result
    except:
        print("Invalid AsrEngineOperator configuration: " + param_engine)
        return None


def _prepare_asr_engine_run(parent_dag, dag_group_name_download_media_files, asr_engine_taskgroup):
    """
    Preparation tasks used for all asr engine task groups

    :param DAG parent_dag: Parent DAG instance
    :param str dag_group_name_download_media_files: Task group name for download_media_files task group
    :param str asr_engine_taskgroup: Task group name 'asr_engine_local' or 'asr_engine_remote'
    """
    # XCOM injection helper
    from modules.operators.xcom import inject_xcom_data
    from modules.operators.storage import op_create_url_by_xcom
    from modules.operators.xcom import op_get_single_data_from_xcom_json
    from modules.operators.storage import op_create_new_urn_on_assetdbtemp

    t0 = op_get_single_data_from_xcom_json(
        parent_dag,
        parent_dag.dag_id,
        "asr_locale",
        inject_xcom_data(
            parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
        ),
        ["video_locale", "podcast_locale"],
        "asr_locale",
    )
    # Create urn with new uuid for asr_result on assetdb-temp
    t1 = op_create_new_urn_on_assetdbtemp(
        parent_dag, parent_dag.dag_id, "asr_result_de_urn", "asr_result_de_urn", ".json"
    )
    t2 = op_create_new_urn_on_assetdbtemp(
        parent_dag, parent_dag.dag_id, "asr_result_en_urn", "asr_result_en_urn", ".json"
    )
    # Create urn with new uuid for transcript_urn on assetdb-temp
    t3 = op_create_new_urn_on_assetdbtemp(
        parent_dag, parent_dag.dag_id, "transcript_de_urn", "transcript_de_urn", ".json"
    )
    t4 = op_create_new_urn_on_assetdbtemp(
        parent_dag, parent_dag.dag_id, "transcript_en_urn", "transcript_en_urn", ".json"
    )
    # Create urn with new uuid for subtitle_urn on assetdb-temp
    t5 = op_create_new_urn_on_assetdbtemp(parent_dag, parent_dag.dag_id, "subtitle_de_urn", "subtitle_de_urn", ".vtt")
    t6 = op_create_new_urn_on_assetdbtemp(parent_dag, parent_dag.dag_id, "subtitle_en_urn", "subtitle_en_urn", ".vtt")
    # Create url "asr_result" using previous urn "asr_result_urn" on assetdb-temp
    t7 = op_create_url_by_xcom(
        parent_dag,
        parent_dag.dag_id,
        "asr_result_de_url_upload",
        "asr_result_de_url_upload",
        inject_xcom_data(
            parent_dag.dag_id, asr_engine_taskgroup, "op_create_new_urn_on_assetdbtemp", "asr_result_de_urn"
        ),
        "asr_result_de_urn",
        "upload",
    )
    t8 = op_create_url_by_xcom(
        parent_dag,
        parent_dag.dag_id,
        "asr_result_en_url_upload",
        "asr_result_en_url_upload",
        inject_xcom_data(
            parent_dag.dag_id, asr_engine_taskgroup, "op_create_new_urn_on_assetdbtemp", "asr_result_en_urn"
        ),
        "asr_result_en_urn",
        "upload",
    )
    # Create url "transcript" using previous urn "transcript_urn" on assetdb-temp
    t9 = op_create_url_by_xcom(
        parent_dag,
        parent_dag.dag_id,
        "transcript_de_url_upload",
        "transcript_de_url_upload",
        inject_xcom_data(
            parent_dag.dag_id, asr_engine_taskgroup, "op_create_new_urn_on_assetdbtemp", "transcript_de_urn"
        ),
        "transcript_de_urn",
        "upload",
    )
    t10 = op_create_url_by_xcom(
        parent_dag,
        parent_dag.dag_id,
        "transcript_en_url_upload",
        "transcript_en_url_upload",
        inject_xcom_data(
            parent_dag.dag_id, asr_engine_taskgroup, "op_create_new_urn_on_assetdbtemp", "transcript_en_urn"
        ),
        "transcript_en_urn",
        "upload",
    )
    # Create url "subtitle" using previous urn "subtitle_urn" on assetdb-temp
    t11 = op_create_url_by_xcom(
        parent_dag,
        parent_dag.dag_id,
        "subtitle_de_url_upload",
        "subtitle_de_url_upload",
        inject_xcom_data(
            parent_dag.dag_id, asr_engine_taskgroup, "op_create_new_urn_on_assetdbtemp", "subtitle_de_urn"
        ),
        "subtitle_de_urn",
        "upload",
    )
    t12 = op_create_url_by_xcom(
        parent_dag,
        parent_dag.dag_id,
        "subtitle_en_url_upload",
        "subtitle_en_url_upload",
        inject_xcom_data(
            parent_dag.dag_id, asr_engine_taskgroup, "op_create_new_urn_on_assetdbtemp", "subtitle_en_urn"
        ),
        "subtitle_en_urn",
        "upload",
    )

    return (t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12)


def _publish_asr_engine_run(parent_dag, asr_engine_taskgroup):
    """
    Publishing tasks used for all asr engine task groups

    :param DAG parent_dag: Parent DAG instance
    :param str asr_engine_taskgroup: Task group name 'asr_engine_local' or 'asr_engine_remote'
    """
    from modules.operators.xcom import inject_xcom_data
    from modules.operators.storage import op_create_url_by_xcom

    # Create url "asr_result_url" using previous urn "asr_result_urn" on assetdb-temp for download
    t14 = op_create_url_by_xcom(
        parent_dag,
        parent_dag.dag_id,
        "asr_result_de_url",
        "asr_result_de_url",
        inject_xcom_data(
            parent_dag.dag_id, asr_engine_taskgroup, "op_create_new_urn_on_assetdbtemp", "asr_result_de_urn"
        ),
        "asr_result_de_urn",
        "download",
    )
    t15 = op_create_url_by_xcom(
        parent_dag,
        parent_dag.dag_id,
        "asr_result_en_url",
        "asr_result_en_url",
        inject_xcom_data(
            parent_dag.dag_id, asr_engine_taskgroup, "op_create_new_urn_on_assetdbtemp", "asr_result_en_urn"
        ),
        "asr_result_en_urn",
        "download",
    )
    # Create url "transcript_url" using previous urn "transcript_urn" on assetdb-temp for download
    t16 = op_create_url_by_xcom(
        parent_dag,
        parent_dag.dag_id,
        "transcript_de_url",
        "transcript_de_url",
        inject_xcom_data(
            parent_dag.dag_id, asr_engine_taskgroup, "op_create_new_urn_on_assetdbtemp", "transcript_de_urn"
        ),
        "transcript_de_urn",
        "download",
    )
    t17 = op_create_url_by_xcom(
        parent_dag,
        parent_dag.dag_id,
        "transcript_en_url",
        "transcript_en_url",
        inject_xcom_data(
            parent_dag.dag_id, asr_engine_taskgroup, "op_create_new_urn_on_assetdbtemp", "transcript_en_urn"
        ),
        "transcript_en_urn",
        "download",
    )
    # Create url "subtitle_url" using previous urn "subtitle_urn" on assetdb-temp for download
    t18 = op_create_url_by_xcom(
        parent_dag,
        parent_dag.dag_id,
        "subtitle_de_url",
        "subtitle_de_url",
        inject_xcom_data(
            parent_dag.dag_id, asr_engine_taskgroup, "op_create_new_urn_on_assetdbtemp", "subtitle_de_urn"
        ),
        "subtitle_de_urn",
        "download",
    )
    t19 = op_create_url_by_xcom(
        parent_dag,
        parent_dag.dag_id,
        "subtitle_en_url",
        "subtitle_en_url",
        inject_xcom_data(
            parent_dag.dag_id, asr_engine_taskgroup, "op_create_new_urn_on_assetdbtemp", "subtitle_en_urn"
        ),
        "subtitle_en_urn",
        "download",
    )
    return (t14, t15, t16, t17, t18, t19)


def asr_engine_local(
    parent_dag,
    dag_group_name_download_media_files,
    dag_group_name_media_converter_audio,
    container_id,
    asr_engine,
    config={},
):
    """
    Generate a asr_engine TaskGroup to be used in a DAG.

    :param DAG parent_dag: Parent DAG instance
    :param str dag_group_name_download_media_files: Task group name for download_media_files task group
    :param str dag_group_name_media_converter_audio: Task group name for media_converter_audio task group
    :param str container_id: Container Id for DockerOperator

    :param str mode: Specify where the asr engine is located, used to select correct engine, see AsrEngineMode enum
    :param str asr_engine: Specify which asr engine should be used, see AsrEngineOperator enum
    :param str config: Configuration for used asr engine with keys e.g. num_cpus, asr_model

    :return: TaskGroup to use in a DAG
    :rtype: airflow.utils.task_group.TaskGroup
    """

    engine_operator = _get_engine_operator(asr_engine)
    if engine_operator is None:
        raise AirflowConfigException("The specified ASR engine was not found! asr_engine: " + asr_engine)

    with TaskGroup("asr_engine_local") as group2:
        # XCOM injection helper
        from modules.operators.xcom import inject_xcom_data

        (t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12) = _prepare_asr_engine_run(
            parent_dag, dag_group_name_download_media_files, "asr_engine_local"
        )

        if engine_operator == AsrEngineOperator.OPENAI:
            from modules.operators.docker_asr import op_docker_asr_engine_local_openai

            t13 = op_docker_asr_engine_local_openai(
                parent_dag.dag_id,
                "asr_result",
                container_id,
                inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_media_converter_audio, "op_create_url_by_xcom", "audio_raw_url"
                ),
                "audio_raw_url",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_local", "op_get_single_data_from_xcom_json", "asr_locale"
                ),
                "asr_locale",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_local", "op_create_url_by_xcom", "asr_result_de_url_upload"
                ),
                "asr_result_de_url_upload",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_local", "op_create_url_by_xcom", "asr_result_en_url_upload"
                ),
                "asr_result_en_url_upload",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_local", "op_create_url_by_xcom", "transcript_de_url_upload"
                ),
                "transcript_de_url_upload",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_local", "op_create_url_by_xcom", "transcript_en_url_upload"
                ),
                "transcript_en_url_upload",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_local", "op_create_url_by_xcom", "subtitle_de_url_upload"
                ),
                "subtitle_de_url_upload",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_local", "op_create_url_by_xcom", "subtitle_en_url_upload"
                ),
                "subtitle_en_url_upload",
                config,
            )
            t13.doc_md = """\
              #ASR Engine Local OpenAi Whisper
              Create asr result from raw audio wav file and save it in assetdb-temp
              """
        elif engine_operator == AsrEngineOperator.WHISPER_S2T:
            from modules.operators.docker_asr import op_docker_asr_engine_local_whisper_s2t

            t13 = op_docker_asr_engine_local_whisper_s2t(
                parent_dag.dag_id,
                "asr_result",
                container_id,
                inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_media_converter_audio, "op_create_url_by_xcom", "audio_raw_url"
                ),
                "audio_raw_url",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_local", "op_get_single_data_from_xcom_json", "asr_locale"
                ),
                "asr_locale",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_local", "op_create_url_by_xcom", "asr_result_de_url_upload"
                ),
                "asr_result_de_url_upload",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_local", "op_create_url_by_xcom", "asr_result_en_url_upload"
                ),
                "asr_result_en_url_upload",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_local", "op_create_url_by_xcom", "transcript_de_url_upload"
                ),
                "transcript_de_url_upload",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_local", "op_create_url_by_xcom", "transcript_en_url_upload"
                ),
                "transcript_en_url_upload",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_local", "op_create_url_by_xcom", "subtitle_de_url_upload"
                ),
                "subtitle_de_url_upload",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_local", "op_create_url_by_xcom", "subtitle_en_url_upload"
                ),
                "subtitle_en_url_upload",
                config,
            )
            t13.doc_md = """\
              #ASR Engine Local whisper-s2t
              Create asr result from raw audio wav file and save it in assetdb-temp
              """
        else:
            raise AirflowConfigException(
                "The specified ASR engine for asr_result is currently not supported! asr_engine: " + asr_engine
            )

        (t14, t15, t16, t17, t18, t19) = _publish_asr_engine_run(parent_dag, "asr_engine_local")

        (
            t0
            >> t1
            >> t2
            >> t3
            >> t4
            >> t5
            >> t6
            >> t7
            >> t8
            >> t9
            >> t10
            >> t11
            >> t12
            >> t13
            >> t14
            >> t15
            >> t16
            >> t17
            >> t18
            >> t19
        )

    return group2


def asr_engine_remote(
    parent_dag,
    dag_group_name_download_media_files,
    dag_group_name_media_converter_audio,
    container_id,
    asr_engine,
    config={},
):
    """
    Generate a asr_engine TaskGroup to be used in a DAG.

    :param DAG parent_dag: Parent DAG instance
    :param str dag_group_name_download_media_files: Task group name for download_media_files task group
    :param str dag_group_name_media_converter_audio: Task group name for media_converter_audio task group
    :param str container_id: Container Id for DockerOperator

    :param str mode: Specify where the asr engine is located, used to select correct engine, see AsrEngineMode enum
    :param str asr_engine: Specify which asr engine should be used, see AsrEngineOperator enum
    :param str config: Configuration for used asr engine with keys e.g. asr_model, batch_size

    :return: TaskGroup to use in a DAG
    :rtype: airflow.utils.task_group.TaskGroup
    """

    engine_operator = _get_engine_operator(asr_engine)
    if engine_operator is None:
        raise AirflowConfigException("The specified ASR engine was not found! asr_engine: " + asr_engine)

    with TaskGroup("asr_engine_remote") as group2:
        # XCOM injection helper
        from modules.operators.xcom import inject_xcom_data

        (t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12) = _prepare_asr_engine_run(
            parent_dag, dag_group_name_download_media_files, "asr_engine_remote"
        )

        # if engine_operator == AsrEngineOperator.MOD9:
        #    from modules.operators.docker_asr import op_docker_asr_engine_remote_mod9
        #    t13 = op_docker_asr_engine_remote_mod9(
        #             parent_dag.dag_id,
        #             "asr_result",
        #             container_id,
        #             inject_xcom_data(
        #                parent_dag.dag_id,
        #                dag_group_name_media_converter_audio,
        #                "op_create_url_by_xcom",
        #                "audio_raw_url"
        #             ),
        #             "audio_raw_url",
        #             inject_xcom_data(
        #                parent_dag.dag_id,
        #                "asr_engine_remote",
        #                "op_get_single_data_from_xcom_json",
        #                "asr_locale"
        #             ),
        #             "asr_locale",
        #             inject_xcom_data(
        #                parent_dag.dag_id,
        #                "asr_engine_remote",
        #                "op_create_url_by_xcom",
        #                "asr_result_de_url_upload"
        #             ),
        #             "asr_result_de_url_upload",
        #             inject_xcom_data(
        #                parent_dag.dag_id,
        #                "asr_engine_remote",
        #                "op_create_url_by_xcom",
        #                "asr_result_en_url_upload"
        #             ),
        #             "asr_result_en_url_upload",
        #             inject_xcom_data(
        #                parent_dag.dag_id,
        #                "asr_engine_remote",
        #                "op_create_url_by_xcom",
        #                "transcript_de_url_upload"
        #             ),
        #             "transcript_de_url_upload",
        #             inject_xcom_data(
        #                parent_dag.dag_id,
        #                "asr_engine_remote",
        #                "op_create_url_by_xcom",
        #                "transcript_en_url_upload"
        #             ),
        #             "transcript_en_url_upload",
        #             inject_xcom_data(
        #                parent_dag.dag_id,
        #                "asr_engine_remote",
        #                "op_create_url_by_xcom",
        #                "subtitle_de_url_upload"
        #             ),
        #             "subtitle_de_url_upload",
        #             inject_xcom_data(
        #                parent_dag.dag_id,
        #                "asr_engine_remote",
        #                "op_create_url_by_xcom",
        #                "subtitle_en_url_upload"
        #             ),
        #             "subtitle_en_url_upload",
        #             config
        #    )
        #    t13.doc_md = """\
        #      #ASR Engine Remote mod9
        #      Create asr result from raw audio wav file and save it in assetdb-temp
        #      """
        if engine_operator == AsrEngineOperator.WHISPER_S2T:
            from modules.operators.docker_asr import op_docker_asr_engine_remote_whisper_s2t

            t13 = op_docker_asr_engine_remote_whisper_s2t(
                parent_dag.dag_id,
                "asr_result",
                container_id,
                inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_media_converter_audio, "op_create_url_by_xcom", "audio_raw_url"
                ),
                "audio_raw_url",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_remote", "op_get_single_data_from_xcom_json", "asr_locale"
                ),
                "asr_locale",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_remote", "op_create_url_by_xcom", "asr_result_de_url_upload"
                ),
                "asr_result_de_url_upload",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_remote", "op_create_url_by_xcom", "asr_result_en_url_upload"
                ),
                "asr_result_en_url_upload",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_remote", "op_create_url_by_xcom", "transcript_de_url_upload"
                ),
                "transcript_de_url_upload",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_remote", "op_create_url_by_xcom", "transcript_en_url_upload"
                ),
                "transcript_en_url_upload",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_remote", "op_create_url_by_xcom", "subtitle_de_url_upload"
                ),
                "subtitle_de_url_upload",
                inject_xcom_data(
                    parent_dag.dag_id, "asr_engine_remote", "op_create_url_by_xcom", "subtitle_en_url_upload"
                ),
                "subtitle_en_url_upload",
                config,
            )
            t13.doc_md = """\
              #ASR Engine Remote whisper-s2t
              Create asr result from raw audio wav file and save it in assetdb-temp
              """
        else:
            raise AirflowConfigException(
                "The specified ASR engine for asr_result is currently not supported! asr_engine: " + asr_engine
            )

        (t14, t15, t16, t17, t18, t19) = _publish_asr_engine_run(parent_dag, "asr_engine_remote")

        join_asr_urn = EmptyOperator(task_id="join-asr-urn", dag=parent_dag)
        join_asr_url = EmptyOperator(task_id="join-asr-url", dag=parent_dag)
        join_asr = EmptyOperator(task_id="join-asr", dag=parent_dag)

        t0 >> join_asr_urn
        [t1, t2, t3, t4, t5, t6] >> join_asr_urn
        join_asr_urn >> [t7, t8, t9, t10, t11, t12] >> join_asr_url
        join_asr_url >> t13 >> [t14, t15, t16, t17, t18, t19] >> join_asr

    return group2
