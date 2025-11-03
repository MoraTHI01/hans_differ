#!/usr/bin/env python
"""OpenID Connect Implementation for flask multipass
   Using keycloak with openid connect as proxy to SAML2 shibboleth idp
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2024, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"

import logging
from urllib.parse import urlencode, urljoin, urlparse, urlunparse

from authlib.common.errors import AuthlibBaseError
from authlib.integrations.flask_client import FlaskIntegration, OAuth
from flask import current_app, redirect, request, url_for
from requests.exceptions import HTTPError, RequestException

from flask_multipass.auth import AuthProvider
from flask_multipass.data import AuthInfo, IdentityInfo
from flask_multipass.exceptions import AuthenticationFailed, IdentityRetrievalFailed
from flask_multipass.identity import IdentityProvider
from flask_multipass.util import login_view


# jwt/oidc-specific fields that are not relevant to applications
INTERNAL_FIELDS = ("nonce", "session_state", "acr", "jti", "exp", "azp", "iss", "iat", "auth_time", "typ", "nbf", "aud")


class _MultipassFlaskIntegration(FlaskIntegration):
    @staticmethod
    def load_config(oauth, name, params):
        # we do not support loading anything directly from the flask config
        return {}


class _MultipassOAuth(OAuth):
    framework_integration_cls = _MultipassFlaskIntegration

    def init_app(self, app, cache=None, fetch_token=None, update_token=None):
        # we do not use any of the flask extension functionality nor the registry
        # and do not want to prevent the main application from using it
        pass


_authlib_oauth = _MultipassOAuth("dummy")


class OidcAuthProvider(AuthProvider):
    """Provide authentication using Authlib (OAuth/OIDC).

    The type name to instantiate this provider is ``authlib``.

    The following settings are supported:

    - ``callback_uri``:  the relative uri used after a successful oauth login.
                         defaults to ``/multipass/authlib/<name>``, but you can
                         change it e.g. if your oauth/oidc infrastructure requires
                         a specific callback uri and you do not want to rely on the
                         default one.
    - ``include_token``: when set to ``True``, the AuthInfo passed to the
                         identity provider includes the ``token`` containing
                         the raw token data received from oauth. this is useful
                         when connecting this auth provider to a custom identity
                         provider that needs to do more than just calling the
                         userinfo endpoint.
                         when set to `'only'`, the AuthInfo will *only* contain
                         the token, and no other data will be retrieved from the
                         id token or userinfo endpoint.
    - ``use_id_token``:  specify whether to use the OIDC id token instead of
                         calling the userinfo endpoint. if unspecified or None,
                         it will default to true when the ``openid`` scope is
                         enabled (which indicates that OIDC is being used)
    - ``authlib_args``:  a dict of params forwarded to authlib. see the arguments
                         of ``register()`` in the
                         `authlib docs <https://docs.authlib.org/en/latest/client/frameworks.html>`_
                         for details.
    - ``shibboleth``:    Optional a dict of params with static meta data of the used
                         shibboleth idp in background of a keycloak service
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        callback_uri = self.settings.get("callback_uri", f"/multipass/authlib/{self.name}")
        self.authlib_client = _authlib_oauth.register(self.name, **self.authlib_settings)
        self.include_token = self.settings.get("include_token", True)
        self.use_id_token = self.settings.get("use_id_token", True)
        self.server_scheme = self.settings.get("server_scheme", "http")
        self.server_api_endpoint = self.settings.get("server_api_endpoint", "http://localhost:80/api")
        self.server_internal_api = self.settings.get("server_internal_api", "http://hans-frontend-web:5001")
        self.shibboleth_meta = self.settings.get("shibboleth", {})
        if self.use_id_token is None:
            # default to using the id token when using the openid scope (oidc)
            client_kwargs = self.authlib_settings.get("client_kwargs", {})
            scopes = client_kwargs.get("scope", "").split()
            self.use_id_token = "openid" in scopes
        self.authorized_endpoint = "_flaskmultipass_authlib_" + self.name
        current_app.add_url_rule(
            callback_uri, self.authorized_endpoint, self._authorize_callback, methods=("GET", "POST")
        )

    @property
    def authlib_settings(self):
        return self.settings["authlib_args"]

    @property
    def shibboleth_meta_data(self):
        return self.shibboleth_meta

    def _get_redirect_uri(self):
        return url_for(self.authorized_endpoint, _external=True)

    def initiate_external_login(self):
        try:
            redirect_uri = self._get_redirect_uri()
            redirect_uri = urlunparse(urlparse(str(redirect_uri))._replace(scheme=self.server_scheme))
            final_url = redirect_uri.replace(self.server_internal_api, self.server_api_endpoint)
            print("### REDIRECT URI: %s", final_url)
            return self.authlib_client.authorize_redirect(final_url)
        except RequestException:
            logging.getLogger("multipass.oidc").exception("Initiating Authlib login failed")
            multipass_exc = AuthenticationFailed("Logging in is currently not possible due to an error", provider=self)
            return self.multipass.handle_auth_error(multipass_exc, True)

    def process_logout(self, frontend_protocol, frontend_host, return_url, id_token):
        print("process_logout")
        try:
            logout_uri = self.authlib_settings["logout_uri"]
        except KeyError:
            logout_uri = self.authlib_client.load_server_metadata().get("end_session_endpoint")
        if logout_uri:
            return_url = urljoin(frontend_protocol + "://" + frontend_host, return_url)
            query = urlencode({"post_logout_redirect_uri": return_url})
            query_token = urlencode({"id_token_hint": id_token})
            print(logout_uri + "?" + query + "&" + query_token)
            # Currently post_logout_redirect_uri is not supported
            # return redirect(logout_uri + "?" + query + "&" + query_token)
            return redirect(logout_uri + "?" + query_token)

    @login_view
    def _authorize_callback(self):
        # if authorization failed abort early
        error = request.args.get("error")
        if error:
            raise AuthenticationFailed(error, provider=self)
        try:
            try:
                print("##### TOKEN AUTH")
                token_data = self.authlib_client.authorize_access_token()
                # print(token_data)
            except HTTPError as exc:
                try:
                    data = exc.response.json()
                except ValueError:
                    data = {"error": "unknown", "error_description": exc.response.text}
                error = data.get("error", "unknown")
                desc = data.get("error_description", repr(data))
                logging.getLogger("multipass.oidc").error(f"Getting token failed: {error}: %s", desc)
                raise
            authinfo_token_data = {}
            if self.include_token == "only":
                return self.multipass.handle_auth_success(AuthInfo(self, token=token_data))
            elif self.include_token:
                authinfo_token_data["token"] = token_data

            if self.use_id_token:
                try:
                    # authlib 1.0+ parses the id_token automatically
                    id_token = dict(token_data["userinfo"])
                except KeyError:
                    # older authlib versions
                    id_token = self.authlib_client.parse_id_token(token_data)
                for key in INTERNAL_FIELDS:
                    id_token.pop(key, None)
                return self.multipass.handle_auth_success(AuthInfo(self, **dict(authinfo_token_data, **id_token)))
            else:
                user_info = self.authlib_client.userinfo(token=token_data)
                return self.multipass.handle_auth_success(AuthInfo(self, **dict(authinfo_token_data, **user_info)))
        except AuthlibBaseError as exc:
            raise AuthenticationFailed(str(exc), provider=self)


