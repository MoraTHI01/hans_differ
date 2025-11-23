#!/usr/bin/env python
"""
XCOM operators and helpers.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import pendulum
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator


def gen_task_id(dag_id, operator_name, operator_taskid_suffix):
    """
    Helper to create a task_id for an operator, used to receive XCom data.
    See 'inject_xcom_data'

    :param str dag_id: DAG id of the operators DAG.
    :param str operator_name: Name of the operator.
    :param str operator_taskid_suffix: Suffix for the operator task_id.

    :return: dict Configuration for assetdb-temp
    """
    return operator_name + "_" + dag_id + "_" + operator_taskid_suffix


def inject_xcom_data(
    parent_dag_id, task_group_id, source_operator_name, source_operator_task_id_suffix, xcom_key="return_value"
):
    """
    Helper to inject XCom data from an other operator of a task group
    mainly used for operators to inject the XCom data they need.

    See https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/xcoms.html#xcoms
    Check LazySelectSequence in
    https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/dynamic-task-mapping.html
    which requires now [0] in the returned template

    :param str parent_dag_id: Id of the parent dag, e.g. 'parent_dag.dag_id' of the task group and source operator
    :param str task_group_id: id of the task group, e.g. 'media_converter_audio', if the source operator is not in a task group use empty string here
    :param str source_operator_name: Name of the source operator which is part of the task group, e.g. 'op_create_new_urn_on_assetdbtemp'
    :param str source_operator_task_id_suffix: Source operator task id suffix, usually corresponds to hans_type parameter, e.g. 'audio_raw_urn'
    :param str xcom_key: XCom key where the source operator pushed the data to XCom, usually 'return_value' if no xcom.push method used, default: 'return_value'

    :return: str Jinja template string to inject the XCOM data
    """
    task_id = None
    if not task_group_id:
        task_id = source_operator_name + "_" + parent_dag_id + "_" + source_operator_task_id_suffix
    else:
        task_id = (
            task_group_id + "." + source_operator_name + "_" + parent_dag_id + "_" + source_operator_task_id_suffix
        )
    return "{{ ti.xcom_pull(key='" + xcom_key + "', task_ids=['" + task_id + "'])[0] }}"


def get_data_from_xcom(xcom_data: str, xcom_data_keys: list):
    """
    Helper to parse xcom data structure to return string value
    of given xcom data key.

    :param str xcom_data: XCOM data string
    :param list xcom_data_keys: List with data keys

    :return: str Value of the data key, None otherwise
    """
    import ast

    print("get_data_from_xcom")
    print(f"XCOM Data: {xcom_data}")
    print(f"XCOM Data Keys: {xcom_data_keys}")
    try:
        xcom_array = ast.literal_eval(xcom_data)
        print(f"XCOM Data Obj: {xcom_array}")
        for item in xcom_array:
            for value in xcom_data_keys:
                if value in item:
                    print(f"XCOM Found key! value: {value}, item: {item}")
                    if isinstance(item, dict):
                        print("XCOM Item is a dictionary")
                        return item[value]
                    else:
                        print("XCOM Item is not a dictionary")
                        return xcom_array[value]
            xcom_dict = dict(item)
            for subitem in xcom_dict:
                for value in xcom_data_keys:
                    if value in subitem:
                        print("XCOM Found key in subitem!")
                        return subitem[value]
    except:
        print("Error: Exception occured. XCOM Key not found!")
        return None
    print("Error: XCOM Key not found!")
    return None


def get_single_data_from_xcom_json(xcom_data, xcom_data_keys, output_key=None):
    """
    Helper to parse xcom data structure to return json value
    of given xcom data key with new output key

    :param str xcom_data: XCOM data string
    :param array xcom_data_keys: String array with data keys
    :param str output_key: String output key

    :return: json Json containing the output_key with the value of the data key, None otherwise
    """
    from modules.operators.xcom import get_data_from_xcom

    result = get_data_from_xcom(xcom_data, xcom_data_keys)
    if result is not None:
        return '{"' + output_key + '": "' + result + '"}'
    else:
        return None


def op_get_data_from_xcom(dag, dag_id, task_id_suffix, xcom_data, xcom_data_keys):
    """
    Provides PythonVirtualenvOperator to get data from xcom by key
    Converts video or podcast file to wav and saves it in assetdb-temp.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str xcom_data: XCOM Data which contains data keys.
    :param list xcom_data_keys: String list with XCOM data keys.

    :return: PythonVirtualenvOperator to get data from xcom by key
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_get_data_from_xcom", task_id_suffix),
        python_callable=get_data_from_xcom,
        op_args=[xcom_data, xcom_data_keys],
        requirements=[
            "/opt/hans-modules/dist/hans_shared_modules-0.1-py3-none-any.whl",
            "eval-type-backport",
            "datetime",
        ],
        # pip_install_options=["--force-reinstall"],
        python_version="3",
        dag=dag,
    )


def op_get_single_data_from_xcom_json(dag, dag_id, task_id_suffix, xcom_data, xcom_data_keys, output_key):
    """
    Provides PythonVirtualenvOperator to get single data from xcom by key
    Converts video or podcast file to wav and saves it in assetdb-temp.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str xcom_data: XCOM Data which contains data keys.
    :param list xcom_data_keys: String list with XCOM data keys.
    :param str output_key: Use this output key as the new json key for the obtained data.

    :return: PythonVirtualenvOperator to get single data from xcom by key
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_get_single_data_from_xcom_json", task_id_suffix),
        python_callable=get_single_data_from_xcom_json,
        op_args=[xcom_data, xcom_data_keys, output_key],
        requirements=[
            "/opt/hans-modules/dist/hans_shared_modules-0.1-py3-none-any.whl",
            "eval-type-backport",
            "datetime",
        ],
        # pip_install_options=["--force-reinstall"],
        python_version="3",
        dag=dag,
    )


def xcom_data_contains_key(xcom_data, xcom_data_key):
    """
    Helper to check if a specific key is contained
    in a xcom data structure.

    :param str xcom_data: XCOM data string
    :param array xcom_data_key: String XCOM data key

    :return: bool True if key is in xcom data, otherwise False
    """
    import ast

    try:
        xcom_array = ast.literal_eval(xcom_data)
        for item in xcom_array:
            xcom_dict = ast.literal_eval(item)
            if xcom_data_key in xcom_dict:
                return True
            for subitem in xcom_dict:
                if xcom_data_key in subitem:
                    return True
    except:
        return False
