#!/usr/bin/env python
"""Metadata API"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"

from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from api.modules.responses import ErrorResponse, JsonResponse
from api.modules.metadata_provider import metadata_provider

metadata_bp = APIBlueprint(
    "metadata",
    __name__,
    abp_responses={"401": ErrorResponse, "403": ErrorResponse},
)

metadata_tag = Tag(name="metadata", description="Provides metadata for DAG runs")

class DagRunId(BaseModel):
    """DAG run ID parameter"""
    dag_run_id: str = Field(..., description="ID of the DAG run")

@metadata_bp.get("/metadata/<dag_run_id>", tags=[metadata_tag])
def get_metadata(path: DagRunId):
    """Get metadata for a specific DAG run"""
    try:
        dag_run_id = path.dag_run_id
        # First try to get metadata directly using the DAG run ID
        metadata = metadata_provider.get_media_metadata(dag_run_id)

        if not metadata:
            return ErrorResponse.create_custom(f"Metadata not found for DAG run ID: {dag_run_id}")

        return JsonResponse.create(metadata)

    except Exception as e:
        print(f"Error fetching metadata for DAG {dag_run_id}: {e}")
        return ErrorResponse.create_custom(str(e))
