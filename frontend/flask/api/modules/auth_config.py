#!/usr/bin/env python
"""Central point to configure authentication"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022-2024, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.4" # Incremented for LDAP focus and OIDC removal
__status__ = "Draft"


import json
import os
from datetime import timedelta


def _read_json_config(config_file_path):
    """Read a json config file"""
    if os.path.isfile(config_file_path):
        try:
            with open(config_file_path, "r", encoding="utf-8") as jsonfile:
                return json.load(jsonfile)
        except json.JSONDecodeError as e:
            print(f"ERROR: JSONDecodeError in {config_file_path}: {e}")
            return {} 
    print(f"WARNING: Config file not found: {config_file_path}")
    return {}


def _get_auth_identities(static_auth_config):
    """Get identities dictionary for simple auth provider's 'identities' setting."""
    identities = {}
    if isinstance(static_auth_config, dict) and isinstance(static_auth_config.get("user"), list):
        for item in static_auth_config["user"]:
            if isinstance(item, dict) and "username" in item and "password" in item:
                 identities[item["username"]] = item["password"]
    return identities


def _get_identities_for_static_idp(static_auth_config):
    """Get identities dictionary for simple identity provider's 'identities' setting."""
    identities = {}
    if isinstance(static_auth_config, dict) and isinstance(static_auth_config.get("user"), list):
        for item in static_auth_config["user"]:
            if not isinstance(item, dict): continue
            username = item.get("username")
            if not username: continue
            identities[username] = {
                "subject-id": item.get("subject-id", username),
                "transient-id": item.get("transient-id"),
                "mail": item.get("mail"),
                "displayName": item.get("displayName"),
                "givenName": item.get("givenName"),
                "sn": item.get("sn"),
                "o": item.get("o"),
                "schacHomeOrganization": item.get("schacHomeOrganization"),
                "preferedLanguage": item.get("preferedLanguage"),
                "dfnEduPersonTermsOfStudy": item.get("dfnEduPersonTermsOfStudy"),
                "dfnEduPersonstudyBranch1": item.get("dfnEduPersonstudyBranch1"),
                "dfnEduPersonstudyBranch2": item.get("dfnEduPersonstudyBranch2"),
                "dfnEduPersonstudyBranch3": item.get("dfnEduPersonstudyBranch3"),
                "dfnEduPersonFieldOfStudyString": item.get("dfnEduPersonFieldOfStudyString"),
                "courseAcronymId": item.get("courseAcronymId"),
            }
    return identities


def _get_users_by_group(static_auth_config, target_group):
    """Get list of users of a specific group for StaticIdentityProvider's 'groups' setting."""
    users = []
    if isinstance(static_auth_config, dict) and isinstance(static_auth_config.get("user"), list):
        for item in static_auth_config["user"]:
            if isinstance(item, dict) and item.get("group") == target_group and "username" in item:
                users.append(item["username"])
    return users


def configure_flask_multipass(app):
    """
    Configure flask authorization and security
    :param Flask app: Flask app
    :return: Flask app Configured Flask app
    """
    auth_config_dir = os.path.join(os.path.dirname(__file__), "../auth")

    app_auth_file = os.path.join(auth_config_dir, "app_auth.json")
    # oidc_auth_file = os.path.join(auth_config_dir, "oidc_auth.json") # OIDC file no longer actively used for config
    static_auth_file = os.path.join(auth_config_dir, "static_auth.json")
    
    app_auth_config = _read_json_config(app_auth_file)
    # oidc_auth_config_from_file = _read_json_config(oidc_auth_file) # No longer loading OIDC config
    static_auth_config = _read_json_config(static_auth_file)
    
    app.config["MULTIPASS_AUTH_PROVIDERS"] = {
        # "oidc_auth_provider": oidc_auth_config_from_file.get("oidc_auth_provider", {}), # OIDC REMOVED
        "simple_auth_provider": {
            "type": "static", 
            "title": "Simple authentication provider",
            "identities": _get_auth_identities(static_auth_config),
        },
        "ldap_auth_provider": {
            "type": "ldap_auth_provider", # CRITICAL: Must match ID in auth.py's register_provider
            "title": "University LDAP Login",
            "settings": {} 
        },
    }
    
    app.config["MULTIPASS_IDENTITY_PROVIDERS"] = {
        # "oidc_identity_provider": { # OIDC REMOVED
        #     "type": "oidc_identity_provider", 
        #     "identifier_field": "sub",
        #     "shibboleth": oidc_auth_config_from_file.get("oidc_auth_provider", {}).get("shibboleth", {}),
        #     "restricted_permission_provider": oidc_auth_config_from_file.get("oidc_auth_provider", {}).get("restricted_permission_provider", {}),
        # },
        "simple_identity_provider": {
            "type": "static",
            "identities": _get_identities_for_static_idp(static_auth_config),
            "groups": {
                "admin": _get_users_by_group(static_auth_config, "admin"),
                "ml-backend": _get_users_by_group(static_auth_config, "ml-backend"),
                "lecturer": _get_users_by_group(static_auth_config, "lecturer"),
                "everybody": _get_users_by_group(static_auth_config, "everybody"),
                "developer": _get_users_by_group(static_auth_config, "developer"),
            },
        },
        "ldap_identity_provider": {
            "type": "ldap_identity_provider", # CRITICAL: Must match ID in auth.py
            "title": "University LDAP Identity",
            "settings": {}
        },
    }

    app.config["MULTIPASS_PROVIDER_MAP"] = {
        "simple_auth_provider": "simple_identity_provider",
        # "oidc_auth_provider": "oidc_identity_provider", # OIDC REMOVED
        "ldap_auth_provider": "ldap_identity_provider",
    }

    app.config["MULTIPASS_IDENTITY_INFO_KEYS"] = [
        "subject-id", "givenName", "mail", "sn", "preferedLanguage",
        "dfnEduPersonFieldOfStudyString", "o", "courseAcronymId", "group", "role"
    ]

    app_specific_security_config = app_auth_config.get("app", {})
    app.secret_key = app_specific_security_config.get("secret_key", os.urandom(24))
    app.config["JWT_SECRET_KEY"] = app_specific_security_config.get("JWT_SECRET_KEY", "default-jwt-super-secret-fallback")
    app.config["JWT_ALGORITHM"] = app_specific_security_config.get("JWT_ALGORITHM", "HS256")
    
    jwt_private_key_content = app_specific_security_config.get("JWT_PRIVATE_KEY")
    jwt_public_key_content = app_specific_security_config.get("JWT_PUBLIC_KEY")

    if app.config["JWT_ALGORITHM"] not in ["HS256", "HS384", "HS512"]:
        if jwt_private_key_content:
            app.config["JWT_PRIVATE_KEY"] = jwt_private_key_content
        else:
            print(f"ERROR: JWT_PRIVATE_KEY not found in app_auth.json for algorithm {app.config['JWT_ALGORITHM']}.")
        
        if jwt_public_key_content:
            app.config["JWT_PUBLIC_KEY"] = jwt_public_key_content
        else:
            print(f"ERROR: JWT_PUBLIC_KEY not found in app_auth.json for algorithm {app.config['JWT_ALGORITHM']}.")

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=int(app_specific_security_config.get("JWT_ACCESS_TOKEN_EXPIRES_HOURS", 3)))
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=int(app_specific_security_config.get("JWT_REFRESH_TOKEN_EXPIRES_DAYS", 30)))
    
    return app
