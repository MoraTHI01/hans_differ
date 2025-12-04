#!/usr/bin/env python
"""The security configuration for the API """
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import requests
import json
from urllib.parse import unquote

from flask import current_app

# https://luolingchun.github.io/flask-openapi3/Example/
# https://github.com/luolingchun/flask-api-demo/blob/master/src/app/utils/jwt_tools.py
from flask_jwt_extended import get_jwt_identity

from connectors.connector_provider import connector_provider


class SecurityConfiguration:
    """Security configuration for flask"""

    def __init__(self):
        """Initialize security configuration"""
        self.security_schemes = {"jwt": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}}
        self.security = [{"jwt": []}]

    def get_security_schemes(self):
        """Get configured security schemes"""
        return self.security_schemes

    def get_security(self):
        """Get configured security methods"""
        return self.security


class SecurityMetaData:
    """Meta data used e.g. to filter query results"""

    def __init__(
        self, i_subject_id, i_username, i_mail, i_language, i_faculty, i_university, i_course, i_role, i_idp, i_id_token
    ):
        """Init meta data"""
        self.subject_id = unquote(i_subject_id, encoding=None)
        self.username = unquote(i_username, encoding=None)
        self.mail = unquote(i_mail, encoding=None)
        self.language = i_language
        self.faculty = unquote(i_faculty, encoding=None).casefold().lower()
        self.university = unquote(i_university, encoding=None).casefold().lower()
        self.course = unquote(i_course, encoding=None).casefold().lower()
        self.role = i_role
        self.idp = i_idp
        self.id_token = i_id_token
        self.is_sso_user = self.idp != "simple_identity_provider"

    @staticmethod
    def gen_meta_data_from_identity(verbose=False):
        """Get filter dict, e.g. for query. requires @jwt_required() decorator!"""
        identity = get_jwt_identity()
        if verbose is True:
            print("current identity:")
            print(identity)
        subject_id = identity.get("id")
        username = identity.get("username")
        mail = identity.get("mail")
        lang = identity.get("preferedLanguage")
        faculty = identity.get("faculty")
        university = identity.get("university")
        course = identity.get("course")
        role = identity.get("role")
        idp = identity.get("idp")
        id_token = identity.get("id_token")
        return SecurityMetaData(subject_id, username, mail, lang, faculty, university, course, role, idp, id_token)

    def _log_identity(self, verbose=False):
        """
        Log current identity on stdout
        """
        print("Identity")
        if verbose is True:
            print(self.subject_id)
            print(self.username)
            print(self.mail)
        print(self.language)
        print(self.faculty)
        print(self.university)
        print(self.course)
        print(self.role)
        print(self.idp)
        print(self.id_token)

    def _filter(self, input_list, key_val_list, key, subkey=None, verbose=False):
        """
        Filter a query result using identity meta data

        :param list input_list: list of dicts containing meta data
        :param list key_val_list: List of dict item key values in lowercase
        :param str key: Key to a dict which is part of input_list
        :param str sub_key: Optional sub key of key dict, default: None

        :return list: Filtered input_list
        """
        if verbose is True:
            print("Filter list:")
            print(json.dumps(input_list, indent=4, default=str))
            print("Compare key: " + key)
            if subkey is not None:
                print("Compare sub key: " + subkey)
            print("Compare with values:")
            print(key_val_list)
        if subkey is None:
            return list(filter(lambda d: d[key].casefold().lower() in key_val_list, input_list))
        else:
            return list(filter(lambda d: d[key][subkey].casefold().lower() in key_val_list, input_list))

    def final_filter_verify_restricted(self, result_list):
        """
        Filter a filtered query result list to only contain access granted restricted media

        :param list result_list: query result list of filter_media_results or channel results

        :return list: Filtered query result list with only access granted items
        """
        print("FilterVerifyRestricted")
        restricted_items = list(filter(lambda d: d["lms_gated_access"] is True, result_list))
        print(f"CheckAccessForRestrictedItems: {restricted_items}")
        # Remove all items that are restricted and not allowed to be accessed
        for rel in restricted_items:
            if rel["lms_gated_access_details"]["type"] == "moodle":
                course_id = rel["lms_gated_access_details"]["course_id"]
                if not self.verify_protected_access(course_id) and self.role.lower() != "admin":
                    print("Removing restricted item!")
                    result_list.remove(rel)
        print(f"FilterVerifyRestricted: {result_list}")
        return result_list

    def final_filter_verify_published(self, result_list, verify_published=True, verify_restricted=True):
        """
        Filter a filtered query result list to only contain published media

        :param list result_list: query result list of filter_media_results

        :return list: Filtered query result list with only published items
        """
        if verify_published is True:
            # print("FilterVerifyPublished")
            if not self.role == "lecturer" and self.idp == "simple_identity_provider":
                # print("FilterVerifyPublished:NotLecturer")
                # gen list of media items which are not published
                rem_items = list(
                    filter(
                        lambda d: d["state"]["published"] is False and d["state"]["overall_step"] == "FINISHED",
                        result_list,
                    )
                )
                # print(f"FilterVerifyPublishedRemoveItems: {rem_items}")
                # Remove all items that are allready in default_items to prevent duplicates
                for el in rem_items:
                    result_list.remove(el)
        # print(f"FilterVerifyPublishedResult: {result_list}")
        if verify_restricted is True:
            return self.final_filter_verify_restricted(result_list)
        else:
            return result_list

    def filter_media_results(self, media_query_result_list, verify_published=True):
        """
        Filter a media result query using identity meta data

        :param list media_query_result_list: list of dicts containing query meta data

        :return list: Filtered query result list
        """
        if media_query_result_list is None or len(media_query_result_list) < 1 or not media_query_result_list[0]:
            return media_query_result_list

        # List of items available for all users
        default_items = self._filter(media_query_result_list, ["hans"], "description", "course_acronym")

        # Remove all items that are allready in default_items to prevent duplicates
        for el in default_items:
            media_query_result_list.remove(el)

        # Filter items by university
        list_university = self._filter(media_query_result_list, [self.university.lower()], "description", "university")
        # Prevent admins and developers from filtering faculty
        # Admins will get a university item list
        if self.role.lower() == "admin" or self.role.lower() == "developer" or self.idp == "oidc_identity_provider":
            return self.final_filter_verify_published(
                default_items + list_university, verify_published=verify_published
            )
        # Filter university items by faculty
        list_faculty = self._filter(list_university, [self.faculty.lower()], "description", "faculty")
        # Prevent filtering course if wildcard set
        if self.course == "*":
            return self.final_filter_verify_published(default_items + list_faculty, verify_published=verify_published)
        # Filter faculty items by course acronym id
        list_course = self._filter(list_faculty, [self.course.lower()], "description", "course_acronym")
        return self.final_filter_verify_published(default_items + list_course, verify_published=verify_published)

    def filter_channel_results(self, channel_results_list):
        """
        Filter a channel results using identity meta data

        :param list channel_results_list: list of dicts containing channel meta data

        :return list: Filtered query result list
        """
        if channel_results_list is None or len(channel_results_list) < 1:
            return channel_results_list

        # List of items available for all users
        default_items = self._filter(channel_results_list, ["hans"], "course_acronym")
        # Filter items by university
        list_university = self._filter(channel_results_list, [self.university.lower()], "university")
        # Prevent admins and developers from filtering faculty
        # Admins will get a university item list
        if self.role.lower() == "admin" or self.role.lower() == "developer" or self.idp == "oidc_identity_provider":
            return self.final_filter_verify_restricted(default_items + list_university)
        # Filter university items by faculty
        list_faculty = self._filter(list_university, [self.faculty.lower()], "faculty")
        # Prevent filtering course if wildcard set
        if self.course == "*":
            return self.final_filter_verify_restricted(default_items + list_faculty)
        # Filter faculty items by course acronym id
        list_course = self._filter(list_faculty, [self.course.lower()], "course_acronym")
        return self.final_filter_verify_restricted(default_items + list_course)

    def check_user_has_roles(self, input_roles_list):
        """
        Check the role of the current user

        :param list input_roles_list: List of valid roles in lowercase

        :return bool: True if the user has the role, False otherwise
        """
        if self.role.lower() in input_roles_list:
            return True
        else:
            return False

    def check_identity_is_valid(self):
        """
        Check if current identity is in identities list
        """
        # print("check_identity_is_valid")
        if self.idp == "simple_identity_provider":
            idp = current_app.config["MULTIPASS_IDENTITY_PROVIDERS"]["simple_identity_provider"]
            identities = idp["identities"]
            user_data = identities[self.username]
            if user_data["subject-id"] == self.subject_id:
                print("Static identity is valid")
                return True
            else:
                print("Static identity is not valid!")
                return False
        else:
            mongo_connector = connector_provider.get_metadb_connector()
            mongo_connector.connect()
            urn_meta_data = f"metadb:meta:post:identity:{self.subject_id}"
            curr_meta_data = mongo_connector.get_metadata(urn_meta_data)
            if curr_meta_data is not None:
                print("OIDC identity is valid")
                return True
            else:
                print("OIDC identity is not valid!")
                return False

    def verify_protected_access(self, course_id="2"):
        """
        Check if current identity is allowed for access
        :return bool True if allowed, False otherwise
        """
        # print("check_identity_is_valid")
        idp = current_app.config["MULTIPASS_IDENTITY_PROVIDERS"]["oidc_identity_provider"]
        # {'type': 'moodle', 'url': 'http://localhost/webservice/rest/server.php', 'wstoken': '0815'}
        restricted_permission_provider = idp["restricted_permission_provider"]
        url = restricted_permission_provider["url"]
        wstoken = restricted_permission_provider["wstoken"]

        # Define the parameters for the request
        params = {
            "wstoken": wstoken,
            "wsfunction": "core_user_get_users_by_field",
            "moodlewsrestformat": "json",
            "field": "email",
            "values[0]": self.mail,
        }
        user_id = -1
        try:
            # Make the POST request to the Moodle API
            response = requests.post(url, data=params)
            # Check if the request was successful
            if response.status_code == 200:
                user_data = response.json()
                if user_data:
                    # print(user_data)
                    if "exception" in user_data:
                        ex = response["exception"]
                        print(f"Error: {response.status_code} - {ex}")
                    else:
                        user_id = user_data[0].get("id")
                        print(f"User ID: {user_id}")
                else:
                    print("No user found with the provided email.")
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except:
            print("Error during connection to LMS. Trying second attempt.")
            try:
                # Make the POST request to the Moodle API
                response = requests.post(url, data=params)
                # Check if the request was successful
                if response.status_code == 200:
                    user_data = response.json()
                    if user_data:
                        # print(user_data)
                        if "exception" in user_data:
                            ex = response["exception"]
                            print(f"Error: {response.status_code} - {ex}")
                        else:
                            user_id = user_data[0].get("id")
                            print(f"User ID: {user_id}")
                    else:
                        print("No user found with the provided email.")
                else:
                    print(f"Error: {response.status_code} - {response.text}")
            except:
                print("Connection to LMS failed.")

        if user_id == -1:
            return False

        payload = {
            "wstoken": wstoken,
            "wsfunction": "core_enrol_get_users_courses",
            "moodlewsrestformat": "json",
            "userid": user_id,
        }
        try:
            response = requests.post(url, data=payload)
            # Check if the request was successful
            if response.status_code == 200:
                # [{'id': 2, ...}, ...]
                user_data = response.json()
                if user_data:
                    # print(user_data)
                    if "exception" in user_data:
                        ex = response["exception"]
                        print(f"Error: {response.status_code} - {ex}")
                    else:
                        for item in user_data:
                            if int(item["id"]) == int(course_id):
                                print(f"Course ID: {course_id} found!")
                                return True
                else:
                    print("No course id found in users courses with the provided email.")
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except:
            print("Error during connection to LMS. Trying second attempt.")
            try:
                response = requests.post(url, data=payload)
                # Check if the request was successful
                if response.status_code == 200:
                    # [{'id': 2, ...}, ...]
                    user_data = response.json()
                    if user_data:
                        # print(user_data)
                        if "exception" in user_data:
                            ex = response["exception"]
                            print(f"Error: {response.status_code} - {ex}")
                        else:
                            for item in user_data:
                                if int(item["id"]) == int(course_id):
                                    print(f"Course ID: {course_id} found!")
                                    return True
                    else:
                        print("No course id found in users courses with the provided email.")
                else:
                    print(f"Error: {response.status_code} - {response.text}")
            except:
                print("Connection to LMS failed.")
                return False
        return False
