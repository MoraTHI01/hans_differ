#!/usr/bin/env python
"""Authorization handling - Stable LDAP-Only Version"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022-2024, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.1.0" # Stable LDAP integration
__status__ = "Production"


import sys
from datetime import timedelta
from urllib.parse import quote
from flask import jsonify, request, session, current_app
from flask_openapi3 import APIBlueprint
from flask_cors import cross_origin

from flask_multipass import Multipass
from flask_multipass.providers.static import StaticAuthProvider, StaticIdentityProvider

from api.modules.responses import AuthenticationRequired, UnauthorizedResponse
from api.modules.responses import ErrorResponse, RefreshAuthenticationRequired
from api.modules.security import SecurityConfiguration, SecurityMetaData

from api.modules.ldap_provider import LdapAuthProvider, LdapIdentityProvider

from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token


class AuthBlueprint(APIBlueprint):
    """Blueprint to manage authorization, focused on LDAP and Static providers."""

    def __init__(self, blueprint_id, name, **kwargs):
        super().__init__(blueprint_id, name, **kwargs)
        self.multipass = Multipass()
        self.jwt_manager = None
        # Define provider IDs as instance attributes for easy access
        self.ldap_auth_provider_id = "ldap_auth_provider"
        self.ldap_identity_provider_id = "ldap_identity_provider"
        self.simple_auth_provider_id = "simple_auth_provider"
        self.simple_identity_provider_id = "simple_identity_provider"

    def init_app(self, app):
        """Initialize Multipass and JWT with the Flask app."""
        self.multipass.register_provider(StaticAuthProvider, self.simple_auth_provider_id)
        self.multipass.register_provider(StaticIdentityProvider, self.simple_identity_provider_id)
        self.multipass.register_provider(LdapAuthProvider, self.ldap_auth_provider_id)
        self.multipass.register_provider(LdapIdentityProvider, self.ldap_identity_provider_id)
        
        self.multipass.init_app(app)
        self.multipass.identity_handler(self.identity_handler)
        self.jwt_manager = JWTManager(app)
        current_app.logger.info("AuthBlueprint: Multipass and JWT initialized.")

    def create_credentials_for_identity(self, identity):
        """Creates access and refresh tokens for a given identity dict."""
        time_delta_access = timedelta(hours=4)
        time_delta_refresh = timedelta(hours=6)
        if identity.get("role") == "ml-backend":
            time_delta_access = timedelta(hours=2)
            time_delta_refresh = timedelta(hours=2)

        access_token = create_access_token(identity=identity, expires_delta=time_delta_access)
        refresh_token = create_refresh_token(identity=identity, expires_delta=time_delta_refresh)
        return (access_token, refresh_token)

    def identity_handler(self, identity_info):
        """
        Multipass callback to handle a successful authentication from any provider.
        It prepares the final identity dictionary and returns JWTs.
        """
        provider_name = identity_info.provider.name if identity_info.provider else 'Unknown'
        current_app.logger.debug(f"Identity Handler entered for provider: '{provider_name}'")
        
        if not identity_info.data:
            current_app.logger.error(f"Identity handler for '{provider_name}' received no data.")
            return ErrorResponse.create_custom("Identity processing failed.")

        # Consolidate identity creation
        identity = {
            "id": identity_info.data.get("subject-id", identity_info.identifier),
            "username": quote(identity_info.data.get("username", identity_info.identifier)),
            "firstName": quote(identity_info.data.get("givenName", "")),
            "lastName": quote(identity_info.data.get("sn", "")),
            "mail": quote(identity_info.data.get("mail", "")),
            "preferedLanguage": quote(identity_info.data.get("preferedLanguage", "en")),
            "faculty": quote(identity_info.data.get("dfnEduPersonFieldOfStudyString", "")),
            "university": quote(identity_info.data.get("o", "")),
            "course": quote(identity_info.data.get("courseAcronymId", "")),
            "role": quote(identity_info.data.get("group", "user")),
            "idp": provider_name
        }

        # The static provider might have group info managed separately
        if provider_name == self.simple_identity_provider_id:
            groups = self.multipass.identity_providers[self.simple_identity_provider_id].get_identity_groups(identity_info.identifier)
            identity["role"] = quote(str(groups.pop().name) if groups else "user")

        current_app.logger.debug(f"Identity for {identity['username']} (IDP: {provider_name}) processed, creating JWTs.")
        (access_token, refresh_token) = self.create_credentials_for_identity(identity)
        return jsonify(access_token=access_token, refresh_token=refresh_token)


# --- Blueprint and Route Definitions ---

auth_api_bp = AuthBlueprint(
    "auth", __name__,
    abp_responses={"401": UnauthorizedResponse, "403": RefreshAuthenticationRequired},
    abp_security=SecurityConfiguration().get_security()
)

@auth_api_bp.route("/login", methods=["POST"], strict_slashes=False) 
def login_static_basic_auth():
    """Login using static provider (HTTP Basic Auth)."""
    print(f"--- ROUTE HIT --- /login (static basic auth) --- METHOD: {request.method}", flush=True)
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return AuthenticationRequired.create()
    
    data = {"username": auth.username, "password": auth.password}
    provider = auth_api_bp.multipass.auth_providers.get(auth_api_bp.simple_auth_provider_id)
    if not provider:
        return ErrorResponse.create_custom("Static provider not configured.")
    return auth_api_bp.multipass.handle_login_form(provider, data)


@auth_api_bp.route("/login/<provider_name>", methods=["POST"], strict_slashes=False) 
def login_via_provider_id(provider_name: str):
    """Login using a specified provider (e.g., 'ldap')."""
    print(f"--- ROUTE HIT --- /login/<provider> --- provider: '{provider_name}', Method: {request.method}", flush=True)

    provider_map = {
        "ldap": auth_api_bp.ldap_auth_provider_id,
        "static": auth_api_bp.simple_auth_provider_id
    }
    provider_id = provider_map.get(provider_name.lower())

    if not provider_id:
        current_app.logger.warning(f"Login attempt with unknown provider: '{provider_name}'")
        return ErrorResponse.create_custom("Provider does not exist", code=404)

    provider = auth_api_bp.multipass.auth_providers.get(provider_id)
    if not provider:
        current_app.logger.error(f"Provider '{provider_id}' is defined but not loaded in Multipass.")
        return ErrorResponse.create_custom("Provider not configured on server.", code=500)

    login_data = request.get_json(silent=True) 
    if not login_data or 'username' not in login_data or 'password' not in login_data:
        return ErrorResponse.create_custom("Username and password required in JSON body.", code=400)
    
    current_app.logger.debug(f"Calling handle_login_form for '{provider_id}' with user: {login_data['username']}")
    return auth_api_bp.multipass.handle_login_form(provider, login_data)


@auth_api_bp.route("/logout", methods=["POST"], strict_slashes=False) 
@jwt_required()
def logout():
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    current_app.logger.info(f"Logout processed for user: {sec_meta_data.username}")
    return jsonify(message="Successfully logged out")


@auth_api_bp.route("/sso-providers", methods=["GET"], strict_slashes=False)
def get_sso_providers():
    sso_providers_list = []
    
    if auth_api_bp.ldap_auth_provider_id in auth_api_bp.multipass.auth_providers:
        ldap_org_name = current_app.config.get('LDAP_ORGANIZATION_NAME', "University LDAP")
        ldap_domain = current_app.config.get('LDAP_DOMAIN', "") 
        sso_providers_list.append({
            "id": "ldap", 
            "o": ldap_org_name,
            "schacHomeOrganization": ldap_domain,
            "preferedLanguage": "de"
        })
    else:
        current_app.logger.warning("LDAP provider not found during SSO provider enumeration.")
   
    current_app.logger.debug(f"Returning SSO providers: {sso_providers_list}")
    return jsonify(sso_provider=sso_providers_list)


@auth_api_bp.route("/refresh", methods=["POST"], strict_slashes=False)
@jwt_required(refresh=True) 
def refresh():
    current_user_identity = get_jwt_identity() 
    if not current_user_identity:
        return ErrorResponse.create_custom("Invalid refresh token.")
    
    (new_access_token, _) = auth_api_bp.create_credentials_for_identity(current_user_identity)
    return jsonify(access_token=new_access_token)

