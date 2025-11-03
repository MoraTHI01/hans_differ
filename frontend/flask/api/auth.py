#!/usr/bin/env python
"""Authorization handling"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


from datetime import timedelta
from urllib.parse import quote, unquote
from flask import jsonify, request, make_response, url_for, redirect, session
from flask_openapi3 import APIBlueprint
from flask_cors import cross_origin

from flask_multipass import Multipass
from flask_multipass.providers.static import StaticAuthProvider, StaticIdentityProvider

from api.modules.config import get_frontend_protocol, get_frontend_host_url
from api.modules.responses import AuthenticationRequired, UnauthorizedResponse
from api.modules.responses import ErrorResponse, RefreshAuthenticationRequired
from api.modules.security import SecurityConfiguration, SecurityMetaData
from api.modules.connectors.connector_provider import connector_provider

# Use custom authlib provider for openid connect
from api.modules.oidc import OidcAuthProvider, OidcIdentityProvider

# https://flask-jwt-extended.readthedocs.io/en/stable/basic_usage/
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token

# TODO: https://flask-jwt-extended.readthedocs.io/en/stable/blocklist_and_token_revoking.html#revoking-refresh-tokens


class AuthBlueprint(APIBlueprint):
    """Blueprint to manage authorization"""

    def __init__(self, blueprint_id, name):
        self.simple_auth_provider_id = "simple_auth_provider"
        self.simple_identity_provider_id = "simple_identity_provider"
        self.oidc_auth_provider_id = "oidc_auth_provider"
        self.oidc_identity_provider_id = "oidc_identity_provider"
        self.curr_auth_provider_id = "simple_auth_provider"
        self.curr_identity_provider_id = "simple_identity_provider"
        self.multipass = Multipass()
        self.jwt_manager = None
        super().__init__(
            blueprint_id,
            name,
            abp_responses={"401": UnauthorizedResponse, "403": RefreshAuthenticationRequired},
            abp_security=SecurityConfiguration().get_security(),
        )

    def get_auth_provider_id(self, provider):
        """Get current auth provider id"""
        if provider == "shib":
            return None
        elif provider == "oidc":
            return self.oidc_auth_provider_id
        elif provider == "static":
            return self.simple_auth_provider_id
        else:
            return self.simple_auth_provider_id

    def get_current_auth_provider_id(self):
        """Get current auth provider id"""
        return self.curr_auth_provider_id

    def set_current_auth_provider_id(self, provider):
        """Set current auth provider id"""
        self.curr_auth_provider_id = self.get_auth_provider_id(provider)

    def get_current_identity_provider_id(self):
        """Get current auth provider id"""
        return self.curr_identity_provider_id

    def init(self, app):
        """Set the multipass object for auth handling"""
        self.multipass.register_provider(StaticAuthProvider, self.simple_auth_provider_id)
        self.multipass.register_provider(StaticIdentityProvider, self.simple_identity_provider_id)
        self.multipass.register_provider(OidcAuthProvider, self.oidc_auth_provider_id)
        self.multipass.register_provider(OidcIdentityProvider, self.oidc_identity_provider_id)
        self.multipass.init_app(app)
        self.multipass.identity_handler(self.identity_handler)
        self.jwt_manager = JWTManager(app)

    def is_jwt_token_valid(self, token):
        """Verify JWT token is valid"""
        # print("is_jwt_token_valid")
        try:
            decode_token(token)
            return True
        except:
            return False

    def create_credentials_for_identity(self, identity):
        """Create credentials for identity"""
        # https://doku.tid.dfn.de/de:shibsp:config-slo?s[]=sessionlifetime
        # timedelta(seconds=43200)
        # timedelta(hours=12)
        time_delta_access = timedelta(hours=4)
        time_delta_refresh = timedelta(hours=6)
        if identity["role"] == "ml-backend":
            # Airflow user is only allowed for 2 hour,
            # download and publish requests should not last longer than two hours
            time_delta_access = timedelta(hours=2)
            time_delta_refresh = timedelta(hours=2)
        # print(f'Identity: {identity}')

        # print('Creating access and refresh token')
        access_token = create_access_token(identity=identity, expires_delta=time_delta_access)
        if self.is_jwt_token_valid(access_token) is False:
            print("Error: Unable to decode access token!")
            print("Please check JWT algorithm configuration!")

        refresh_token = create_refresh_token(identity=identity, expires_delta=time_delta_refresh)
        if self.is_jwt_token_valid(refresh_token) is False:
            print("Error: Unable to decode refresh token!")
            print("Please check JWT algorithm configuration!")
        return (access_token, refresh_token)

    def identity_handler(self, identity_info):
        """Handle identity request"""
        if identity_info.provider.name == self.oidc_identity_provider_id:
            identity_data = identity_info.provider.get_identity(identity_info.identifier)
            # print("OIDC Identity Data")
            # print(identity_data)
            identity = {
                "id": identity_data["subject-id"],
                "username": quote(identity_data["username"]),
                "firstName": quote(identity_data["givenName"]),
                "lastName": quote(identity_data["sn"]),
                "preferedLanguage": quote(identity_data["preferedLanguage"]),
                "faculty": quote(identity_data["dfnEduPersonFieldOfStudyString"]),
                "university": quote(identity_data["o"]),
                "course": quote(identity_data["courseAcronymId"]),
                "role": quote(identity_data["group"]),
                "idp": auth_api_bp.oidc_identity_provider_id,
                "id_token": identity_data["id_token"],
            }
            mongo_connector = connector_provider.get_metadb_connector()
            mongo_connector.connect()
            urn_meta_data = f"metadb:meta:post:identity:{identity_info.identifier}"
            curr_meta_data = mongo_connector.get_metadata(urn_meta_data)
            if curr_meta_data is not None:
                mongo_connector.remove_metadata(urn_meta_data)
            (success, urn_result) = mongo_connector.put_object(urn_meta_data, None, "application/json", identity)
            session["success-id"] = identity_info.identifier
            target_url = url_for("auth.login_success")
            # mongo_connector.disconnect()
            return redirect(target_url)
        else:
            groups = identity_info.provider.get_identity_groups(identity_info.identifier)
            identity = {
                "id": identity_info.data["subject-id"],
                "username": quote(identity_info.identifier),
                "firstName": quote(identity_info.data["givenName"]),
                "lastName": quote(identity_info.data["sn"]),
                "preferedLanguage": quote(identity_info.data["preferedLanguage"]),
                "faculty": quote(identity_info.data["dfnEduPersonFieldOfStudyString"]),
                "university": quote(identity_info.data["o"]),
                "course": quote(identity_info.data["courseAcronymId"]),
                "role": quote(str(groups.pop().name)),
                "idp": self.simple_identity_provider_id,
                "id_token": "0815",
            }
            print("Response with JWT access and refresh token")
            (access_token, refresh_token) = self.create_credentials_for_identity(identity)
            return jsonify(access_token=access_token, refresh_token=refresh_token)


auth_api_bp = AuthBlueprint("auth", __name__)


@auth_api_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login"""
    auth = request.authorization
    if not auth:
        return AuthenticationRequired.create()
    print("Login with provider: static")
    data = {"username": auth.username, "password": auth.password}
    auth_api_bp.set_current_auth_provider_id("static")
    return auth_api_bp.multipass.handle_login_form(
        auth_api_bp.multipass.auth_providers[auth_api_bp.get_current_auth_provider_id()], data
    )


