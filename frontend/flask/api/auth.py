#!/usr/bin/env python
"""Authorization handling - LDAP Focus with Enhanced Logging & Refined Routing"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022-2024, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.8" # Incremented for refined routing/logging
__status__ = "Draft"

from datetime import timedelta
from urllib.parse import quote, unquote
from flask import jsonify, request, make_response, url_for, redirect, session, current_app
from flask_openapi3 import APIBlueprint # Use this directly
from flask_cors import cross_origin

from flask_multipass import Multipass
from flask_multipass.providers.static import StaticAuthProvider, StaticIdentityProvider

from api.modules.responses import AuthenticationRequired, UnauthorizedResponse
from api.modules.responses import ErrorResponse, RefreshAuthenticationRequired
from api.modules.security import SecurityConfiguration, SecurityMetaData

from connectors.connector_provider import connector_provider

from api.modules.ldap_provider import LdapAuthProvider, LdapIdentityProvider

from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token

# Define blueprint directly using APIBlueprint.
# The name 'auth' here is critical for flask-openapi3 if it uses it for path prefixing
# when app.register_api(auth_api_bp) is called without an explicit url_prefix there.
# However, your URL map shows routes are at root of where blueprint is mounted.
auth_api_bp = APIBlueprint(
    "auth",  # Blueprint name
    __name__,
    abp_responses={"401": UnauthorizedResponse, "403": RefreshAuthenticationRequired},
    abp_security=SecurityConfiguration().get_security()
)

# Provider ID constants for internal use and registration
SIMPLE_AUTH_PROVIDER_ID = "simple_auth_provider"
SIMPLE_IDENTITY_PROVIDER_ID = "simple_identity_provider"
LDAP_AUTH_PROVIDER_ID = "ldap_auth_provider"
LDAP_IDENTITY_PROVIDER_ID = "ldap_identity_provider"

# These will be initialized in init_multipass_for_blueprint
_multipass_instance = None
_jwt_manager_instance = None

# State for current providers (managed within the blueprint's context)
_current_auth_provider_id_state = SIMPLE_AUTH_PROVIDER_ID
_current_identity_provider_id_state = SIMPLE_IDENTITY_PROVIDER_ID


def init_multipass_for_blueprint(app):
    global _multipass_instance, _jwt_manager_instance
    if _multipass_instance is None:
        _multipass_instance = Multipass()
        _multipass_instance.register_provider(StaticAuthProvider, SIMPLE_AUTH_PROVIDER_ID)
        _multipass_instance.register_provider(StaticIdentityProvider, SIMPLE_IDENTITY_PROVIDER_ID)
        _multipass_instance.register_provider(LdapAuthProvider, LDAP_AUTH_PROVIDER_ID)
        _multipass_instance.register_provider(LdapIdentityProvider, LDAP_IDENTITY_PROVIDER_ID)
        
        _multipass_instance.init_app(app)
        _multipass_instance.identity_handler(identity_handler_func) # Use a direct function reference
    
    if _jwt_manager_instance is None:
        _jwt_manager_instance = JWTManager(app)
    
    current_app.logger.info(f"Multipass and JWT initialized for blueprint '{auth_api_bp.name}'.")


def get_auth_provider_id_func(provider_name_str):
    provider_lower = provider_name_str.lower() if provider_name_str else ""
    if provider_lower == "static":
        return SIMPLE_AUTH_PROVIDER_ID
    elif provider_lower == "ldap":
        return LDAP_AUTH_PROVIDER_ID
    else:
        current_app.logger.warning(f"Unknown auth provider requested: {provider_name_str}")
        return None

def set_current_providers_func(provider_name_str):
    global _current_auth_provider_id_state, _current_identity_provider_id_state
    
    resolved_auth_id = get_auth_provider_id_func(provider_name_str)
    _current_auth_provider_id_state = resolved_auth_id
    
    if resolved_auth_id == LDAP_AUTH_PROVIDER_ID:
        _current_identity_provider_id_state = LDAP_IDENTITY_PROVIDER_ID
    elif resolved_auth_id == SIMPLE_AUTH_PROVIDER_ID:
        _current_identity_provider_id_state = SIMPLE_IDENTITY_PROVIDER_ID
    else:
        _current_identity_provider_id_state = None
    current_app.logger.debug(f"Current auth provider set to: {_current_auth_provider_id_state}, identity: {_current_identity_provider_id_state}")


def is_jwt_token_valid_func(token):
    try:
        decode_token(token)
        return True
    except Exception as e: 
        current_app.logger.error(f"JWT token validation error: {e}")
        return False

def create_credentials_for_identity_func(identity):
    time_delta_access = timedelta(hours=4)
    time_delta_refresh = timedelta(hours=6)
    if identity.get("role") == "ml-backend":
        time_delta_access = timedelta(hours=2)
        time_delta_refresh = timedelta(hours=2)

    access_token = create_access_token(identity=identity, expires_delta=time_delta_access)
    if not is_jwt_token_valid_func(access_token): # Use the helper
        current_app.logger.error("Unable to decode newly created access token!")

    refresh_token = create_refresh_token(identity=identity, expires_delta=time_delta_refresh)
    if not is_jwt_token_valid_func(refresh_token): # Use the helper
        current_app.logger.error("Unable to decode newly created refresh token!")
    return (access_token, refresh_token)

# This function will be registered as the identity_handler
def identity_handler_func(identity_info):
    current_app.logger.debug(f"identity_handler_func called for provider name: '{identity_info.provider.name if identity_info.provider else 'None'}' and ID: '{identity_info.identifier}'")
    identity_data_source = identity_info.data 
    final_idp_name = identity_info.provider.name # This should be the registered ID like "ldap_identity_provider"

    if not identity_data_source:
        current_app.logger.error(f"Identity handler for '{final_idp_name}' received no data in identity_info.data.")
        return ErrorResponse.create_custom(f"Identity processing failed for {final_idp_name}.")

    # Common structure for identity
    identity = {
        "id": identity_data_source.get("subject-id", identity_data_source.get("username", identity_info.identifier)),
        "username": quote(identity_data_source.get("username", identity_info.identifier)), # Fallback to identifier
        "firstName": quote(identity_data_source.get("givenName", "")),
        "lastName": quote(identity_data_source.get("sn", "")),
        "mail": quote(identity_data_source.get("mail", "")),
        "preferedLanguage": quote(identity_data_source.get("preferedLanguage", "en")),
        "faculty": quote(identity_data_source.get("dfnEduPersonFieldOfStudyString", "")), # These might be specific to IdP
        "university": quote(identity_data_source.get("o", "")),
        "course": quote(identity_data_source.get("courseAcronymId", "")),
        "role": quote(identity_data_source.get("group", "user")), # 'group' from LdapIdentityProvider or static config
        "idp": final_idp_name,
        "id_token": "N/A" if final_idp_name != "oidc_identity_provider" else identity_data_source.get("id_token", "N/A_OIDC_MISSING")
    }
    
    # If it was static provider, it might have groups differently
    if final_idp_name == SIMPLE_IDENTITY_PROVIDER_ID:
        groups = _multipass_instance.identity_providers[SIMPLE_IDENTITY_PROVIDER_ID].get_identity_groups(identity_info.identifier)
        identity["role"] = quote(str(groups.pop().name) if groups else "user")

    current_app.logger.debug(f"Identity for {identity['username']} (IDP: {final_idp_name}) processed, creating JWTs.")
    (access_token, refresh_token) = create_credentials_for_identity_func(identity)
    return jsonify(access_token=access_token, refresh_token=refresh_token)


@auth_api_bp.route("/login", methods=["POST"], strict_slashes=False) 
def login_static_basic_auth():
    """Login using static provider (HTTP Basic Auth). Expects Basic Auth header."""
    current_app.logger.debug(f"Request to /login (static basic auth). Method: {request.method}")
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        current_app.logger.warning("/login - Basic auth credentials missing.")
        return AuthenticationRequired.create()
    
    data = {"username": auth.username, "password": auth.password}
    set_current_providers_func("static") 
    
    static_auth_provider_instance = _multipass_instance.auth_providers.get(SIMPLE_AUTH_PROVIDER_ID)
    if not static_auth_provider_instance:
        current_app.logger.error("Static Auth Provider instance not found for /login.")
        return ErrorResponse.create_custom("Static provider not configured.")
    
    current_app.logger.debug(f"Calling handle_login_form for Static (Basic Auth) with user: {data['username']}")
    return _multipass_instance.handle_login_form(static_auth_provider_instance, data)


@auth_api_bp.route("/login/<provider_name_from_url>", methods=["POST"], strict_slashes=False) 
def login_via_provider_id(provider_name_from_url=None):
    """Login using a specified provider (e.g., LDAP). Expects JSON body with username/password."""
    current_app.logger.debug(f"login_via_provider_id function entered. provider_name_from_url: '{provider_name_from_url}', Method: {request.method}")

    if not provider_name_from_url:
        current_app.logger.warning("login_via_provider_id called with no provider name.")
        return ErrorResponse.create_custom("Provider name must be specified in the URL.")

    set_current_providers_func(provider_name_from_url)
    actual_auth_provider_id = _current_auth_provider_id_state # Use the state variable

    current_app.logger.debug(f"login_via_provider_id - Resolved actual_auth_provider_id: {actual_auth_provider_id}")

    if actual_auth_provider_id == LDAP_AUTH_PROVIDER_ID:
        if request.method == "POST": # This route now only handles POST for LDAP
            current_app.logger.debug("login_via_provider_id - LDAP POST request received.")
            login_data = request.get_json(silent=True) 
            if login_data is None:
                current_app.logger.error("login_via_provider_id - LDAP POST: Invalid JSON or Content-Type.")
                return ErrorResponse.create_custom("Invalid request: JSON body expected.")
            if 'username' not in login_data or 'password' not in login_data:
                current_app.logger.error("login_via_provider_id - LDAP POST: Missing username or password.")
                return ErrorResponse.create_custom("Username and password required.")
            
            ldap_auth_provider_instance = _multipass_instance.auth_providers.get(LDAP_AUTH_PROVIDER_ID)
            if not ldap_auth_provider_instance:
                current_app.logger.error(f"LDAP Auth Provider instance ('{LDAP_AUTH_PROVIDER_ID}') not found.")
                return ErrorResponse.create_custom("LDAP provider not configured on server.")
            
            current_app.logger.debug(f"login_via_provider_id - Calling handle_login_form for LDAP user: {login_data.get('username')}")
            # handle_login_form will call LdapAuthProvider.process_login, then identity_handler_func
            response = _multipass_instance.handle_login_form(ldap_auth_provider_instance, login_data) 
            current_app.logger.debug(f"login_via_provider_id - LDAP handle_login_form response status: {response.status_code if hasattr(response, 'status_code') else 'N/A'}")
            return response
        else: # Should not be reached if route is POST only, but defensive
            return ErrorResponse.create_custom("GET not supported for this LDAP login endpoint.")
            
    # Add other specific provider handlers here if needed, e.g. /login/static_json_post
    # elif actual_auth_provider_id == SIMPLE_AUTH_PROVIDER_ID: ...
            
    else: 
        current_app.logger.warning(f"login_via_provider_id - Provider '{provider_name_from_url}' (resolved to '{actual_auth_provider_id}') is not supported or unknown.")
        return ErrorResponse.create_custom(f"Login provider '{provider_name_from_url}' not supported.")


@auth_api_bp.route("/logout", methods=["POST"], strict_slashes=False) # Changed to POST only for consistency
@jwt_required()
def logout():
    """Logout user."""
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    idp_type = sec_meta_data.idp 
    current_app.logger.debug(f"/logout called for IDP type: {idp_type}, user: {sec_meta_data.username}")
    
    # For JWT-based auth, logout is primarily client-side token removal.
    # Backend can implement token blocklisting if needed.
    # Here, we just acknowledge and confirm.
    current_app.logger.info(f"Logout processed for user: {sec_meta_data.username}, IDP: {idp_type}")
    return jsonify(message="Successfully logged out", access_token="", refresh_token="")


@auth_api_bp.route("/sso-providers", methods=["GET"], strict_slashes=False)
def get_sso_providers():
    """Lists available SSO providers and their metadata."""
    sso_providers_list = []
    current_app.logger.debug("/sso-providers endpoint called.") 
    
    # Check for LDAP provider
    if LDAP_AUTH_PROVIDER_ID in _multipass_instance.auth_providers:
        current_app.logger.debug(f"LDAP provider '{LDAP_AUTH_PROVIDER_ID}' found for /sso-providers.")
        try:
            ldap_org_name = current_app.config.get('LDAP_ORGANIZATION_NAME', "University LDAP") # Fallback name
            ldap_domain = current_app.config.get('LDAP_DOMAIN', "") 
            sso_providers_list.append({
                "id": "ldap", 
                "o": ldap_org_name,
                "schacHomeOrganization": ldap_domain,
                "preferedLanguage": current_app.config.get('LDAP_PREFERED_LANGUAGE', "de") 
            })
        except Exception as e: 
            current_app.logger.error(f"Error processing LDAP provider for /sso-providers list: {e}")
    else:
        current_app.logger.debug(f"LDAP provider ID '{LDAP_AUTH_PROVIDER_ID}' NOT found for /sso-providers list.")
   
    current_app.logger.debug(f"Final sso_providers_list: {sso_providers_list}")
    return jsonify(sso_provider=sso_providers_list)


@auth_api_bp.route("/refresh", methods=["POST"], strict_slashes=False)
@jwt_required(refresh=True) 
def refresh():
    """Refresh access token using a valid refresh token."""
    current_app.logger.debug("/refresh endpoint called.")
    try:
        current_user_identity = get_jwt_identity() 
        if not current_user_identity:
            current_app.logger.error("/refresh - Invalid refresh token: No identity.")
            return ErrorResponse.create_custom("Invalid refresh token.")
        (new_access_token, _) = create_credentials_for_identity_func(current_user_identity)
        current_app.logger.debug("/refresh - New access token created.")
        return jsonify(access_token=new_access_token)
    except Exception as e:
        current_app.logger.error(f"/refresh - Error: {e}")
        return ErrorResponse.create_custom("Error refreshing access token.")

