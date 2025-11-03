from airflow import DAG
from airflow.utils.task_group import TaskGroup


def chapter_title_sum(parent_dag, dag_group_name_download_media_files, container_id, config: dict):
    """
    Generate a chapter title summary TaskGroup to be used in a DAG.

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
    with TaskGroup("chapter_title_sum") as group6:
        # XCOM injection helper
        from modules.operators.xcom import inject_xcom_data

        # Create urn with new uuid for topic result on assetdb-temp
        from modules.operators.storage import op_create_new_urn_on_assetdbtemp

        # Create urn with new uuid for topic result on assetdb-temp, for German and English
        t0 = op_create_new_urn_on_assetdbtemp(
            parent_dag, parent_dag.dag_id, "topic_result_de_urn", "topic_result_de_urn", ".json"
        )

        t1 = op_create_new_urn_on_assetdbtemp(
            parent_dag, parent_dag.dag_id, "topic_result_en_urn", "topic_result_en_urn", ".json"
        )

        # Create summaries and titles of topic segments
        from modules.operators.llm_remote import op_llm_remote_prompt

        t6 = op_llm_remote_prompt(
            dag=parent_dag,
            dag_id=parent_dag.dag_id,
            task_id_suffix="create_segment_summaries",
            mode="topic_summary",
            context_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
            ),
            context_data_key="topic_result_raw_urn",
            download_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
            ),
            download_meta_urn_key="meta_urn",
            upload_llm_result_data=inject_xcom_data(
                parent_dag.dag_id, "chapter_title_sum", "op_create_new_urn_on_assetdbtemp", "topic_result_en_urn"
            ),
            upload_llm_result_urn_key="topic_result_en_urn",
            use_orchestrator=use_orchestrator,
        )

        # Create url "topic_result_en_url" using previous urn "topic_result_en_urn" on assetdb-temp for download
        from modules.operators.storage import op_create_url_by_xcom

        t7 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "topic_result_en_url",
            "topic_result_en_url",
            inject_xcom_data(
                parent_dag.dag_id, "chapter_title_sum", "op_create_new_urn_on_assetdbtemp", "topic_result_en_urn"
            ),
            "topic_result_en_urn",
            "download",
        )

        # Translation of topic_result_en_urn to topic_result_de_urn

        # Create url "topic_result_de_url" using previous urn "topic_result_de_urn" on assetdb-temp for upload
        t8 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "topic_result_de_url_upload",
            "topic_result_de_url_upload",
            inject_xcom_data(
                parent_dag.dag_id, "chapter_title_sum", "op_create_new_urn_on_assetdbtemp", "topic_result_de_urn"
            ),
            "topic_result_de_urn",
            "upload",
        )

        if use_nlp_translate_remote is False:
            # Translate segment summaries from English to German
            from modules.operators.docker_nlp import op_docker_nlp_translate_local

            t9 = op_docker_nlp_translate_local(
                parent_dag.dag_id,
                "trl_chapter_title_sum",
                container_id,
                inject_xcom_data(
                    parent_dag.dag_id, "chapter_title_sum", "op_create_url_by_xcom", "topic_result_en_url"
                ),
                "topic_result_en_url",
                "de",
                inject_xcom_data(
                    parent_dag.dag_id, "chapter_title_sum", "op_create_url_by_xcom", "topic_result_de_url_upload"
                ),
                "topic_result_de_url_upload",
                config,
            )
            t9.doc_md = """\
              #NLP Translation
              Translate TopicResult json to target language and save it in assetdb-temp
              """
        else:
            # Translate segment summaries from English to German
            from modules.operators.nlp_translate import op_nlp_translate_remote

            t9 = op_nlp_translate_remote(
                dag=parent_dag,
                dag_id=parent_dag.dag_id,
                task_id_suffix="trl_chapter_title_sum",
                source_language="en",
                target_language="de",
                download_data=inject_xcom_data(
                    parent_dag.dag_id, "chapter_title_sum", "op_create_new_urn_on_assetdbtemp", "topic_result_en_urn"
                ),
                download_data_key="topic_result_en_urn",
                upload_data=inject_xcom_data(
                    parent_dag.dag_id, "chapter_title_sum", "op_create_new_urn_on_assetdbtemp", "topic_result_de_urn"
                ),
                upload_data_key="topic_result_de_urn",
                use_orchestrator=use_orchestrator,
            )
            t9.doc_md = """\
              #NLP Translation
              Translate TopicResult json to target language and save it in assetdb-temp
              """

        # Create url "topic_result_de_url" using previous urn "topic_result_de_urn" on assetdb-temp for download
        t10 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "topic_result_de_url",
            "topic_result_de_url",
            inject_xcom_data(
                parent_dag.dag_id, "chapter_title_sum", "op_create_new_urn_on_assetdbtemp", "topic_result_de_urn"
            ),
            "topic_result_de_urn",
            "download",
        )

        t0 >> t1 >> t6 >> t7 >> t8 >> t9 >> t10

    return group6