@auth_api_bp.route("/login/", methods=["GET", "POST"])
@auth_api_bp.route("/login/<provider>", methods=["GET", "POST"])
def login_provider(provider=None):
    """Login using provider, e.g. shib for shibboleth"""
    if provider is not None:
        provider_name = str(provider)
        print(f"Login with provider: {provider_name}")
        auth_api_bp.set_current_auth_provider_id(provider_name)
        provider_id = auth_api_bp.get_current_auth_provider_id()
        if provider_id is not None:
            response = auth_api_bp.multipass.process_login(provider_id)
            response.headers.add("Access-Control-Allow-Origin", "*")  # Add CORS headers
            response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
            response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            response.headers.add("Access-Control-Expose-Headers", "Access-Control-Allow-Origin")
            response.status_code = 200
            return response
        else:
            return ErrorResponse.create_custom("Provider not found!")
    else:
        return ErrorResponse.create_custom("Provider name empty!")


@auth_api_bp.route("/login-oidc-success")
def login_success():
    if "success-id" in session:
        mongo_connector = connector_provider.get_metadb_connector()
        mongo_connector.connect()
        urn_meta_data = f"metadb:meta:post:identity:{session['success-id']}"
        curr_meta_data = mongo_connector.get_metadata(urn_meta_data)
        if curr_meta_data is None:
            return ErrorResponse.create_custom("Not allowed!")
        (access_token, refresh_token) = auth_api_bp.create_credentials_for_identity(curr_meta_data)
        session["success-id"] = None
        # mongo_connector.remove_metadata(urn_meta_data)
        # mongo_connector.disconnect()
        return jsonify(access_token=access_token, refresh_token=refresh_token)
    else:
        return ErrorResponse.create_custom("Not allowed!")


