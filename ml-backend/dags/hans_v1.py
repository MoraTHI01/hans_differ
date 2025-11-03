import pendulum
from airflow import DAG
from airflow.configuration import conf
from airflow.operators.dummy import DummyOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python import PythonOperator, PythonVirtualenvOperator, BranchPythonOperator

from datetime import datetime, timedelta


now = pendulum.now(tz="UTC")
now_to_the_hour = (now - timedelta(0, 0, 0, 0, 0, 3)).replace(minute=0, second=0, microsecond=0)
START_DATE = now_to_the_hour

default_args = {
    "owner": "airflow",
    "description": "HAnS media file processing",
    "depend_on_past": False,
    "start_date": START_DATE,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 5,
    "retry_delay": timedelta(seconds=30),
}

# DAG name is the dag_id and needs to contain a version string at the end.
# The version part is starting with "_v" and uses semantic versioning
# A new major version will result in a new hans python file, e.g. "hans_v2.py"
# A new TaskGroup which is introduced will increase the minor version, e.g. "hans_v1.1.0"
# Fixes will increase the last part of the version number, e.g. "hans_v1.0.1"
# Limit active DAG runs to 1 to not stuck with resources e.g. RAM or CPU on docker,
# see https://www.astronomer.io/guides/airflow-scaling-workers/ and
# https://airflow.apache.org/docs/apache-airflow/stable/faq.html#how-to-improve-dag-performance
DAG_NAME = "hans_v1.0.3"
with DAG(DAG_NAME, default_args=default_args, schedule_interval=None, catchup=False, max_active_runs=1) as dag:
    now = datetime.now()
    time_started = now.strftime("%m_%d_%Y_%H_%M_%S")

    # DEVELOPER CONFIGURATION
    do_publish = True
    do_video_encoding = True
    do_use_remote_asr_engine = True
    do_use_nlp_translate_remote = True
    do_topic_segmentation_remote = True
    # CONFIGURATION END

    if do_video_encoding is False:
        do_publish = False

    # Used to create unique docker container id
    container_id = time_started

    # TASK GROUPS USED IN GRAPH DEFINITION

    from modules.task_groups.download import download_media_files

    group0 = download_media_files(dag)

    from modules.task_groups.media_converter import media_converter_audio

    group1 = media_converter_audio(dag, "download_media_files", container_id)

    # hans_v1.0.4 will add Anonymization
    # from modules.task_groups.text_extraction import text_extraction
    # group2 = text_extraction(dag, "download_media_files", container_id)

    from modules.task_groups.slides_processor import slides_processor

    group3 = slides_processor(dag, "download_media_files", config={"use_orchestrator": False, "dpi": 150})

    if not do_use_remote_asr_engine is True:
        # ASR ENGINE LOCAL TASK GROUP
        # creates transcript and subtitles
        asr_engine_task_group_name = "asr_engine_local"

        from modules.task_groups.asr_engine import asr_engine_local

        # Activation of different ASR engines is possible by specifying different parameter here
        group4 = asr_engine_local(
            dag,
            "download_media_files",
            "media_converter_audio",
            container_id,
            # USE WHISPER_S2T on CPU not for production! Use OPENAI on CPU for production instead!
            "OPENAI",
            config={
                "batch_size": 8,
                "num_cpus": 4.0,
                "ram_limit_docker": "10g",
                "use_gpu": False,
                "asr_model": "medium",
            },
        )
    else:
        # ASR ENGINE REMOTE TASK GROUP
        # creates transcript and subtitles
        asr_engine_task_group_name = "asr_engine_remote"

        from modules.task_groups.asr_engine import asr_engine_remote

        # Activation of different ASR engines is possible by specifying different parameter here
        group4 = asr_engine_remote(
            dag,
            "download_media_files",
            "media_converter_audio",
            container_id,
            # USE WHISPER_S2T, mod9 currently not fully implemented
            "WHISPER_S2T",
            config={
                "use_orchestrator": False,
                "batch_size": 8,  # 8 for smaller GPU's e.g. RTX 2080 Ti, 48 for data center e.g. A100 40GB
                "asr_model": "large-v3",
            },
        )

    from modules.task_groups.search_data_preparation import search_data_preparation

    group5 = search_data_preparation(
        parent_dag=dag,
        dag_group_name_download_media_files="download_media_files",
        dag_group_name_asr_engine=asr_engine_task_group_name,
        dag_group_name_summarization="summarization",
    )

    # topic segmentation of video content
    if do_topic_segmentation_remote:
        from modules.task_groups.topic_segmentation_remote import topic_segmentation

        ts_config = {"use_nlp_translate_remote": do_use_nlp_translate_remote, "use_orchestrator": False}
        group6 = topic_segmentation(
            dag, "download_media_files", asr_engine_task_group_name, container_id, config=ts_config
        )
    else:
        print(
            "Local topic segmentation image is currently not pre-built. "
            "Remove skip file `ml-backend/dags/docker_jobs/topic-segmentation/skip` and re-build ml-backend"
        )
        from modules.task_groups.topic_segmentation_unsupervised import topic_segmentation

        ts_config = {
            "use_nlp_translate_remote": do_use_nlp_translate_remote,
            "use_orchestrator": False,
            "use_gpu": False,
            "embedding_model": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        }
        group6 = topic_segmentation(
            dag, "download_media_files", asr_engine_task_group_name, container_id, config=ts_config
        )

    # questionnaire for each video topic
    from modules.task_groups.questionnaire import questionnaire

    group7 = questionnaire(
        dag,
        "download_media_files",
        "topic_segmentation",
        "op_create_new_urn_on_assetdbtemp",
        "topic_result_urn",
        "topic_result_urn",
        container_id,
        config={"use_nlp_translate_remote": do_use_nlp_translate_remote, "use_orchestrator": False, "use_gpu": False},
    )

    # summarization of video content
    from modules.task_groups.summarization import summarization

    group8 = summarization(
        dag,
        "download_media_files",
        asr_engine_task_group_name,
        container_id,
        config={"use_nlp_translate_remote": do_use_nlp_translate_remote, "use_orchestrator": False, "use_gpu": False},
    )

    # CONVERT VIDEO FOR STREAMING

    # Video resolution could be configured, default value is 'hd' (720p)
    # with a streaming encoding speed near the half of the video duration (factor 2.x).
    # For 1080p use 'full-hd' as value but the streaming encoding speed will decrease
    # to near realtime (factor 1.x) depending on the system hardware configuration.
    from modules.task_groups.media_converter import media_converter_video

    group9 = media_converter_video(
        dag,
        "download_media_files",
        container_id,
        do_video_encoding,
        config={"num_cpus": 4.0, "ram_limit_docker": "10g", "use_gpu": False, "resolution": "hd"},
    )

    # Video-to-Slide (VTS) Alignment
    # Align the video and the slides content and create timestamps for each slide when it should be displayed
    from modules.task_groups.media_alignment import media_alignment

    group10 = media_alignment(
        dag,
        "download_media_files",
        asr_engine_task_group_name,
        "slides_processor",
        config={
            "autoimage_name": "MBZUAI/swiftformer-xs",
            "sentence_model_name": "sentence-transformers/distiluse-base-multilingual-cased",
            "jump_penalty": 0.1,
            "merge_method": "max",  # Supported methods: mean, max, all, weighted_sum
        },
    )

    from modules.task_groups.keyword_extraction import keyword_extractor

    group11 = keyword_extractor(dag, "download_media_files", "slides_processor", asr_engine_task_group_name)

    # PUBLISHING TASK GROUP

    # Artefacts to be uploaded to backend in publishing task group
    from modules.operators.transfer import Artefact, HansType

    # Main metadata artefact used to store the metadata in metadb
    # fmt: off
    meta_artefact = Artefact(dag.dag_id, "download_media_files", "op_download_and_store_local",
            "meta_urn", HansType.META_DATA, "assetdb-temp", "archive", "metadb", "meta:post:id")

    # Slides artefact
    slide_artefact = Artefact(dag.dag_id, "download_media_files", "op_download_and_store_local",
            "slides_urn", HansType.SLIDES, "assetdb-temp", "archive", "assetdb", "assets")

    if do_video_encoding is True:
        # Media artefact contains multiple files
        media_artefact = Artefact(dag.dag_id, "media_converter_video", "op_create_new_urn_on_assetdbtemp",
                "video_dash_urn", HansType.MEDIA, "assetdb-temp", "archive", "mediadb", "videos", True)

    # Media thumbnails artefact contains multiple files
    media_thumbnails_artefact = Artefact(dag.dag_id, "media_converter_video", "op_create_new_urn_on_assetdbtemp",
            "video_thumb_urn", HansType.THUMBNAILS_MEDIA, "assetdb-temp", "archive", "assetdb", "assets" , True)
    # Slides images artefact contains multiple files per slide, the slide picture e,g. 1.png,
    # the search vector slide file e.g. 1.json, and for each slides file aggregated slides meta data e.g. slides.meta.json
    slides_images_artefact = Artefact(dag.dag_id, "slides_processor", "op_create_new_urn_on_assetdbtemp",
            "slides_images_urn", HansType.SLIDES_IMAGES_META, "assetdb-temp", "archive", "assetdb", "assets" , True)

    all_artefacts_with_urns = [
        Artefact(dag.dag_id, asr_engine_task_group_name, "op_create_new_urn_on_assetdbtemp",
            "asr_result_de_urn", HansType.ASR_RESULT_DE, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, asr_engine_task_group_name, "op_create_new_urn_on_assetdbtemp",
            "asr_result_en_urn", HansType.ASR_RESULT_EN, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, "media_converter_audio", "op_create_new_urn_on_assetdbtemp",
            "audio_raw_urn", HansType.AUDIO, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, asr_engine_task_group_name, "op_create_new_urn_on_assetdbtemp",
            "transcript_de_urn", HansType.TRANSCRIPT_DE, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, asr_engine_task_group_name, "op_create_new_urn_on_assetdbtemp",
            "transcript_en_urn", HansType.TRANSCRIPT_EN, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, asr_engine_task_group_name, "op_create_new_urn_on_assetdbtemp",
            "subtitle_de_urn", HansType.SUBTITLE_DE, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, asr_engine_task_group_name, "op_create_new_urn_on_assetdbtemp",
            "subtitle_en_urn", HansType.SUBTITLE_EN, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, "summarization", "op_create_new_urn_on_assetdbtemp", "short_summary_result_de_urn",
            HansType.SHORT_SUMMARY_RESULT_DE, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, "summarization", "op_create_new_urn_on_assetdbtemp", "short_summary_result_en_urn",
            HansType.SHORT_SUMMARY_RESULT_EN, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, "summarization", "op_create_new_urn_on_assetdbtemp",
            "summary_result_de_urn", HansType.SUMMARY_RESULT_DE, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, "summarization", "op_create_new_urn_on_assetdbtemp",
            "summary_result_en_urn", HansType.SUMMARY_RESULT_EN, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, "topic_segmentation", "op_create_new_urn_on_assetdbtemp",
            "topic_result_urn", HansType.TOPIC_RESULT_RAW, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, "topic_segmentation", "op_create_new_urn_on_assetdbtemp",
            "topic_result_de_urn", HansType.TOPIC_RESULT_DE, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, "topic_segmentation", "op_create_new_urn_on_assetdbtemp",
            "topic_result_en_urn", HansType.TOPIC_RESULT_EN, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, "search_data_preparation", "op_create_new_urn_on_assetdbtemp",
            "search_data_urn", HansType.SEARCH_DATA, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, "search_data_preparation", "op_create_new_urn_on_assetdbtemp",
                 "search_data_vectors_urn", HansType.SEARCH_DATA_VECTORS, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, "search_data_preparation", "op_create_new_urn_on_assetdbtemp",
                 "search_summary_data_vector_urn", HansType.SEARCH_SUMMARY_DATA_VECTOR, "assetdb-temp", "archive", "assetdb",
                 "assets"),
        Artefact(dag.dag_id, "search_data_preparation.local_search_data_preparation", "op_create_new_urn_on_assetdbtemp",
                 "local_search_data_de_urn", HansType.SEARCH_TRIE_DE, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, "search_data_preparation.local_search_data_preparation", "op_create_new_urn_on_assetdbtemp",
                 "local_search_data_en_urn", HansType.SEARCH_TRIE_EN, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, "questionnaire", "op_create_new_urn_on_assetdbtemp",
            "questionnaire_result_de_urn", HansType.QUESTIONNAIRE_RESULT_DE, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, "questionnaire", "op_create_new_urn_on_assetdbtemp",
            "questionnaire_result_en_urn", HansType.QUESTIONNAIRE_RESULT_EN, "assetdb-temp", "archive", "assetdb", "assets"),
        Artefact(dag.dag_id, "keyword_extractor", "op_create_new_urn_on_assetdbtemp",
                "keywords_result_urn", HansType.KEYWORDS_RESULT, "assetdb-temp", "archive", "assetdb",
                 "assets"),
        Artefact(dag.dag_id, "keyword_extractor", "op_create_new_urn_on_assetdbtemp",
                "slides_trie_result_urn", HansType.SLIDES_TRIE, "assetdb-temp", "archive", "assetdb",
                 "assets")
    ]
    # fmt: on

    if do_publish is True:
        from modules.task_groups.publish import publish_artefacts

        group12 = publish_artefacts(
            dag,
            "download_media_files",
            [slide_artefact],
            all_artefacts_with_urns,
            media_artefact,
            [media_thumbnails_artefact, slides_images_artefact],
            meta_artefact,
            time_started,
        )

    # ARCHIVING TASK GROUP

    from modules.task_groups.archive import archive_artefacts

    if do_video_encoding is True:
        group13 = archive_artefacts(
            dag,
            "download_media_files",
            [meta_artefact, slide_artefact],
            all_artefacts_with_urns + [media_artefact] + [media_thumbnails_artefact, slides_images_artefact],
            time_started,
        )
    else:
        group13 = archive_artefacts(
            dag,
            "download_media_files",
            [meta_artefact, slide_artefact],
            all_artefacts_with_urns + [media_thumbnails_artefact, slides_images_artefact],
            time_started,
        )

    join = EmptyOperator(task_id="join", dag=dag)
    # GRAPH DEFINITION
    if do_publish is True:
        group0 >> group3 >> group10
        group0 >> group9 >> join
        group0 >> group1 >> group4 >> group6 >> group7 >> group10
        group4 >> group8 >> group5 >> group10
        group10 >> group11 >> join
        join >> group12 >> group13
    else:
        group0 >> group3 >> group10
        group0 >> group9 >> join
        group0 >> group1 >> group4 >> group6 >> group7 >> group10
        group4 >> group8 >> group5 >> group10
        group10 >> group11 >> join
        join >> group13
