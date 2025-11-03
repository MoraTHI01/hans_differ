#!/usr/bin/env python
"""Query channels or media items """
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import json

from flask_jwt_extended import jwt_required
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field

from api.modules.metadata_provider import metadata_provider
from api.modules.responses import ErrorForbidden, UnauthorizedResponse, RefreshAuthenticationRequired
from api.modules.responses import ErrorResponse, JsonResponse
from api.modules.security import SecurityConfiguration, SecurityMetaData
from flask_jwt_extended import jwt_required


query_api_bp = APIBlueprint(
    "query",
    __name__,
    abp_security=SecurityConfiguration().get_security(),
    abp_responses={"401": UnauthorizedResponse, "403": RefreshAuthenticationRequired},
)


search_tag = Tag(name="search media", description="Provides found media content")


class SearchQuery(BaseModel):
    """API template for searching media items"""

    q: str = Field(None, description="Query text for the search engine")
    f: str = Field(None, description="Query field for the search engine, * = Search in all fields")


recent_tag = Tag(name="recent media", description="Provides recent media content")


class RecentQuery(BaseModel):
    """API template for retrieving recent media items"""

    n: int = Field(None, description="Number of media items to provide")


channels_tag = Tag(name="available channels", description="Provides all available channels")


class ChannelsQuery(BaseModel):
    """API template for retrieving channel items"""

    n: int = Field(None, description="Number of channel items to provide")


# REQUESTS FROM FRONTEND
def prep_querystrings_tolist(query):
    return query.replace("undefined", "").replace(",", " ").split()


@query_api_bp.get("/search", tags=[search_tag])
@jwt_required()
def search(query: SearchQuery):
    """Search for media in searchengine and provide found media items to vue"""
    # Protect api from access of airflow ml-backend users
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    query_prep = " ".join(prep_querystrings_tolist(query.q))
    fields_prep = prep_querystrings_tolist(query.f)
    print("Search")
    # print("SearchQuery:")
    # print(query_prep)
    # print("SearchFields:")
    # print(fields_prep)
    search_credentials = {
        "university": sec_meta_data.university,
        "faculty": sec_meta_data.faculty,
        "course_acronym": sec_meta_data.course,
    }
    if (
        sec_meta_data.role.lower() == "admin"
        or sec_meta_data.role.lower() == "developer"
        or sec_meta_data.idp == "oidc_identity_provider"
    ):
        search_credentials["faculty"] = "*"
        search_credentials["course_acronym"] = "*"
    search_result = metadata_provider.search_lectures_standard(
        query=query_prep, search_credentials=search_credentials, fields=fields_prep
    )
    if search_result is None:
        return JsonResponse.create({})
    search_result_uuid_list = [res[0] for res in search_result]
    meta_data_list = metadata_provider.get_metadata_for_uuid_list(search_result_uuid_list)
    if meta_data_list is None or len(meta_data_list) < 1:
        return JsonResponse.create({})
    # #print("Search:")
    # #print(json.dumps(meta_data_list, indent=4, default=str))
    meta_data_list_filtered = sec_meta_data.filter_media_results(meta_data_list)
    # Add search score and search highlights to search result before return
    for elID in range(len(meta_data_list_filtered)):
        elUUID = meta_data_list_filtered[elID]["uuid"]
        score = 0
        highlights = {}
        if elUUID in search_result_uuid_list:
            searchResID = search_result_uuid_list.index(elUUID)
            if len(search_result[searchResID]) >= 3:
                score = search_result[searchResID][1]
                highlights = search_result[searchResID][2]
        meta_data_list_filtered[elID]["search_score"] = score
        meta_data_list_filtered[elID]["search_highlights"] = highlights
    # # Add search score and search highlights to search result before return
    # # TODO: Fix bug here the lists are not of same size e.g.:
    # Solved:
    #   HAnS videos were added twice in sec_meta_data.filter_media_results(meta_data_list) due to filter(HAnS) and filter(University) when user was admin of THN
    # # [wsgi:error] [pid 11:tid 281472826597760] [remote 172.18.0.5:48430] ### meta_data_filtered_length: 4
    # # [wsgi:error] [pid 11:tid 281472826597760] [remote 172.18.0.5:48430] ### search_result_length: 2
    # # [wsgi:error] [pid 11:tid 281472826597760] [remote 172.18.0.5:48430] ### num_search_results: 3
    # # [wsgi:error] [pid 11:tid 281472826597760] [remote 172.18.0.5:48430] ### num_search_results: 3
    # meta_data_filtered_length = len(meta_data_list_filtered)
    # print(f"### meta_data_filtered_length: {meta_data_filtered_length}")
    # search_result_length = len(search_result)
    # print(f"### search_result_length: {search_result_length}")
    # for i in range(0,len(meta_data_list_filtered)):
    #     if i < search_result_length:
    #         num_search_results = len(search_result[i])
    #         print(f"### num_search_results: {num_search_results}")
    #         if num_search_results >= 3:
    #             meta_data_list_filtered[i]['search_score'] = search_result[i][1]
    #             meta_data_list_filtered[i]['search_highlights'] = search_result[i][2]
    # print("SearchResult:")
    # print(json.dumps(meta_data_list_filtered, indent=4, default=str))
    return JsonResponse.create(meta_data_list_filtered)