@auth_api_bp.route("/logout", methods=["GET", "POST"])
@jwt_required()
def logout():
    """Logout"""
    sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    if sec_meta_data.idp == auth_api_bp.oidc_identity_provider_id:
        auth_provider = auth_api_bp.multipass.auth_providers[auth_api_bp.oidc_auth_provider_id]
        print("Logout OIDC")
        # Redirect post logout url is not working so logout-oidc-success is not called,
        # but we erase the token before on client vue side in the auth store
        response = auth_provider.process_logout(
            get_frontend_protocol(), get_frontend_host_url(), url_for("auth.logout_success"), sec_meta_data.id_token
        )
        response.headers.add("Access-Control-Allow-Origin", "*")  # Add CORS headers
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        response.headers.add("Access-Control-Expose-Headers", "Access-Control-Allow-Origin")
        response.status_code = 200
        return response
    else:
        print("Logout")
        return jsonify(access_token="", refresh_token="")


@auth_api_bp.route("/logout-oidc-success")
def logout_success():
    print("OIDC logout success")
    return jsonify(access_token="", refresh_token="")


@auth_api_bp.route("/sso-providers", methods=["GET"])
def get_sso_providers():
    print("SSO providers")
    auth_provider = auth_api_bp.multipass.auth_providers[auth_api_bp.oidc_auth_provider_id]
    shibboleth_meta = auth_provider.shibboleth_meta_data
    sso_provider = [
        {
            "id": "oidc",  # Currently we map oidc to oidc_auth_provider_id
            "o": shibboleth_meta["o"],
            "schacHomeOrganization": shibboleth_meta["schacHomeOrganization"],
            "preferedLanguage": shibboleth_meta["preferedLanguage"],
        }
    ]
    return jsonify(sso_provider=sso_provider)


@auth_api_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    # sec_meta_data = SecurityMetaData.gen_meta_data_from_identity()
    # if not sec_meta_data.check_identity_is_valid():
    #    return UnauthorizedResponse.create()
    print("Refresh Token")
    # TODO: https://flask-jwt-extended.readthedocs.io/en/stable/blocklist_and_token_revoking.html#revoking-refresh-tokens
    try:
        identity = get_jwt_identity()
        (a_token, _) = auth_api_bp.create_credentials_for_identity(identity)
        return jsonify(access_token=a_token)  # , refresh_token=r_token)
    except:
        return ErrorResponse.create_custom("Error refreshing access token")
