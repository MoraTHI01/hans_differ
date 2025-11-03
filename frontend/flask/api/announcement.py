#!/usr/bin/env python
"""Manage announcements """
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2024, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import io
import json
from datetime import datetime
from uuid import uuid4
from typing import List
from pprint import pprint

from flask_jwt_extended import jwt_required
from flask_openapi3 import APIBlueprint, Tag, FileStorage
from pydantic import BaseModel, Field, ConfigDict
from datetime import date

from api.modules.connectors.connector_provider import connector_provider
from api.modules.responses import ErrorForbidden, UnauthorizedResponse, RefreshAuthenticationRequired
from api.modules.responses import ErrorResponse, JsonResponse
from api.modules.security import SecurityConfiguration, SecurityMetaData


announcement_api_bp = APIBlueprint(
    "announcement",
    __name__,
    abp_security=SecurityConfiguration().get_security(),
    abp_responses={"401": UnauthorizedResponse, "403": RefreshAuthenticationRequired},
)


announcement_tag = Tag(name="upload announcement", description="Upload or change announcement")
get_announcement_tag = Tag(name="get announcement", description="Get all announcements")


class UploadAnnouncementForm(BaseModel):
    """API template for submit announcement form"""

    start_date: str = Field(None, description="The start date in the format YYYY-MM-DD")
    end_date: str = Field(None, description="The end date in the format YYYY-MM-DD")
    uuid: str = Field(None, description="Unique identifier of the announcement")
    status: str = Field(None, description="Status of the announcement, supported values: 'active', 'inactive'")
    title_de: str = Field(None, description="Title of the announcement")
    text_de: str = Field(None, description="Text of the announcement")
    title_en: str = Field(None, description="Title of the announcement")
    text_en: str = Field(None, description="Text of the announcement")


# REQUESTS FROM FRONTEND


@announcement_api_bp.post("/announcement", tags=[announcement_tag])
@jwt_required()
def upload_announcement(form: UploadAnnouncementForm):
    """Upload announcement from vue to backend"""
    # Protect api to only allow uploading for admin user
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if not sec_meta_data.check_user_has_roles(["admin"]):
        return ErrorForbidden.create()

    # Store meta data in mongodb
    mongo_connector = connector_provider.get_metadb_connector()
    mongo_connector.connect()

    announcement = form.model_dump()
    announcement["type"] = "announcement"

    print("Adding announcement")
    print(announcement)

    urn_input = "metadb:meta:post:id:" + announcement["uuid"]
    (success, urn_result) = mongo_connector.put_object(urn_input, None, "application/json", announcement)
    # mongo_connector.disconnect()
    if success is False:
        return ErrorResponse.create_custom("Error while uploading announcement")

    return JsonResponse.create({"success": success})


@announcement_api_bp.get("/announcement", tags=[get_announcement_tag])
@jwt_required()
def get_announcement():
    """Get announcements"""

    # Store meta data in mongodb
    mongo_connector = connector_provider.get_metadb_connector()
    mongo_connector.connect()

    # Get the current date
    current_date = datetime.now()
    # Format the date as YYYY-MM-DD
    date_string = current_date.strftime("%Y-%m-%d")
    curr_date = datetime.strptime(date_string, "%Y-%m-%d")

    announcements = mongo_connector.get_metadata_by_type("announcement")
    res = {"result": []}
    for an in announcements:
        if an["status"].lower() == "active":
            start_date = datetime.strptime(an["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(an["end_date"], "%Y-%m-%d")
            if curr_date >= start_date and curr_date <= end_date:
                res["result"].append(an)
    return JsonResponse.create_json_string_response(json.dumps(res))