@query_api_bp.get("/recent", tags=[recent_tag])
@jwt_required()
def recent(query: RecentQuery):
    """Provide recent media items to vue"""
    # Protect api from access of airflow ml-backend users
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    print("Recent")
    # print("RecentQuery:")
    # print(query.n)
    search_credentials = {
        "university": sec_meta_data.university,
        "faculty": sec_meta_data.faculty,
        "course_acronym": sec_meta_data.course,
        "lecturer": "*",
    }
    if (
        sec_meta_data.role.lower() == "admin"
        or sec_meta_data.role.lower() == "developer"
        or sec_meta_data.idp == "oidc_identity_provider"
    ):
        search_credentials["faculty"] = "*"
        search_credentials["course_acronym"] = "*"
    search_recent_result = metadata_provider.search_recent_lectures(
        search_credentials=search_credentials, amount=query.n
    )
    if search_recent_result is None:
        return JsonResponse.create({})
    search_result_uuid_list = [res[0] for res in search_recent_result]
    meta_data_list = metadata_provider.get_metadata_for_uuid_list(search_result_uuid_list)
    if meta_data_list is None or len(meta_data_list) < 1:
        return JsonResponse.create({})
    # print("Recent:")
    # print(json.dumps(meta_data_list, indent=4, default=str))
    meta_data_list_filtered = sec_meta_data.filter_media_results(meta_data_list)
    # only show published and listed items
    meta_data_list_filtered = [
        item
        for item in meta_data_list_filtered
        if item["state"]["published"] is True and item["state"]["listed"] is True
    ]
    # print("RecentResult:")
    # print(json.dumps(meta_data_list_filtered, indent=4, default=str))
    return JsonResponse.create(meta_data_list_filtered)


@query_api_bp.get("/channels", tags=[channels_tag])
@jwt_required()
def channels(query: ChannelsQuery):
    """Provide channel items to vue"""
    # Protect api from access of airflow ml-backend users
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    if sec_meta_data.check_user_has_roles(["ml-backend"]):
        return ErrorForbidden.create()
    print("Channels")
    # print("ChannelsQuery:")
    # print(query.n)
    search_channels_result = metadata_provider.search_channels(amount=query.n)
    if search_channels_result is None:
        return JsonResponse.create({})
    # print("Channels:")
    # print(json.dumps(search_channels_result, indent=4, default=str))
    search_channels_result_filtered = sec_meta_data.filter_channel_results(search_channels_result)
    # print("ChannelsResult:")
    # print(json.dumps(search_channels_result_filtered, indent=4, default=str))
    return JsonResponse.create(search_channels_result_filtered)
