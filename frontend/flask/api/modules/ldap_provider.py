# api/modules/ldap_provider.py
import ssl
import uuid
from ldap3 import Server, Connection, Tls, SUBTREE, ALL_ATTRIBUTES
from ldap3.core.exceptions import LDAPException, LDAPBindError
from flask_multipass.auth import AuthProvider
from flask_multipass.identity import IdentityProvider
from flask_multipass.data import IdentityInfo
from flask_multipass.exceptions import MultipassException
from flask import current_app # Keep for logging within request context

class LdapAuthProvider(AuthProvider):
    def __init__(self, multipass, name, settings):
        super().__init__(multipass, name, settings)
        # Configuration is now passed via settings, not current_app at import time
        self.ldap_server_url = self.settings.get('ldap_server_url')
        if not self.ldap_server_url:
            raise ValueError("LdapAuthProvider setting 'ldap_server_url' is missing.")
            
        self.use_ssl = self.settings.get('use_ssl', True)
        
        self.service_bind_dn = self.settings.get('service_bind_dn')
        self.service_bind_password = self.settings.get('service_bind_password')
        self.base_dn = self.settings.get('base_dn')
        self.uid_attr = self.settings.get('uid_attr')

    def process_login(self, auth_info):
        login_username = auth_info.data.get('username')
        login_password = auth_info.data.get('password')

        if not login_username or not login_password:
            return None # Authentication failed

        server = Server(self.ldap_server_url, use_ssl=self.use_ssl)
        user_dn = None

        try:
            # Step 1: Bind with service account to find user's DN
            service_conn = Connection(server, user=self.service_bind_dn, password=self.service_bind_password, auto_referrals=False)
            if not service_conn.bind():
                current_app.logger.error(f"LDAP Auth: Cannot bind with service account: {service_conn.last_error}")
                return None

            search_filter = f'({self.uid_attr}={login_username})'
            if service_conn.search(search_base=self.base_dn, search_filter=search_filter, search_scope=SUBTREE, attributes=['dn']):
                if service_conn.entries and len(service_conn.entries) == 1:
                    user_dn = service_conn.entries[0].entry_dn
                else:
                    current_app.logger.warning(f"LDAP Auth: User {login_username} not found or multiple entries found.")
                    service_conn.unbind()
                    return None
            else:
                current_app.logger.error(f"LDAP Auth: Search for user {login_username} failed: {service_conn.last_error}")
                service_conn.unbind()
                return None
            service_conn.unbind()

            if not user_dn:
                return None

            # Step 2: Attempt to bind as the user with their DN and password
            user_conn = Connection(server, user=user_dn, password=login_password, auto_referrals=False)
            if user_conn.bind():
                current_app.logger.info(f"LDAP Auth: Successful bind for user {login_username}")
                user_conn.unbind()
                # Pass the username (sAMAccountName) to the identity provider
                return auth_info.identity_provider.process_auth(auth_info, login_username)
            else:
                current_app.logger.warning(f"LDAP Auth: Bind failed for user {login_username} (DN: {user_dn}): {user_conn.last_error}")
                user_conn.unbind()
                return None
        except (LDAPBindError, LDAPException) as e:
            current_app.logger.error(f"LDAP Exception for {login_username}: {e}")
            return None

    def initiate_external_login(self):
        raise MultipassException("LDAP provider does not support external login.", provider=self)

class LdapIdentityProvider(IdentityProvider):
    def __init__(self, multipass, name, settings):
        super().__init__(multipass, name, settings)
        self.ldap_server_url = self.settings.get('ldap_server_url')
        if not self.ldap_server_url:
            raise ValueError("LdapIdentityProvider setting 'ldap_server_url' is missing.")

        self.use_ssl = self.settings.get('use_ssl', True)
        self.service_bind_dn = self.settings.get('service_bind_dn')
        self.service_bind_password = self.settings.get('service_bind_password')
        self.base_dn = self.settings.get('base_dn')
        self.uid_attr = self.settings.get('uid_attr')
        self.fields_mapping = self.settings.get('fields_mapping', {})

    def get_identity(self, identifier):
        server = Server(self.ldap_server_url, use_ssl=self.use_ssl)
        conn = Connection(server, user=self.service_bind_dn, password=self.service_bind_password, auto_referrals=False)

        if not conn.bind():
            current_app.logger.error(f"LDAP Identity: Cannot bind with service account: {conn.last_error}")
            return None

        search_filter = f'({self.uid_attr}={identifier})'
        attributes_to_fetch = list(set(self.fields_mapping.values()))
        if 'memberOf' not in attributes_to_fetch:
            attributes_to_fetch.append('memberOf')

        if conn.search(search_base=self.base_dn, search_filter=search_filter, search_scope=SUBTREE, attributes=attributes_to_fetch):
            if conn.entries and len(conn.entries) == 1:
                entry = conn.entries[0]
                identity_data = {}
                for app_field, ldap_attr in self.fields_mapping.items():
                    if ldap_attr in entry:
                        value = entry[ldap_attr].value
                        if isinstance(value, bytes) and ldap_attr.lower() == 'objectguid':
                            value = str(uuid.UUID(bytes_le=value))
                        identity_data[app_field] = value if not isinstance(value, list) else value[0]
                    else:
                        identity_data[app_field] = ''
                
                # Placeholder for role mapping from groups
                if 'memberOf' in entry and entry.memberOf.values:
                    identity_data['group'] = 'user' # Your role mapping logic would go here
                else:
                    identity_data['group'] = 'user'

                conn.unbind()
                return identity_data
        
        conn.unbind()
        return None

    def process_auth(self, auth_info, identifier):
        identity_data = self.get_identity(identifier)
        if identity_data:
            return IdentityInfo(provider=self, identifier=identifier, data=identity_data)
        return None
