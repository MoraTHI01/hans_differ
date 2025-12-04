#!/usr/bin/env python
"""Publish data on backend, mainly used by ml-backend """
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import json
from datetime import datetime

from flask_jwt_extended import jwt_required
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field
from flask_pydantic import validate
from typing import Optional

from connectors.connector_provider import connector_provider

from api.modules.responses import ErrorForbidden, UnauthorizedResponse, RefreshAuthenticationRequired
from api.modules.responses import ErrorResponse, JsonResponse
from api.modules.security import SecurityConfiguration, SecurityMetaData


publish_api_bp = APIBlueprint(
    "publish",
    __name__,
    abp_security=SecurityConfiguration().get_security(),
    abp_responses={"401": UnauthorizedResponse, "403": RefreshAuthenticationRequired},
)


publish_tag = Tag(
    name="Publish media item", description="Publish single media item from airflow dag hans_v1 into backend"
)
publish_update_tag = Tag(
    name="Publish update of media item",
    description="Publish update of a single media item from airflow dag chapter_sum_v1 into backend",
)


class PublishForm(BaseModel):
    """API template for publishing files on backend"""

    uuid: str = Field(None, description="UUID for publishing")
    data: str = Field(None, description="JSON meta data for publishing")
    from_package: bool = Field(False, description="Use meta data from package")
    editing_progress: Optional[int] = Field(False, description="Editing progress to be set")


# REQUESTS FROM ML-BACKEND


