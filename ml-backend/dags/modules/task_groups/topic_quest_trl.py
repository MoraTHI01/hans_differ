from airflow import DAG
from airflow.utils.task_group import TaskGroup


def topic_quest_trl(parent_dag, dag_group_name_download_media_files, container_id, config: dict):
    """
    Translate topics and questionnaires TaskGroup to be used in a DAG.

    :param DAG parent_dag: Parent DAG instance
    :param str dag_group_name_download_media_files: Task group name for download media files task group
    :param str container_id: Container Id for DockerOperator
    :param str config: Configuration of docker operator (e.g. gpu usage)

    :return: TaskGroup to use in a DAG
    :rtype: airflow.utils.task_group.TaskGroup
    """
    use_orchestrator = False
    if "use_orchestrator" in config:
        use_orchestrator = config["use_orchestrator"]
    use_nlp_translate_remote = False
    if "use_nlp_translate_remote" in config:
        use_nlp_translate_remote = config["use_nlp_translate_remote"]
    with TaskGroup("topic_quest_trl") as group6:
        # XCOM injection helper
        from modules.operators.xcom import inject_xcom_data

        # Create urn with new uuid for topic result on assetdb-temp
        from modules.operators.storage import op_create_new_urn_on_assetdbtemp

        # Create urn with new uuid for topic result on assetdb-temp, for German and English
        t0 = op_create_new_urn_on_assetdbtemp(
            parent_dag, parent_dag.dag_id, "topic_result_en_urn", "topic_result_en_urn", ".json"
        )

        # Create url "topic_result_en_url" using previous urn "topic_result_en_urn" on assetdb-temp for upload
        from modules.operators.storage import op_create_url_by_xcom

        t1 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "topic_result_en_url_upload",
            "topic_result_en_url_upload",
            inject_xcom_data(
                parent_dag.dag_id, "topic_quest_trl", "op_create_new_urn_on_assetdbtemp", "topic_result_en_urn"
            ),
            "topic_result_en_urn",
            "upload",
        )

        if use_nlp_translate_remote is False:
            # Translate segment summaries from English to German
            from modules.operators.docker_nlp import op_docker_nlp_translate_local

            t2 = op_docker_nlp_translate_local(
                parent_dag.dag_id,
                "trl_topics",
                container_id,
                inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
                ),
                "topic_result_de_url",
                "en",
                inject_xcom_data(
                    parent_dag.dag_id, "topic_quest_trl", "op_create_url_by_xcom", "topic_result_en_url_upload"
                ),
                "topic_result_en_url_upload",
                config,
            )
            t2.doc_md = """\
              #NLP Translation
              Translate TopicResult json to target language and save it in assetdb-temp
              """
        else:
            # Translate segment summaries from English to German
            from modules.operators.nlp_translate import op_nlp_translate_remote

            t2 = op_nlp_translate_remote(
                dag=parent_dag,
                dag_id=parent_dag.dag_id,
                task_id_suffix="trl_topics",
                source_language="de",
                target_language="en",
                download_data=inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
                ),
                download_data_key="topic_result_de_urn",
                upload_data=inject_xcom_data(
                    parent_dag.dag_id, "topic_quest_trl", "op_create_new_urn_on_assetdbtemp", "topic_result_en_urn"
                ),
                upload_data_key="topic_result_en_urn",
                use_orchestrator=use_orchestrator,
            )
            t2.doc_md = """\
              #NLP Translation
              Translate TopicResult json to target language and save it in assetdb-temp
              """

        t3 = op_create_new_urn_on_assetdbtemp(
            parent_dag, parent_dag.dag_id, "questionnaire_result_en_urn", "questionnaire_result_en_urn", ".json"
        )

        t4 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "questionnaire_result_en_url_upload",
            "questionnaire_result_en_url_upload",
            inject_xcom_data(
                parent_dag.dag_id, "topic_quest_trl", "op_create_new_urn_on_assetdbtemp", "questionnaire_result_en_urn"
            ),
            "questionnaire_result_en_urn",
            "upload",
        )

        if use_nlp_translate_remote is False:
            # Translate questionnaire German to English
            from modules.operators.docker_nlp import op_docker_nlp_translate_local

            t5 = op_docker_nlp_translate_local(
                parent_dag.dag_id,
                "trl_questionnaire",
                container_id,
                inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
                ),
                "questionnaire_result_de_url",
                "en",
                inject_xcom_data(
                    parent_dag.dag_id, "topic_quest_trl", "op_create_url_by_xcom", "questionnaire_result_en_url_upload"
                ),
                "questionnaire_result_en_url_upload",
                config,
            )
            t5.doc_md = """\
             #NLP Translation
             Translate QuestionnaireResult json to target language
             and save it in assetdb-temp
             """
        else:
            # Translate questionnaire English to German
            from modules.operators.nlp_translate import op_nlp_translate_remote

            t5 = op_nlp_translate_remote(
                dag=parent_dag,
                dag_id=parent_dag.dag_id,
                task_id_suffix="trl_questionnaire",
                source_language="de",
                target_language="en",
                download_data=inject_xcom_data(
                    parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
                ),
                download_data_key="questionnaire_result_de_urn",
                upload_data=inject_xcom_data(
                    parent_dag.dag_id,
                    "topic_quest_trl",
                    "op_create_new_urn_on_assetdbtemp",
                    "questionnaire_result_en_urn",
                ),
                upload_data_key="questionnaire_result_en_urn",
                use_orchestrator=use_orchestrator,
            )
            t5.doc_md = """\
             #NLP Translation
             Translate QuestionnaireResult to target language
             and save it in assetdb-temp
             """

        t0 >> t1 >> t2 >> t3 >> t4 >> t5

    return group6
