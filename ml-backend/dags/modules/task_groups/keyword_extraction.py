from airflow.utils.task_group import TaskGroup


def keyword_extractor(
    parent_dag, dag_group_name_download_media_files, dag_group_name_slides_processor, dag_group_name_asr_engine
) -> TaskGroup:
    """
    Generate a slides_processor TaskGroup to be used in a DAG.

    :param DAG parent_dag: Parent DAG instance
    :param str dag_group_name_download_media_files: Task group name for download media files task group

    :param str config: Configuration for used asr engine with keys e.g. use_gpu

    :return: TaskGroup to use in a DAG
    :rtype: airflow.utils.task_group.TaskGroup
    """
    with TaskGroup("keyword_extractor") as group11:
        # XCOM injection helper
        from modules.operators.xcom import inject_xcom_data

        # Create urn with new uuid for keywords result on assetdb-temp
        from modules.operators.storage import op_create_new_urn_on_assetdbtemp

        t0 = op_create_new_urn_on_assetdbtemp(
            parent_dag, parent_dag.dag_id, "keywords_result_urn", "keywords_result_urn"
        )

        # Extract keywords from slides text
        from modules.operators.llm_remote import op_llm_remote_prompt

        t1 = op_llm_remote_prompt(
            dag=parent_dag,
            dag_id=parent_dag.dag_id,
            task_id_suffix="create_keywords",
            mode="keywords",
            context_data=inject_xcom_data(
                parent_dag.dag_id,
                dag_group_name_slides_processor,
                "op_create_new_urn_on_assetdbtemp",
                "slides_images_urn",
            ),
            context_data_key="slides_images_urn",
            download_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_download_media_files, "op_download_and_store_local", "download"
            ),
            download_meta_urn_key="meta_urn",
            upload_llm_result_data=inject_xcom_data(
                parent_dag.dag_id, "keyword_extractor", "op_create_new_urn_on_assetdbtemp", "keywords_result_urn"
            ),
            upload_llm_result_urn_key="keywords_result_urn",
            use_orchestrator=False,
        )
        t1.doc_md = """\
          #Keyword Extraction
          Extracts keywords from the slides text and saves them on assetdb-temp.
          """

        # Add counts to the keywords result (based on transcript)
        from modules.operators.keyword_counter import op_keyword_counter

        t2 = op_keyword_counter(
            dag=parent_dag,
            dag_id=parent_dag.dag_id,
            task_id_suffix="count_keywords",
            transcript_de_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_asr_engine, "op_create_new_urn_on_assetdbtemp", "transcript_de_urn"
            ),
            transcript_de_data_key="transcript_de_urn",
            transcript_en_data=inject_xcom_data(
                parent_dag.dag_id, dag_group_name_asr_engine, "op_create_new_urn_on_assetdbtemp", "transcript_en_urn"
            ),
            transcript_en_data_key="transcript_en_urn",
            keyword_data=inject_xcom_data(
                parent_dag.dag_id, "keyword_extractor", "op_create_new_urn_on_assetdbtemp", "keywords_result_urn"
            ),
            keyword_data_key="keywords_result_urn",
        )
        t2.doc_md = """\
          #Count Keywords
          Counts the extracted keywords in the transcript and saves them on assetdb-temp.
          """

        # Create urn with new uuid for slides trie result on assetdb-temp
        from modules.operators.storage import op_create_new_urn_on_assetdbtemp

        t3 = op_create_new_urn_on_assetdbtemp(
            parent_dag, parent_dag.dag_id, "slides_trie_result_urn", "slides_trie_result_urn"
        )

        # Create slides local search trie
        from modules.operators.slides_local_search import op_create_local_slides_search_trie

        t4 = op_create_local_slides_search_trie(
            parent_dag,
            parent_dag.dag_id,
            "create_slides_local_search_trie",
            inject_xcom_data(
                parent_dag.dag_id,
                dag_group_name_slides_processor,
                "op_create_new_urn_on_assetdbtemp",
                "slides_images_urn",
            ),
            "slides_images_urn",
            inject_xcom_data(
                parent_dag.dag_id, "keyword_extractor", "op_create_new_urn_on_assetdbtemp", "slides_trie_result_urn"
            ),
            "slides_trie_result_urn",
        )

        t0 >> t1 >> t2 >> t3 >> t4

    return group11