# TODO: use security mechanism for ml-backend to auth e.g jwt, see security.py
@publish_api_bp.post("/publish", tags=[publish_tag])
@jwt_required()
@validate()
def publish(body: PublishForm):
    """Publish processed media files from ml-backend dag hans_v1 to backend"""
    # Protect api to only allow publishing for ml-backend user
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if not sec_meta_data.check_user_has_roles(["ml-backend"]) or sec_meta_data.is_sso_user is True:
        return ErrorForbidden.create()

    print("/publish: Received uuid:")
    print(body.uuid)
    print("/publish: Received data:")
    print(body.data)
    received_meta_data = json.loads(body.data)

    mongo_connector = connector_provider.get_metadb_connector()
    mongo_connector.connect()

    urn_meta_data = f"metadb:meta:post:id:{body.uuid}"
    curr_meta_data = mongo_connector.get_metadata(urn_meta_data)

    if curr_meta_data is None:
        (success, urn_result) = mongo_connector.put_object(urn_meta_data, None, "application/json", received_meta_data)
        if success is False:
            return ErrorResponse.create_custom("Error while fetching meta data during publishing!")
        curr_meta_data = mongo_connector.get_metadata(urn_meta_data)

    # Update overall_step of media to notify frontend about successful ml-backend processing
    # EDITING indicated the user can start with the next step and edit the video
    if not "state" in curr_meta_data:
        curr_meta_data["state"] = {}
        curr_meta_data["state"]["published"] = False
        curr_meta_data["state"]["listed"] = False
    curr_meta_data["state"]["overall_step"] = "EDITING"
    curr_meta_data["state"]["editing_progress"] = 0

    if body.from_package is False:
        # Add only previously not existing keys from received json data
        # See upload.py:upload_meta_data
        patch_skip_key_list = ["title", "language", "description", "permissions", "licenses"]
        for key in received_meta_data:
            if not key in patch_skip_key_list:
                # thumbnails is a dict!
                if isinstance(received_meta_data[key], dict):
                    if not key in curr_meta_data:
                        curr_meta_data[key] = {}
                    for subkey in received_meta_data[key]:
                        curr_meta_data[key][subkey] = received_meta_data[key][subkey]
                else:
                    curr_meta_data[key] = received_meta_data[key]

    curr_meta_data_str = json.dumps(curr_meta_data)

    print("Patched meta data: " + curr_meta_data_str)

    # Update in mongodb
    (success, urn_result) = mongo_connector.put_object(urn_meta_data, None, "application/json", curr_meta_data)
    # mongo_connector.disconnect()
    if success is False:
        return ErrorResponse.create_custom("Error while updating meta data during publishing!")

    # Create dummy channel package after successful publishing
    try:
        import requests
        from flask import request

        # Get a fresh admin JWT token by logging in
        import base64

        # Admin credentials
        credentials = 'glurak25@thi.de:SGFt-3bH3Y!D@@'
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        # Login to get admin JWT token
        login_response = requests.get('http://localhost:7087/api/login',
                                    headers={'Authorization': f'Basic {encoded_credentials}'})

        if login_response.status_code != 200:
            print(f"Failed to login as admin. Status: {login_response.status_code}")
            raise Exception("Failed to login as admin")

        login_data = login_response.json()
        access_token = login_data.get('access_token')

        if not access_token:
            print("No access token in login response")
            raise Exception("No access token received")

        # Create FormData like the Vue frontend does
        form_data = {
            'language': 'en',
            'course': 'dummy',
            'course_acronym': 'dm',
            'semester': 'Dummy Semester 2024',
            'lecturer': 'Dummy Lecturer',
            'faculty': 'Dummy Faculty',
            'faculty_acronym': 'DF',
            'faculty_color': '#2F9B92',
            'university': 'Technische Hochschule Ingolstadt',
            'university_acronym': 'THI',
            'license': 'OER',
            'license_url': 'https://open-educational-resources.de',
            'tags': 'dm',
            'thumbnails_lecturer': 'http://localhost/avatars/avatar-m-00001.png',
            'archive_channel_content': 'true'
        }

        # Debug: print the data being sent
        print(f"Sending form data: {form_data}")

        # Make API call to createChannel endpoint through Apache proxy using form data
        response = requests.post('http://localhost:7087/api/createChannel',
                                headers={'Authorization': f'Bearer {access_token}'},
                                data=form_data)

        if response.status_code == 200:
            print("Successfully created dummy channel via API call")
            print(f"Response: {response.text}")
        else:
            print(f"Failed to create dummy channel via API call. Status: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"Error creating dummy channel package via API: {e}")
        # Don't fail the main publish operation if dummy channel creation fails

    return JsonResponse.create({"result": urn_result})


# TODO: use security mechanism for ml-backend to auth e.g jwt, see security.py
@publish_api_bp.post("/publish-update", tags=[publish_update_tag])
@jwt_required()
@validate()
def publish_update(body: PublishForm):
    """Publish updated media file from ml-backend dag chapter_sum_v1 to backend"""
    # Protect api to only allow publishing for ml-backend user
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if not sec_meta_data.check_user_has_roles(["ml-backend"]) or sec_meta_data.is_sso_user is True:
        return ErrorForbidden.create()

    print("/publish-update: Received uuid:")
    print(body.uuid)
    print("/publish-update: Received data:")
    print(body.data)

    now = datetime.now()
    time_updated = now.strftime("%m_%d_%Y_%H_%M_%S")

    received_meta_data = json.loads(body.data)

    mongo_connector = connector_provider.get_metadb_connector()
    mongo_connector.connect()

    urn_meta_data = f"metadb:meta:post:id:{body.uuid}"
    curr_meta_data = mongo_connector.get_metadata(urn_meta_data)

    # Update overall_step of media to notify frontend about successful ml-backend processing
    # EDITING indicated the user can start with the next step and edit the video
    if not "state" in curr_meta_data:
        curr_meta_data["state"] = {}
        curr_meta_data["state"]["published"] = False
        curr_meta_data["state"]["listed"] = False
    curr_meta_data["state"]["overall_step"] = "EDITING"
    # Editing step is set by backend airflow graph depending on executed graph
    curr_meta_data["state"]["editing_progress"] = body.editing_progress

    if body.from_package is False:
        # Add only previously not existing keys from received json data
        # See upload.py:upload_meta_data
        patch_skip_key_list = ["title", "language", "description", "permissions", "licenses"]
        history_enabled_key_list = [
            "topic_result_raw",
            "topic_result_en",
            "topic_result_de",
            "questionnaire_result_en",
            "questionnaire_result_de",
            "airflow_info",
        ]
        for key in received_meta_data:
            if not key in patch_skip_key_list:
                # thumbnails is a dict!
                if isinstance(received_meta_data[key], dict):
                    if not key in curr_meta_data:
                        curr_meta_data[key] = {}
                    for subkey in received_meta_data[key]:
                        curr_meta_data[key][subkey] = received_meta_data[key][subkey]
                else:
                    if key in history_enabled_key_list:
                        curr_history_key = key + "_history"
                        if not curr_history_key in curr_meta_data:
                            curr_meta_data[curr_history_key] = []
                        if key in curr_meta_data:
                            curr_meta_data[curr_history_key].append(
                                {"datetime": time_updated, "key": key, "value": curr_meta_data[key]}
                            )
                    curr_meta_data[key] = received_meta_data[key]

    curr_meta_data_str = json.dumps(curr_meta_data)

    print("Patched meta data: " + curr_meta_data_str)

    # Update in mongodb
    (success, urn_result) = mongo_connector.put_object(urn_meta_data, None, "application/json", curr_meta_data)
    # mongo_connector.disconnect()
    if success is False:
        return ErrorResponse.create_custom("Error while updating meta data during publishing!")

    return JsonResponse.create({"result": urn_result})
