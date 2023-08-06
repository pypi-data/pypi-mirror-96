# -*- coding: utf-8 -*-

from eve.auth import BasicAuth, TokenAuth
from eve.utils import config
from flask import request, Response, g
from flask import abort
from functools import wraps
from .validation import AsymmetricKeyValidator


AUTH_CLAIMS = 'authen_claims'
AUTH_ROLES = 'authen_roles'
AUTH_VALUE = 'auth_value'


class JWTAuth(TokenAuth):
    """
    Implements JWT token validation support.
    """

    def __init__(self, validator=None ,issuer=None):
        self.validator = validator #AsymmetricKeyValidator(key_url=key_url, default_key=default_key)
        self.issuer = issuer

    @property
    def validator(self):
        if self._validator is None:
            scope_claim = config.JWT_SCOPE_CLAIM
            roles_claim = config.JWT_ROLES_CLAIM
            self._validator = AsymmetricKeyValidator(key_url=config.JWT_KEY_URL,
                                        scope_claim=scope_claim, roles_claim=roles_claim)
        return self._validator

    @validator.setter
    def validator(self, value):
        self._validator = value

    @property
    def issuer(self):
        if self._issuer is None:
            return config.JWT_ISSUER
        return self._issuer

    @issuer.setter
    def issuer(self, value):
        self._issuer = value

    def set_authen_claims(self, claims):
        setattr(g, AUTH_CLAIMS, claims)

    def get_authen_claims(self):
        return g.get(AUTH_CLAIMS, {})

    def set_authen_roles(self, roles):
        setattr(g, AUTH_ROLES, roles)

    def get_authen_roles(self):
        return g.get(AUTH_ROLES, [])

    def authorized(self, allowed_roles, resource, method):
        authorized = False

        if request.authorization:
            auth = request.authorization
            authorized = self.check_auth(auth.username, auth.password,
                                         allowed_roles, resource, method)
        else:
            try:
                access_token = request.args['access_token']
            except KeyError:
                access_token = request.headers.get('Authorization', '').partition(' ')[2]
            authorized = self.check_token(access_token, allowed_roles, resource, method)

        return authorized

    def authenticate(self):
        """
        Indicate to the client that it needs to authenticate via a 401.
        """
        if request.headers.get('Authorization') or request.args.get('access_token'):
            realm = 'Bearer realm="%s", error="invalid_token"' % __package__
        else:
            realm = 'Bearer realm="%s"' % __package__
        # print(realm)
        resp = Response(None, 401, {'WWW-Authenticate': realm})
        abort(401, description='Please provide proper credentials', response=resp)

    def check_token(self, token, allowed_roles, resource, method):
        """
        This function is called when a token is sent throught the access_token
        parameter or the Authorization header as specified in the oAuth 2 specification.

        The provided token is validated with the JWT_SECRET defined in the Eve configuration.
        The token issuer (iss claim) must be the one specified by JWT_ISSUER and the audience
        (aud claim) must be one of the value(s) defined by the either the "audiences" resource
        parameter or the global JWT_AUDIENCES configuration.

        If JWT_ROLES_CLAIM is defined and a claim by that name is present in the token, roles
        are checked using this claim.

        If a JWT_SCOPE_CLAIM is defined and a claim by that name is present in the token, the
        claim value is check, and if "viewer" is present, only GET and HEAD methods will be
        allowed. The scope name is then added to the list of roles with the scope: prefix.

        If the validation succeed, the claims are stored and accessible thru the
        get_authen_claims() method.
        """
        domain = config.DOMAIN or {}
        resource_conf = domain.get(resource, {})
        audiences = resource_conf.get('audiences', config.JWT_AUDIENCES)
        return self._perform_validation(token, audiences, allowed_roles)

    def requires_token(self, audiences=None, allowed_roles=None):
        """
        Decorator for functions that will be protected with token authentication.

        Token must be provvided either through access_token parameter or Authorization
        header.

        See check_token() method for further details.
        """
        def requires_token_wrapper(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                try:
                    token = request.args['access_token']
                except KeyError:
                    token = request.headers.get('Authorization', '').partition(' ')[2]

                if not self._perform_validation(token, audiences, allowed_roles):
                    self.authenticate()
                    # abort(401)

                return f(*args, **kwargs)
            return decorated
        return requires_token_wrapper

    def _perform_validation(self, token, audiences, allowed_roles):
        validated, payload, account_id, roles = self.validator.validate_token(
                token, self.issuer, request.method, audiences, allowed_roles)
        if not validated:
            return False

        # Save roles for later access
        self.set_authen_roles(roles)

        # Save claims for later access
        self.set_authen_claims(payload)

        # Limit access to the authen account
        self.set_request_auth_value(account_id)

        return True

    def check_auth(self, username, password, allowed_roles, resource, method):
        return False


requires_token = JWTAuth().requires_token


def set_authen_claims(claims):
    """
    Set the authentication claims

    Parameters:
        claims (dict[str]): JWT claims
    """
    setattr(g, AUTH_CLAIMS, claims)


def get_authen_claims():
    """
    Get the authentication claims

    Returns:
        dict[str]: JWT claims
    """
    return g.get(AUTH_CLAIMS, {})


def set_authen_roles(roles=[]):
    """
    Get the authentication roles

    Parameters:
        roles (arr[str])
    """
    setattr(g, AUTH_ROLES, roles)


def get_authen_roles():
    """
    Get the authentication roles

    Returns:
        arr[str]: Array of associated roles
    """
    return g.get(AUTH_ROLES, [])


def set_request_auth_value(value=None):
    """
    Sets the current request's auth value

    Parameters:
        value (str|None): The request auth value
    """
    setattr(g, AUTH_VALUE, value)


def get_request_auth_value():
    """
    Get the authentication value

    Returns:
        str: auth value string
    """
    return g.get(AUTH_VALUE)
