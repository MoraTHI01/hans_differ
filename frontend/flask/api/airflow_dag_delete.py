import os
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field
from api.modules.responses import ErrorResponse, JsonResponse
import requests

# Use environment variables for Airflow connection
AIRFLOW_HOST = os.getenv("HANS_ML_BACKEND_AIRFLOW_HOST", "hans-ml-backend-airflow-webserver")
AIRFLOW_PORT = os.getenv("HANS_ML_BACKEND_AIRFLOW_PORT", "8080")
AIRFLOW_BASE_URL = f"http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1"
DAG_ID = "hans_v1.0.3"
AUTH_HEADER = "Basic YWlyZmxvdzphaXJmbG93"  # base64 encoded "airflow:airflow"

dag_delete_api_bp = APIBlueprint(
    "airflow_dag_delete",
    __name__,
    abp_responses={"401": ErrorResponse, "403": ErrorResponse},
)

dag_delete_tag = Tag(name="airflow dag delete", description="Delete Airflow DAG runs")

class PathDagRunId(BaseModel):
    dag_run_id: str = Field(..., description="The ID of the DAG run to delete")

@dag_delete_api_bp.delete("/<string:dag_run_id>", tags=[dag_delete_tag])
def delete_dag_run(path: PathDagRunId):
    """Delete a DAG run by ID"""
    try:
        dag_run_id = path.dag_run_id

        response = requests.delete(
            f"{AIRFLOW_BASE_URL}/dags/{DAG_ID}/dagRuns/{dag_run_id}",
            headers={"Authorization": AUTH_HEADER}
        )
        if response.status_code == 204:
            return JsonResponse.create({"message": "DAG run deleted successfully"})
        else:
            return ErrorResponse.create_custom(f"Failed to delete DAG run: {response.text}", status_code=response.status_code)
    except Exception as e:
        print(f"Error deleting DAG run: {e}")
        return ErrorResponse.create_custom(str(e))
