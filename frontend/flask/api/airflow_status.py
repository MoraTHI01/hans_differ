#!/usr/bin/env python
"""Airflow status API"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"

import json
import requests
from typing import List, Optional, Dict, Any
import os

from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field

from api.modules.responses import ErrorResponse, JsonResponse

airflow_status_api_bp = APIBlueprint(
    "airflow_status",
    __name__,
    abp_responses={"401": ErrorResponse, "403": ErrorResponse},
)

airflow_tag = Tag(name="airflow status", description="Airflow status operations")

class TaskInstance(BaseModel):
    """Task instance information"""
    duration: Optional[float] = Field(None, description="Duration of the task in seconds")
    state: Optional[str] = Field(None, description="Current state of the task")
    task_id: str = Field(..., description="ID of the task")
    start_date: Optional[str] = Field(None, description="Start date of the task")
    end_date: Optional[str] = Field(None, description="End date of the task")
    try_number: int = Field(..., description="Current try number")
    max_tries: int = Field(..., description="Maximum number of tries")
    hostname: str = Field(..., description="Hostname where the task is running")
    operator: str = Field(..., description="Type of operator")

class InputFile(BaseModel):
    """Input file information"""
    filename: str = Field(..., description="Name of the file")
    hans_type: str = Field(..., description="Type of the file in HAnS")
    locale: str = Field(..., description="Locale of the file")
    mime_type: str = Field(..., description="MIME type of the file")
    urn: str = Field(..., description="URN of the file")

class OutputFile(BaseModel):
    """Output file information"""
    backend: str = Field(..., description="Backend URL")
    frontend: str = Field(..., description="Frontend URL")

class DAGRun(BaseModel):
    """DAG run information"""
    dag_run_id: str = Field(..., description="ID of the DAG run")
    state: str = Field(..., description="Current state of the DAG")
    start_date: Optional[str] = Field(None, description="Start date of the DAG")
    end_date: Optional[str] = Field(None, description="End date of the DAG")
    conf: Dict[str, Any] = Field(..., description="Configuration of the DAG run")
    tasks: Optional[List[TaskInstance]] = Field(default_factory=list, description="List of task instances")

class AirflowStatusResponse(BaseModel):
    """Response containing Airflow status information"""
    running_dags: List[DAGRun] = Field(..., description="List of running DAGs")
    queued_dags: List[DAGRun] = Field(..., description="List of queued DAGs")
    failed_dags: List[DAGRun] = Field(..., description="List of failed DAGs")
    success_dags: List[DAGRun] = Field(..., description="List of successful DAGs")

# Use environment variables for Airflow connection
AIRFLOW_HOST = os.getenv("HANS_ML_BACKEND_AIRFLOW_HOST", "hans-ml-backend-airflow-webserver")
AIRFLOW_PORT = os.getenv("HANS_ML_BACKEND_AIRFLOW_PORT", "8080")
AIRFLOW_BASE_URL = f"http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1"
DAG_ID = "hans_v1.0.3"
AUTH_HEADER = "Basic YWlyZmxvdzphaXJmbG93"  # base64 encoded "airflow:airflow"

def get_task_instances(dag_run_id: str) -> List[TaskInstance]:
    """Get task instances for a DAG run"""
    try:
        response = requests.get(
            f"{AIRFLOW_BASE_URL}/dags/{DAG_ID}/dagRuns/{dag_run_id}/taskInstances",
            headers={"Authorization": AUTH_HEADER}
        )
        response.raise_for_status()
        tasks = []
        for task in response.json()["task_instances"]:
            tasks.append(TaskInstance(
                duration=task.get("duration"),
                state=task.get("state"),
                task_id=task["task_id"],
                start_date=task.get("start_date"),
                end_date=task.get("end_date"),
                try_number=task["try_number"],
                max_tries=task["max_tries"],
                hostname=task["hostname"],
                operator=task["operator"]
            ))
        return tasks
    except Exception as e:
        print(f"Error fetching task instances: {e}")
        return []

def get_dag_runs() -> List[DAGRun]:
    """Get all DAG runs"""
    try:
        response = requests.get(
            f"{AIRFLOW_BASE_URL}/dags/{DAG_ID}/dagRuns",
            headers={"Authorization": AUTH_HEADER}
        )
        response.raise_for_status()
        dags = []
        for dag in response.json()["dag_runs"]:
            dags.append(DAGRun(
                dag_run_id=dag["dag_run_id"],
                state=dag["state"],
                start_date=dag["start_date"],
                end_date=dag.get("end_date"),
                conf=dag["conf"]
            ))
        return dags
    except Exception as e:
        print(f"Error fetching DAG runs: {e}")
        return []

@airflow_status_api_bp.get("/status", tags=[airflow_tag])
def get_status():
    """Get status of Airflow DAGs"""
    try:
        # Get all DAG runs
        all_dags = get_dag_runs()

        # For each DAG, get its task instances
        # for dag in all_dags:
        #     try:
        #         tasks = get_task_instances(dag.dag_run_id)
        #         dag.tasks = tasks
        #     except Exception as e:
        #         print(f"Error fetching tasks for DAG {dag.dag_run_id}: {e}")
        #         dag.tasks = []

        # Group DAGs by state
        running_dags = [dag.model_dump() for dag in all_dags if dag.state == "running"]
        queued_dags = [dag.model_dump() for dag in all_dags if dag.state == "queued"]
        failed_dags = [dag.model_dump() for dag in all_dags if dag.state == "failed"]
        success_dags = [dag.model_dump() for dag in all_dags if dag.state == "success"]

        # Return all DAGs grouped by state
        response_data = {
            "running_dags": running_dags,
            "queued_dags": queued_dags,
            "failed_dags": failed_dags,
            "success_dags": success_dags
        }

        return JsonResponse.create(response_data)

    except Exception as e:
        print(f"Error in get_status: {e}")
        return ErrorResponse.create_custom(str(e))