class OidcIdentityProvider(IdentityProvider):
    """Provides identity information using Authlib.

    This provides access to all data returned by userinfo endpoint or id token.
    The type name to instantiate this provider is ``authlib``.
    """

    #: If the provider supports refreshing identity information
    supports_refresh = False
    #: If the provider supports getting identity information based from
    #: an identifier
    supports_get = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_field = self.settings.setdefault("identifier_field", "sub").lower()
        self.id_data = {}
        self.do_map = False
        self.shibboleth_meta = self.settings.get("shibboleth", {})
        if "mapping" in self.settings:
            mapping_dict = self.settings["mapping"]
            if mapping_dict is not None and len(mapping_dict) > 0:
                self.do_map = True

    def get_identity_from_auth(self, auth_info):
        """Retrieves identity information after authentication

        :param auth_info: An :class:`.AuthInfo` instance from an auth
                          provider
        :return: An :class:`.IdentityInfo` instance containing identity
                 information or ``None`` if no identity was found
        """
        print("get_identity_from_auth")
        # print(auth_info.data)
        # test = {
        #     'token': {
        #         'access_token': '0815.0815.0815-0815-0815',
        #         'expires_in': 300,
        #         'refresh_expires_in': 1800,
        #         'refresh_token': '0815.0815.0815',
        #         'token_type': 'Bearer',
        #         'id_token': '0815.0815.0815-0815-0815-0815-0815-0815-0815--0815--0815-A-0815',
        #         'not-before-policy': 0,
        #         'session_state': 'gaga-9eef-gaga-gaga-d6c74acfd4d0',
        #         'scope': 'openid profile groups email',
        #         'expires_at': 1722965936,
        #         'userinfo': {
        #             'exp': 1722965936,
        #             'iat': 1722965636,
        #             'auth_time': 1722957654,
        #             'jti': 'gaga-e708-4db5-8fbb-1436f12c194b',
        #             'iss': 'https://SOMEWHERE/realms/test',
        #             'aud': 'myclient',
        #             'sub': 'gaga-c4cc-gaga-ga-gad834e8',
        #             'typ': 'ID',
        #             'azp': 'myclient',
        #             'nonce': 'gagaga',
        #             'sid': 'gaga-gaga-gaga-gaga-gagsd4234',
        #             'at_hash': 'gasga-gaggag',
        #             'acr': '0',
        #             'email_verified': True,
        #             'name': 'Pikachu Pokemon',
        #             'groups': ['/admin', 'default-roles-test', 'offline_access', 'uma_authorization'],
        #             'preferred_username': 'pikachu24@somewhere.com',
        #             'given_name': 'Pikachu',
        #             'family_name': 'Pokemon',
        #             'email': 'pikachu.pokemon@somewhere.com'
        #         }
        #     },
        #     'sub': '97f9baac-c4cc-49ca-aa44-831b4d8792f4'
        # }
        identifier = auth_info.data.get(self.id_field)
        if not identifier:
            raise IdentityRetrievalFailed(f"Identifier ({self.id_field}) missing in authlib response", provider=self)

        # Dynamic mapping might be required?
        # if self.do_map is True:
        #    for k, v in self.settings['mapping'].items():
        #        if k in auth_info.data:
        #            value = auth_info.data.get(k)
        #            if k == "groups" or v == "group":
        #                for g in value:
        #                    if g.startswith("/"):
        #                        res_auth_info[k] = g.replace("/","",1)
        #            elif value is not None:
        #                res_auth_info[k] = value
        # print("### get_identity_from_auth: Store auth info")
        # print(res_auth_info)
        # self._id_data[identifier] = res_auth_info

        token_data = auth_info.data.get("token")
        user_info_data = token_data.get("userinfo")
        curr_group = "everybody"
        for g in user_info_data.get("groups"):
            if g.startswith("/"):
                curr_group = g.replace("/", "", 1)

        result = {
            "subject-id": identifier.strip(),
            "username": user_info_data.get("preferred_username"),
            "group": curr_group,
            "mail": user_info_data.get("email"),
            "displayName": user_info_data.get("name"),
            "givenName": user_info_data.get("given_name"),
            "sn": user_info_data.get("family_name"),
            "id_token": token_data.get("id_token"),
        }
        result.update(self.shibboleth_meta)
        self.id_data[identifier.strip()] = result
        return IdentityInfo(self, identifier=identifier.strip(), **result)

    def get_identity(self, identifier):  # pragma: no cover
        """Retrieves identity information.

        This method is similar to :meth:`refresh_identity` but does
        not require `multiauth_data`

        :param identifier: The unique user identifier used by the
                           provider.
        :return: An :class:`.IdentityInfo` instance or ``None`` if the
                 identity does not exist.
        """
        print("get_identity")
        return self.id_data[identifier.strip()]

    def is_valid_identity(self, identifier):
        """Checks if identifier is valid.

        :param identifier: The unique user identifier used by the
                           provider.
        :return: True if valid, Falso otherwise.
        """
        print("is_valid_identity")
        return identifier.strip() in self.id_data
