#!/usr/bin/env python
"""Central point to configure authentication"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import json
import os
from datetime import timedelta


def _read_json_config(config_file_path):
    """Read a json config file"""
    if os.path.isfile(config_file_path):
        with open(config_file_path, "r", encoding="utf-8") as jsonfile:
            return json.load(jsonfile)
    return None


def _get_auth_identities(static_auth_config):
    """Get identities dictionary for simple auth"""
    identities = {}
    for item in static_auth_config["user"]:
        identities[item["username"]] = item["password"]
    return identities


def _get_identities(static_auth_config):
    """Get identities dictionary for simple auth"""
    identities = {}
    for item in static_auth_config["user"]:
        # For shibboleth attributes see
        # https://doku.tid.dfn.de/de:common_attributes and
        # https://doku.tid.dfn.de/de:elearning_attributes and
        # https://doku.tid.dfn.de/de:aai:attributes_best_practice and
        # https://tools.aai.dfn.de/entities/
        identities[item["username"]] = {
            "subject-id": item["subject-id"],
            "transient-id": item["transient-id"],
            "mail": item["mail"],
            "displayName": item["displayName"],
            "givenName": item["givenName"],
            "sn": item["sn"],
            "o": item["o"],
            "schacHomeOrganization": item["schacHomeOrganization"],
            "preferedLanguage": item["preferedLanguage"],
            # Spezifikation des Fachsemesters in jedem
            # einzelnen Faches. Das Attribut enthält numerische Werte der Studienfächer
            # aus der Klassifikation von Prüfungsgruppen und Abschlussprüfungen des
            # Statistischen Bundesamtes (s.
            # https://www.destatis.de/DE/Methoden/Klassifikationen/Bildung/studenten-pruefungsstatistik.pdf)
            # und entspricht dem Wert von dfnEduPersonStudyBranch3, oder,
            # falls dieses nicht gepflegt wird, dfnEduPersonStudyBranch2
            # sowie zusätzlich mit einem ‘$’ getrennt das Fachsemester
            "dfnEduPersonTermsOfStudy": item["dfnEduPersonTermsOfStudy"],
            "dfnEduPersonstudyBranch1": item["dfnEduPersonstudyBranch1"],
            "dfnEduPersonstudyBranch2": item["dfnEduPersonstudyBranch2"],
            "dfnEduPersonstudyBranch3": item["dfnEduPersonstudyBranch3"],
            "dfnEduPersonFieldOfStudyString": item["dfnEduPersonFieldOfStudyString"],
            # course acronym id of the account, e.g. 'FODESOA', '*' is wildcard to omit course filtering
            "courseAcronymId": item["courseAcronymId"],
        }
    return identities


def _get_users_by_group(static_auth_config, group):
    """Get list of users of a specific group"""
    users = []
    for item in static_auth_config["user"]:
        if item["group"] == group:
            users.append(item["username"])
    return users


def configure_flask_multipass(app):
    """
    Configure falsk authorization and security
    :param Flask app: Flask app
    :return: Flask app Configured Flask app
    """
    auth_config_dir = os.path.join(os.path.dirname(__file__), "../auth")

    app_auth_file = os.path.join(auth_config_dir, "app_auth.json")
    oidc_auth_file = os.path.join(auth_config_dir, "oidc_auth.json")
    # shib_auth_file = os.path.join(auth_config_dir, "shib_auth.json")
    static_auth_file = os.path.join(auth_config_dir, "static_auth.json")
    app_auth_config = _read_json_config(app_auth_file)
    oidc_auth_config = _read_json_config(oidc_auth_file)
    # shib_auth_config = _read_json_config(shib_auth_file)
    static_auth_config = _read_json_config(static_auth_file)

    app.config["MULTIPASS_LOGIN_URLS"] = {"/login/", "/login/<provider>"}
    app.config["MULTIPASS_AUTH_PROVIDERS"] = {
        "oidc_auth_provider": oidc_auth_config["oidc_auth_provider"],
        "simple_auth_provider": {
            "type": "static",
            "title": "Simple authentication provider",
            "identities": _get_auth_identities(static_auth_config),
        },
    }
    app.config["MULTIPASS_IDENTITY_PROVIDERS"] = {
        "oidc_identity_provider": {
            "type": "oidc_identity_provider",
            "identifier_field": "sub",
            "shibboleth": oidc_auth_config["oidc_auth_provider"]["shibboleth"],
        },
        "simple_identity_provider": {
            "type": "static",
            "identities": _get_identities(static_auth_config),
            "groups": {
                "admin": _get_users_by_group(static_auth_config, "admin"),
                "ml-backend": _get_users_by_group(static_auth_config, "ml-backend"),
                "lecturer": _get_users_by_group(static_auth_config, "lecturer"),
                "everybody": _get_users_by_group(static_auth_config, "everybody"),
                "developer": _get_users_by_group(static_auth_config, "developer"),
            },
        },
    }
    app.config["MULTIPASS_PROVIDER_MAP"] = {
        "simple_auth_provider": "simple_identity_provider",
        "oidc_auth_provider": "oidc_identity_provider",
    }

    app.config["MULTIPASS_LOGIN_FORM_TEMPLATE"] = ""
    app.config["MULTIPASS_LOGIN_SELECTOR_TEMPLATE"] = ""
    app.config["MULTIPASS_LOGIN_URLS"] = {}
    app.config["MULTIPASS_IDENTITY_INFO_KEYS"] = [
        "subject-id",
        "givenName",
        "sn",
        "preferedLanguage",
        "dfnEduPersonFieldOfStudyString",
        "o",
        "courseAcronymId",
    ]

    # https://curity.io/resources/learn/jwt-best-practices/
    # https://flask-jwt-extended.readthedocs.io/en/stable/options/#jwt-cookie-samesite
    # https://flask-jwt-extended.readthedocs.io/en/stable/refreshing_tokens/#explicit-refreshing-with-refresh-tokens
    app.secret_key = app_auth_config["app"]["secret_key"]
    app.config["JWT_SECRET_KEY"] = app_auth_config["app"]["JWT_SECRET_KEY"]
    app.config["JWT_ALGORITHM"] = app_auth_config["app"]["JWT_ALGORITHM"]
    app.config["JWT_PRIVATE_KEY"] = app_auth_config["app"]["JWT_PRIVATE_KEY"]
    app.config["JWT_PUBLIC_KEY"] = app_auth_config["app"]["JWT_PUBLIC_KEY"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=3)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    return app
