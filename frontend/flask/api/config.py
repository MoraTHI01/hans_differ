# In hans-main/frontend/flask/api/config.py
import ssl

LDAP_SERVER = 'rodc.thi.de'
LDAP_PORT = 636
LDAP_USE_SSL = True
LDAP_SERVICE_ACCOUNT_BIND_DN = 'cn=aimotion-admin,OU=Adminkennungen,OU=Funktionsbenutzer,OU=Benutzer,DC=rz,DC=fh-ingolstadt,DC=de'
LDAP_SERVICE_ACCOUNT_BIND_PASSWORD = 'YOUR_SECURE_PASSWORD' # Consider environment variables
LDAP_BASE_DN = 'DC=rz,DC=fh-ingolstadt,DC=de'
LDAP_UID_ATTR = 'sAMAccountName'
LDAP_FIELDS_MAPPING = {
    'subject-id': 'objectGUID',
    'username': 'sAMAccountName',
    'givenName': 'givenName',
    'sn': 'sn',
    'mail': 'mail',
    'preferedLanguage': 'preferredLanguage',
    'dfnEduPersonFieldOfStudyString': 'department',
    'o': 'o',
    'courseAcronymId': 'extensionAttribute1',
    'group': 'memberOf'
}
LDAP_TLS_VALIDATE_CERT = ssl.CERT_REQUIRED
LDAP_TLS_VERSION = ssl.PROTOCOL_TLSv1_2
LDAP_ORGANIZATION_NAME = "THI LDAP"
LDAP_DOMAIN = "rz.fh-ingolstadt.de"

# For JWT secret key (already likely configured elsewhere, but good practice)
# import os
# JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-super-secret-jwt-key'
