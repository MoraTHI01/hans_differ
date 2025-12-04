#!/usr/bin/env python
"""Manage surveys """
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
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


survey_api_bp = APIBlueprint(
    "survey",
    __name__,
    abp_security=SecurityConfiguration().get_security(),
    abp_responses={"401": UnauthorizedResponse, "403": RefreshAuthenticationRequired},
)


upload_survay_tag = Tag(name="upload survey", description="Upload or change survey")


class UploadSurveyForm(BaseModel):
    """API template for submit survey form"""

    course_acronym: str = Field(None, description="Acronym for the course of the survey")
    survey_language: str = Field(
        None, description="Spoken language identifier for the survey, supported identifiers: 'en', 'de'"
    )
    survey_title: str = Field(None, description="Title of the survey")
    survey_url: str = Field(None, description="Url to the survey")
    survey_status: str = Field(None, description="Status of the survey, supported values: 'active', 'inactive'")


def find_first_matching_dict_index(input_dict, dict_list):
    """
    Search for entry in list of dicts, return first entry index
    """
    for i, d in enumerate(dict_list):
        if all(d[key] == input_dict[key] for key in input_dict):
            return i

    return None


def manage_survey(form: UploadSurveyForm):
    """Helper to manage channel meta survey data in mongodb"""
    print("Survey connect to database")

    # print(my_entry_str, sys.stderr)
    mongo_connector = connector_provider.get_metadb_connector()
    mongo_connector.connect()
    curr_course_acronym = str(form.course_acronym)

    # Update channel survey information
    res_channel = mongo_connector.get_channel_metadata_by_course_acronym(curr_course_acronym)
    if res_channel is None:
        return None
    if not "surveys" in res_channel:
        res_channel["surveys"] = []

    survey_item_input = {
        "type": "survey",
        "survey_language": str(form.survey_language),
        "survey_title": str(form.survey_title),
        "survey_url": str(form.survey_url),
    }
    index = find_first_matching_dict_index(survey_item_input, res_channel["surveys"])
    if index is None:
        print("Adding new survey entry to channel")
        survey_item_input["survey_status"] = str(form.survey_status)
        res_channel["surveys"].append(survey_item_input)
    else:
        print("Changing survey entry on channel")
        res_channel["surveys"][index]["survey_status"] = str(form.survey_status)

    print("Adding survey to channel")
    urn_input = "metadb:meta:post:id:" + res_channel["uuid"]
    (success, urn_result) = mongo_connector.put_object(urn_input, None, "application/json", res_channel)
    if success is False:
        print("Error adding survey to channel!")
        return None

    # Update media items survey information
    print("Adding survey to media items")
    res_media_items = mongo_connector.get_media_metadata_by_course_acronym(curr_course_acronym)
    if res_media_items is None:
        print("Error: Media items for survey not found! Empty res_media_items!")
        return None
    res_media_items_list = list(res_media_items)
    if res_media_items_list is None or len(res_media_items_list) < 1:
        print("Error: Media items for survey not found!")
        return None

    success = False
    for res_media_item in res_media_items_list:
        # print("Media item to add Survey:")
        # pprint(res_media_item)
        if not "surveys" in res_media_item:
            res_media_item["surveys"] = []

        survey_item_input = {
            "type": "survey",
            "survey_language": str(form.survey_language),
            "survey_title": str(form.survey_title),
            "survey_url": str(form.survey_url),
        }
        index = find_first_matching_dict_index(survey_item_input, res_media_item["surveys"])
        if index is None:
            print("Adding new survey entry to media item")
            survey_item_input["survey_status"] = str(form.survey_status)
            res_media_item["surveys"].append(survey_item_input)
        else:
            print("Changing survey entry on media item")
            res_media_item["surveys"][index]["survey_status"] = str(form.survey_status)

        print("Put media item update on database")
        urn_input = "metadb:meta:post:id:" + res_media_item["uuid"]
        (success, urn_result) = mongo_connector.put_object(urn_input, None, "application/json", res_media_item)
        if success is False:
            return None
    # mongo_connector.disconnect()
    if success is True:
        return urn_result
    else:
        return None


# REQUESTS FROM FRONTEND


@survey_api_bp.post("/survey", tags=[upload_survay_tag])
@jwt_required()
def upload_survey(form: UploadSurveyForm):
    """Upload survey from vue to backend"""
    # Protect api to only allow uploading for admin user
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if not sec_meta_data.check_user_has_roles(["admin"]):
        return ErrorForbidden.create()

    print("Survey")

    # Store meta data in mongodb
    meta_urn = manage_survey(form)
    if meta_urn is None:
        return ErrorResponse.create_custom("Error while uploading survey")

    return JsonResponse.create({"success": True})
