MAP = {
    "identifier": "urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
    "fro": {
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress": "emailaddress",  # E-Mail Address, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname": "givenname",  # Given Name, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name": "name",  # Name, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn": "upn",  # UPN, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.xmlsoap.org/claims/CommonName": "CommonName",  # Common Name, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.xmlsoap.org/claims/EmailAddress": "EmailAddress",  # AD FS 1.x E-Mail Address, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.xmlsoap.org/claims/Group": "Group",  # Group, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.xmlsoap.org/claims/UPN": "UPN",  # AD FS 1.x UPN, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/ws/2008/06/identity/claims/role": "role",  # Role, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname": "surname",  # Surname, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/privatepersonalidentifier": "privatepersonalidentifier",  # PPID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier": "nameidentifier",  # Name ID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/ws/2008/06/identity/claims/authenticationinstant": "authenticationinstant",  # Authentication time stamp, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/ws/2008/06/identity/claims/authenticationmethod": "authenticationmethod",  # Authentication method, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/denyonlysid": "denyonlysid",  # Deny only group SID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/ws/2008/06/identity/claims/denyonlyprimarysid": "denyonlyprimarysid",  # Deny only primary SID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/ws/2008/06/identity/claims/denyonlyprimarygroupsid": "denyonlyprimarygroupsid",  # Deny only primary group SID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/ws/2008/06/identity/claims/groupsid": "groupsid",  # Group SID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/ws/2008/06/identity/claims/primarygroupsid": "primarygroupsid",  # Primary group SID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/ws/2008/06/identity/claims/primarysid": "primarysid",  # Primary SID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/ws/2008/06/identity/claims/windowsaccountname": "windowsaccountname",  # Windows account name, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/01/devicecontext/claims/isregistereduser": "isregistereduser",  # Is Registered User, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/01/devicecontext/claims/identifier": "identifier",  # Device Identifier, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/01/devicecontext/claims/registrationid": "registrationid",  # Device Registration Identifier, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/01/devicecontext/claims/displayname": "displayname",  # Device Registration DisplayName, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/01/devicecontext/claims/ostype": "ostype",  # Device OS type, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/01/devicecontext/claims/osversion": "osversion",  # Device OS Version, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/01/devicecontext/claims/ismanaged": "ismanaged",  # Is Managed Device, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/01/requestcontext/claims/x-ms-forwarded-client-ip": "x-ms-forwarded-client-ip",  # Forwarded Client IP, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/01/requestcontext/claims/x-ms-client-application": "x-ms-client-application",  # Client Application, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/01/requestcontext/claims/x-ms-client-user-agent": "x-ms-client-user-agent",  # Client User Agent, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/01/requestcontext/claims/x-ms-client-ip": "x-ms-client-ip",  # Client IP, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/01/requestcontext/claims/x-ms-endpoint-absolute-path": "x-ms-endpoint-absolute-path",  # Endpoint Path, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/01/requestcontext/claims/x-ms-proxy": "x-ms-proxy",  # Proxy, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/01/requestcontext/claims/relyingpartytrustid": "relyingpartytrustid",  # Application Identifier, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/12/certificatecontext/extension/applicationpolicy": "applicationpolicy",  # Application policies, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/12/certificatecontext/extension/authoritykeyidentifier": "authoritykeyidentifier",  # Authority Key Identifier, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/12/certificatecontext/extension/basicconstraints": "basicconstraints",  # Basic Constraint, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/12/certificatecontext/extension/eku": "eku",  # Enhanced Key Usage, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/12/certificatecontext/field/issuer": "issuer",  # Issuer, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/12/certificatecontext/field/issuername": "issuername",  # Issuer Name, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/12/certificatecontext/extension/keyusage": "keyusage",  # Key Usage, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/12/certificatecontext/field/notafter": "notafter",  # Not After, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/12/certificatecontext/field/notbefore": "notbefore",  # Not Before, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/12/certificatecontext/extension/certificatepolicy": "certificatepolicy",  # Certificate Policies, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/rsa": "rsa",  # Public Key, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/12/certificatecontext/field/rawdata": "rawdata",  # Certificate Raw Data, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/12/certificatecontext/extension/san": "san",  # Subject Alternative Name, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/ws/2008/06/identity/claims/serialnumber": "serialnumber",  # Serial Number, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/12/certificatecontext/field/signaturealgorithm": "signaturealgorithm",  # Signature Algorithm, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/12/certificatecontext/field/subject": "subject",  # Subject, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/12/certificatecontext/extension/subjectkeyidentifier": "subjectkeyidentifier",  # Subject Key Identifier, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/12/certificatecontext/field/subjectname": "subjectname",  # Subject Name, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/12/certificatecontext/extension/certificatetemplateinformation": "certificatetemplateinformation",  # V2 Template Name, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/12/certificatecontext/extension/certificatetemplatename": "certificatetemplatename",  # V1 Template Name, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/thumbprint": "thumbprint",  # Thumbprint, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/12/certificatecontext/field/x509version": "x509version",  # X.509 Version, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/ws/2012/01/insidecorporatenetwork": "insidecorporatenetwork",  # Inside Corporate Network, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/ws/2012/01/passwordexpirationtime": "passwordexpirationtime",  # Password Expiration Time, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/ws/2012/01/passwordexpirationdays": "passwordexpirationdays",  # Password Expiration Days, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/ws/2012/01/passwordchangeurl": "passwordchangeurl",  # Update Password URL, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/claims/authnmethodsreferences": "authnmethodsreferences",  # Authentication Methods References, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/2012/01/requestcontext/claims/client-request-id": "client-request-id",  # Client Request ID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "http://schemas.microsoft.com/ws/2013/11/alternateloginid": "alternateloginid",  # Alternate Login ID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
    },
    "to": {
        "emailaddress": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",  # E-Mail Address, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "givenname": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",  # Given Name, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",  # Name, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "upn": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn",  # UPN, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "CommonName": "http://schemas.xmlsoap.org/claims/CommonName",  # Common Name, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "EmailAddress": "http://schemas.xmlsoap.org/claims/EmailAddress",  # AD FS 1.x E-Mail Address, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "Group": "http://schemas.xmlsoap.org/claims/Group",  # Group, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "UPN": "http://schemas.xmlsoap.org/claims/UPN",  # AD FS 1.x UPN, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "role": "http://schemas.microsoft.com/ws/2008/06/identity/claims/role",  # Role, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "surname": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname",  # Surname, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "privatepersonalidentifier": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/privatepersonalidentifier",  # PPID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "nameidentifier": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier",  # Name ID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "authenticationinstant": "http://schemas.microsoft.com/ws/2008/06/identity/claims/authenticationinstant",  # Authentication time stamp, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "authenticationmethod": "http://schemas.microsoft.com/ws/2008/06/identity/claims/authenticationmethod",  # Authentication method, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "denyonlysid": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/denyonlysid",  # Deny only group SID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "denyonlyprimarysid": "http://schemas.microsoft.com/ws/2008/06/identity/claims/denyonlyprimarysid",  # Deny only primary SID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "denyonlyprimarygroupsid": "http://schemas.microsoft.com/ws/2008/06/identity/claims/denyonlyprimarygroupsid",  # Deny only primary group SID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "groupsid": "http://schemas.microsoft.com/ws/2008/06/identity/claims/groupsid",  # Group SID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "primarygroupsid": "http://schemas.microsoft.com/ws/2008/06/identity/claims/primarygroupsid",  # Primary group SID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "primarysid": "http://schemas.microsoft.com/ws/2008/06/identity/claims/primarysid",  # Primary SID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "windowsaccountname": "http://schemas.microsoft.com/ws/2008/06/identity/claims/windowsaccountname",  # Windows account name, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "isregistereduser": "http://schemas.microsoft.com/2012/01/devicecontext/claims/isregistereduser",  # Is Registered User, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "identifier": "http://schemas.microsoft.com/2012/01/devicecontext/claims/identifier",  # Device Identifier, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "registrationid": "http://schemas.microsoft.com/2012/01/devicecontext/claims/registrationid",  # Device Registration Identifier, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "displayname": "http://schemas.microsoft.com/2012/01/devicecontext/claims/displayname",  # Device Registration DisplayName, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "ostype": "http://schemas.microsoft.com/2012/01/devicecontext/claims/ostype",  # Device OS type, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "osversion": "http://schemas.microsoft.com/2012/01/devicecontext/claims/osversion",  # Device OS Version, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "ismanaged": "http://schemas.microsoft.com/2012/01/devicecontext/claims/ismanaged",  # Is Managed Device, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "x-ms-forwarded-client-ip": "http://schemas.microsoft.com/2012/01/requestcontext/claims/x-ms-forwarded-client-ip",  # Forwarded Client IP, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "x-ms-client-application": "http://schemas.microsoft.com/2012/01/requestcontext/claims/x-ms-client-application",  # Client Application, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "x-ms-client-user-agent": "http://schemas.microsoft.com/2012/01/requestcontext/claims/x-ms-client-user-agent",  # Client User Agent, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "x-ms-client-ip": "http://schemas.microsoft.com/2012/01/requestcontext/claims/x-ms-client-ip",  # Client IP, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "x-ms-endpoint-absolute-path": "http://schemas.microsoft.com/2012/01/requestcontext/claims/x-ms-endpoint-absolute-path",  # Endpoint Path, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "x-ms-proxy": "http://schemas.microsoft.com/2012/01/requestcontext/claims/x-ms-proxy",  # Proxy, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "relyingpartytrustid": "http://schemas.microsoft.com/2012/01/requestcontext/claims/relyingpartytrustid",  # Application Identifier, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "applicationpolicy": "http://schemas.microsoft.com/2012/12/certificatecontext/extension/applicationpolicy",  # Application policies, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "authoritykeyidentifier": "http://schemas.microsoft.com/2012/12/certificatecontext/extension/authoritykeyidentifier",  # Authority Key Identifier, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "basicconstraints": "http://schemas.microsoft.com/2012/12/certificatecontext/extension/basicconstraints",  # Basic Constraint, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "eku": "http://schemas.microsoft.com/2012/12/certificatecontext/extension/eku",  # Enhanced Key Usage, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "issuer": "http://schemas.microsoft.com/2012/12/certificatecontext/field/issuer",  # Issuer, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "issuername": "http://schemas.microsoft.com/2012/12/certificatecontext/field/issuername",  # Issuer Name, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "keyusage": "http://schemas.microsoft.com/2012/12/certificatecontext/extension/keyusage",  # Key Usage, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "notafter": "http://schemas.microsoft.com/2012/12/certificatecontext/field/notafter",  # Not After, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "notbefore": "http://schemas.microsoft.com/2012/12/certificatecontext/field/notbefore",  # Not Before, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "certificatepolicy": "http://schemas.microsoft.com/2012/12/certificatecontext/extension/certificatepolicy",  # Certificate Policies, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "rsa": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/rsa",  # Public Key, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "rawdata": "http://schemas.microsoft.com/2012/12/certificatecontext/field/rawdata",  # Certificate Raw Data, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "san": "http://schemas.microsoft.com/2012/12/certificatecontext/extension/san",  # Subject Alternative Name, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "serialnumber": "http://schemas.microsoft.com/ws/2008/06/identity/claims/serialnumber",  # Serial Number, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "signaturealgorithm": "http://schemas.microsoft.com/2012/12/certificatecontext/field/signaturealgorithm",  # Signature Algorithm, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "subject": "http://schemas.microsoft.com/2012/12/certificatecontext/field/subject",  # Subject, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "subjectkeyidentifier": "http://schemas.microsoft.com/2012/12/certificatecontext/extension/subjectkeyidentifier",  # Subject Key Identifier, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "subjectname": "http://schemas.microsoft.com/2012/12/certificatecontext/field/subjectname",  # Subject Name, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "certificatetemplateinformation": "http://schemas.microsoft.com/2012/12/certificatecontext/extension/certificatetemplateinformation",  # V2 Template Name, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "certificatetemplatename": "http://schemas.microsoft.com/2012/12/certificatecontext/extension/certificatetemplatename",  # V1 Template Name, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "thumbprint": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/thumbprint",  # Thumbprint, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "x509version": "http://schemas.microsoft.com/2012/12/certificatecontext/field/x509version",  # X.509 Version, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "insidecorporatenetwork": "http://schemas.microsoft.com/ws/2012/01/insidecorporatenetwork",  # Inside Corporate Network, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "passwordexpirationtime": "http://schemas.microsoft.com/ws/2012/01/passwordexpirationtime",  # Password Expiration Time, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "passwordexpirationdays": "http://schemas.microsoft.com/ws/2012/01/passwordexpirationdays",  # Password Expiration Days, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "passwordchangeurl": "http://schemas.microsoft.com/ws/2012/01/passwordchangeurl",  # Update Password URL, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "authnmethodsreferences": "http://schemas.microsoft.com/claims/authnmethodsreferences",  # Authentication Methods References, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "client-request-id": "http://schemas.microsoft.com/2012/01/requestcontext/claims/client-request-id",  # Client Request ID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
        "alternateloginid": "http://schemas.microsoft.com/ws/2013/11/alternateloginid",  # Alternate Login ID, urn:oasis:names:tc:SAML:2.0:attrname-format:uri
    }
}
