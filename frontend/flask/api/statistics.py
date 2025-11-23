#!/usr/bin/env python
"""Provide statistics """
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2025, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import io
import json
from uuid import uuid4
from typing import List
from pprint import pprint

from flask_jwt_extended import jwt_required
from flask_openapi3 import APIBlueprint, Tag, FileStorage
from pydantic import BaseModel, Field

from connectors.connector_provider import connector_provider

from api.modules.responses import ErrorForbidden, UnauthorizedResponse, RefreshAuthenticationRequired
from api.modules.responses import ErrorResponse, JsonResponse
from api.modules.security import SecurityConfiguration, SecurityMetaData


statistics_api_bp = APIBlueprint(
    "statistics",
    __name__,
    abp_security=SecurityConfiguration().get_security(),
    abp_responses={"401": UnauthorizedResponse, "403": RefreshAuthenticationRequired},
)


statistics_tag = Tag(name="provide statistics", description="Provide statistics")


# REQUESTS FROM FRONTEND


@statistics_api_bp.get("/stats", tags=[statistics_tag])
@jwt_required()
def query_statistics():
    """Query statistics"""
    # Protect api to only allow uploading for admin user
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if sec_meta_data.is_sso_user is True:
        return ErrorForbidden.create()

    print("Statistics")
    # sec_meta_data._log_identity(True)

    metadb_connector = connector_provider.get_metadb_connector()
    metadb_connector.connect()
    if sec_meta_data.check_user_has_roles(["admin"]):
        count_channels = metadb_connector.count_metadata_by_type("channel")
        count_media = metadb_connector.count_metadata_by_type("media")
        count_media_published = metadb_connector.count_metadata_by_type("media", [{"state.published": True}])
        count_media_listed = metadb_connector.count_metadata_by_type(
            "media", [{"state.published": True}, {"state.listed": True}]
        )
    elif sec_meta_data.check_user_has_roles(["developer"]):
        count_channels = metadb_connector.count_metadata_by_type(
            "channel", [{"university": {"$regex": f"^{sec_meta_data.university}$", "$options": "i"}}]
        )
        count_media = metadb_connector.count_metadata_by_type(
            "media", [{"description.university": {"$regex": f"^{sec_meta_data.university}$", "$options": "i"}}]
        )
        count_media_published = metadb_connector.count_metadata_by_type(
            "media",
            [
                {"description.university": {"$regex": f"^{sec_meta_data.university}$", "$options": "i"}},
                {"state.published": True},
            ],
        )
        count_media_listed = metadb_connector.count_metadata_by_type(
            "media",
            [
                {"description.university": {"$regex": f"^{sec_meta_data.university}$", "$options": "i"}},
                {"state.published": True},
                {"state.listed": True},
            ],
        )
    else:
        count_channels = metadb_connector.count_metadata_by_type(
            "channel", [{"course_acronym": sec_meta_data.course.upper()}]
        )
        count_media = metadb_connector.count_metadata_by_type(
            "media", [{"description.course_acronym": sec_meta_data.course.upper()}]
        )
        count_media_published = metadb_connector.count_metadata_by_type(
            "media", [{"description.course_acronym": sec_meta_data.course.upper()}, {"state.published": True}]
        )
        count_media_listed = metadb_connector.count_metadata_by_type(
            "media",
            [
                {"description.course_acronym": sec_meta_data.course.upper()},
                {"state.published": True},
                {"state.listed": True},
            ],
        )
    result = {
        "count_channels": count_channels,
        "count_media": count_media,
        "count_media_published": count_media_published,
        "count_media_listed": count_media_listed,
    }

    return JsonResponse.create(result)
