from airflow.utils.task_group import TaskGroup


def questionnaire(
    parent_dag,
    dag_group_name_download_media_files,
    dag_group_name_topic_segmentation,
    dag_op_topic_segmentation,
    dag_op_key_topic_segmentation,
    dag_topic_segmentation_res_urn_key,
    container_id,
    config: dict,
) -> TaskGroup:
    """
    Generate a questionnaire TaskGroup to be used in a DAG.

    :param DAG parent_dag: Parent DAG instance
    :param str dag_group_name_download_media_files: Task group name for download media files task group
    :param str dag_group_name_topic_segmentation: Task group name for topic_segmentation or chapter title sum task group
    :param str dag_op_topic_segmentation: Operator which creates the dag_topic_segmentation_res_urn_key
    :param str dag_op_key_topic_segmentation: Key published by operator dag_op_topic_segmentation
    :param str dag_topic_segmentation_res_urn_key: Topic segmentation result urn key in topic_segmentation task group or chapter title sum task group
    :param str container_id: Container Id for DockerOperator
    :param str config: Configuration of docker operator (e.g. gpu usage)

    :return: TaskGroup to use in a DAG
    :rtype: airflow.utils.task_group.TaskGroup
    """
    use_nlp_translate_remote = False
    if "use_nlp_translate_remote" in config:
        use_nlp_translate_remote = config["use_nlp_translate_remote"]
    llm_configs = {}
    if "llm_configs" in config:
        llm_configs = config["llm_configs"]
    with TaskGroup("questionnaire") as group7:
        # XCOM injection helper
        from modules.operators.xcom import inject_xcom_data

        # Create urn with new uuid for topic result on assetdb-temp
        from modules.operators.storage import op_create_new_urn_on_assetdbtemp

        # Create urn with new uuid for questionnaire result on assetdb-temp, for German and English
        t0 = op_create_new_urn_on_assetdbtemp(
            parent_dag, parent_dag.dag_id, "questionnaire_result_de_urn", "questionnaire_result_de_urn", ".json"
        )

        t1 = op_create_new_urn_on_assetdbtemp(
            parent_dag, parent_dag.dag_id, "questionnaire_result_en_urn", "questionnaire_result_en_urn", ".json"
        )

        # Create questionnaire
        from modules.operators.llm_remote import op_llm_remote_prompt

        t2 = op_llm_remote_prompt(
            dag=parent_dag,
            dag_id=parent_dag.dag_id,
            task_id_suffix="create_questionnaire",
            mode="questionnaire",
            context_data=inject_xcom_data(
                parent_dag.dag_id,
                dag_group_name_topic_segmentation,
                dag_op_topic_segmentation,
                dag_op_key_topic_segmentation,
            ),
            context_data_key=dag_topic_segmentation_res_urn_key,
            download_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
            ),
            download_meta_urn_key="meta_urn",
            upload_llm_result_data=inject_xcom_data(
                parent_dag.dag_id, "questionnaire", "op_create_new_urn_on_assetdbtemp", "questionnaire_result_en_urn"
            ),
            upload_llm_result_urn_key="questionnaire_result_en_urn",
            llm_configs=llm_configs,
        )
        t2.doc_md = """\
          #Questionnaire
          Use topic result raw file to create multiple choice questions
          for each topic using a remote LLM service.
          """

        # Create url "questionnaire_result_en_url" using previous urn "questionnaire_result_en_urn" on assetdb-temp for download
        from modules.operators.storage import op_create_url_by_xcom

        t3 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "questionnaire_result_en_url",
            "questionnaire_result_en_url",
            inject_xcom_data(
                parent_dag.dag_id, "questionnaire", "op_create_new_urn_on_assetdbtemp", "questionnaire_result_en_urn"
            ),
            "questionnaire_result_en_urn",
            "download",
        )

        # Translation of questionnaire_result_en_urn to questionnaire_result_de_urn

        # Create url "questionnaire_result_de_url" using previous urn "questionnaire_result_de_urn" on assetdb-temp for upload
        from modules.operators.storage import op_create_url_by_xcom

        t4 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "questionnaire_result_de_url_upload",
            "questionnaire_result_de_url_upload",
            inject_xcom_data(
                parent_dag.dag_id, "questionnaire", "op_create_new_urn_on_assetdbtemp", "questionnaire_result_de_urn"
            ),
            "questionnaire_result_de_urn",
            "upload",
        )

        if use_nlp_translate_remote is False:
            # Translate questionnaire English to German
            from modules.operators.docker_nlp import op_docker_nlp_translate_local

            t5 = op_docker_nlp_translate_local(
                parent_dag.dag_id,
                "trl_questionnaire",
                container_id,
                inject_xcom_data(
                    parent_dag.dag_id, "questionnaire", "op_create_url_by_xcom", "questionnaire_result_en_url"
                ),
                "questionnaire_result_en_url",
                "de",
                inject_xcom_data(
                    parent_dag.dag_id, "questionnaire", "op_create_url_by_xcom", "questionnaire_result_de_url_upload"
                ),
                "questionnaire_result_de_url_upload",
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
                source_language="en",
                target_language="de",
                download_data=inject_xcom_data(
                    parent_dag.dag_id,
                    "questionnaire",
                    "op_create_new_urn_on_assetdbtemp",
                    "questionnaire_result_en_urn",
                ),
                download_data_key="questionnaire_result_en_urn",
                upload_data=inject_xcom_data(
                    parent_dag.dag_id,
                    "questionnaire",
                    "op_create_new_urn_on_assetdbtemp",
                    "questionnaire_result_de_urn",
                ),
                upload_data_key="questionnaire_result_de_urn",
                llm_configs=llm_configs,
            )
            t5.doc_md = """\
             #NLP Translation
             Translate QuestionnaireResult to target language
             and save it in assetdb-temp
             """

        # Create url "questionnaire_result_de_url" using previous urn "questionnaire_result_de_urn" on assetdb-temp for download
        from modules.operators.storage import op_create_url_by_xcom

        t6 = op_create_url_by_xcom(
            parent_dag,
            parent_dag.dag_id,
            "questionnaire_result_de_url",
            "questionnaire_result_de_url",
            inject_xcom_data(
                parent_dag.dag_id, "questionnaire", "op_create_new_urn_on_assetdbtemp", "questionnaire_result_de_urn"
            ),
            "questionnaire_result_de_urn",
            "download",
        )

        t0 >> t1 >> t2 >> t3 >> t4 >> t5 >> t6

    return group7
