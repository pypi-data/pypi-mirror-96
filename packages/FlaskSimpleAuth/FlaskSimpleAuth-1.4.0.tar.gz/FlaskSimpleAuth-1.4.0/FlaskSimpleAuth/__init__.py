#
# Debatable flask-side auth management
#
# This code is public domain.
#

from typing import Optional, Union, Callable, Dict, List, Any
from flask import Flask, request, Response

import datetime as dt
from passlib.context import CryptContext  # type: ignore

import logging
log = logging.getLogger('auth')


# carry data for error Response
class AuthException(BaseException):
    def __init__(self, message: str, status: int):
        self.message = message
        self.status = status

#
# AUTH CONFIGURATION
#


# application configuration
APP: Optional[Flask] = None
CONF: Optional[Dict[str, Any]] = None

# auth type
AUTH: Optional[str] = None
LAZY: Optional[bool] = None

# auth token
NAME: Optional[str] = None
REALM: Optional[str] = None
SECRET: Optional[str] = None
DELAY: Optional[int] = None
GRACE: Optional[int] = None
HASH: Optional[str] = None
SIGLEN: Optional[int] = None

# parameter names
LOGIN: Optional[str] = None
USERP: Optional[str] = None
PASSP: Optional[str] = None

# password management
PM: Optional[CryptContext] = None

GetUserPasswordType = Optional[Callable[[str], str]]
get_user_password: GetUserPasswordType = None

# autorisation management
UserInGroupType = Optional[Union[Callable[[str, str], bool],
                                 Callable[[str, int], bool]]]
user_in_group: UserInGroupType = None

# local copy of authenticated user
USER: Optional[str] = None


# wipe out current authentication
def auth_cleanup(res: Response):
    global USER
    USER = None
    return res


# initialize module
def setConfig(app: Flask,
              gup: GetUserPasswordType = None,
              uig: UserInGroupType = None):
    global APP, CONF, AUTH, LAZY
    global NAME, REALM, SECRET, DELAY, GRACE, HASH, SIGLEN
    global LOGIN, USERP, PASSP, PM
    global get_user_password, user_in_group
    # overall setup
    APP = app
    CONF = app.config
    app.after_request(auth_cleanup)
    AUTH = CONF.get("FSA_TYPE", "httpd")
    LAZY = CONF.get("FSA_LAZY", True)
    # token setup
    NAME = CONF.get("FSA_TOKEN_NAME", "auth")
    import re
    realm = CONF.get("FSA_TOKEN_REALM", app.name).lower()
    # tr -cd "[a-z0-9_]" "": is there a better way to do that?
    REALM = "".join(c for c in realm if re.match("[-a-z0-9_]", c))
    import random
    import string
    # list of 94 chars, about 6.5 bits per char
    chars = string.ascii_letters + string.digits + string.punctuation
    if "FSA_TOKEN_SECRET" in CONF:
        SECRET = CONF["FSA_TOKEN_SECRET"]
        if SECRET is not None and len(SECRET) < 16:
            log.warning("token secret is short")
    else:
        log.warning("random token secret, only ok for one process app")
        SECRET = ''.join(random.SystemRandom().choices(chars, k=40))
    DELAY = CONF.get("FSA_TOKEN_DELAY", 60)
    GRACE = CONF.get("FSA_TOKEN_GRACE", 0)
    HASH = CONF.get("FSA_TOKEN_HASH", "blake2s")
    SIGLEN = CONF.get("FSA_TOKEN_LENGTH", 16)
    # parameters
    LOGIN = CONF.get("FSA_FAKE_LOGIN", "LOGIN")
    USERP = CONF.get("FSA_PARAM_USER", "USER")
    PASSP = CONF.get("FSA_PARAM_PASS", "PASS")
    # password setup
    # passlib context is a pain, you have to know the scheme name to set its
    # round which make it impossible to configure directly.
    scheme = CONF.get("FSA_PASSWORD_SCHEME", "bcrypt")
    options = CONF.get("FSA_PASSWORD_OPTIONS", {'bcrypt__default_rounds': 4})
    PM = CryptContext(schemes=[scheme], **options)
    get_user_password = gup
    # autorization helper
    user_in_group = uig


#
# HTTP FAKE AUTH
#
# Just trust a parameter, *only* for local testing.
#
# FSA_FAKE_LOGIN: name of parameter holding the login ("LOGIN")
#
def get_fake_auth():
    assert request.remote_user is None, "do not shadow web server auth"
    assert request.environ["REMOTE_ADDR"][:4] == "127.", \
        "fake auth only on localhost"
    params = request.values if request.json is None else request.json
    user = params.get(LOGIN, None)
    # it could check that the user exists in db
    if user is None:
        raise AuthException("missing login parameter", 401)
    log.info(f"LOGIN (param): {user}")
    return user


#
# PASSWORD MANAGEMENT
#
# FSA_PASSWORD_SCHEME: name of password scheme for passlib context
# FSA_PASSWORD_OPTIONS: further options for passlib context
#
# note: passlib bcrypt is Apache compatible
#

# verify password
def check_password(user, pwd, ref):
    if not PM.verify(pwd, ref):
        log.debug(f"LOGIN (password): password check failed {user}")
        raise AuthException(f"invalid password for user: {user}", 401)
    else:
        log.debug(f"LOGIN (password): password check succeeded for {user}")


# hash password consistently with above check, can be used by app
def hash_password(pwd):
    return PM.hash(pwd)


# check user password agains database-stored credentials
# raise an exception if not ok, otherwise simply proceeds
def check_db_password(user, pwd):
    ref = get_user_password(user)
    if ref is None:
        log.debug(f"LOGIN (password): no such user ({user})")
        raise AuthException(f"no such user: {user}", 401)
    check_password(user, pwd, ref)


#
# HTTP BASIC AUTH
#
def get_basic_auth():
    import base64 as b64
    assert request.remote_user is None
    auth = request.headers.get("Authorization", None)
    log.debug(f"auth: {auth}")
    if auth is None or auth[:6] != "Basic ":
        log.debug(f"LOGIN (basic): unexpected auth {auth}")
        raise AuthException("missing or unexpected authorization header", 401)
    user, pwd = b64.b64decode(auth[6:]).decode().split(':', 1)
    if not request.is_secure:
        log.warning("password authentication over an insecure request")
    check_db_password(user, pwd)
    log.info(f"LOGIN (basic): {user}")
    return user


#
# HTTP PARAM AUTH
#
# User credentials provided from http or json parameters.
#
# FSA_PARAM_USER: parameter name for login ("USER")
# FSA_PARAM_PASS: parameter name for password ("PASS")
#
def get_param_auth():
    assert request.remote_user is None
    params = request.values if request.json is None else request.json
    user, pwd = params.get(USERP, None), params.get(PASSP, None)
    if user is None:
        raise AuthException(f"missing login parameter: {USERP}", 401)
    if pwd is None:
        raise AuthException(f"missing password parameter: {PASSP}", 401)
    if not request.is_secure:
        log.warning("password authentication over an insecure request")
    check_db_password(user, pwd)
    log.info(f"LOGIN (param): {user}")
    return user


#
# TOKEN AUTH
#
# The token can be checked locally with a simple hash, without querying the
# database and validating a possibly expensive salted password (+400 ms!).
#
# Its form is: <realm>:<user>:<validity-limit>:<signature>
#
# FSA_TOKEN_NAME: name of parameter holding the token ("auth")
# FSA_TOKEN_HASH: hashlib algorithm for token authentication ("blake2s")
# FSA_TOKEN_LENGTH: number of signature bytes (32)
# FSA_TOKEN_DELAY: token validity in minutes (60)
# FSA_TOKEN_GRACE: grace delay for token validity in minutes (0)
# FSA_TOKEN_SECRET: signature secret for tokens (mandatory!)
# FSA_TOKEN_REALM: token realm (lc simplified app name)
#

# sign data with secret
def compute_signature(data, secret):
    import hashlib
    h = hashlib.new(HASH)
    h.update(f"{data}:{secret}".encode())
    return h.digest()[:SIGLEN].hex()


# build a timestamp string
def get_timestamp(ts):
    return "%04d%02d%02d%02d%02d%02d" % ts.timetuple()[:6]


# compute a token for "user" valid for "delay" minutes, signed with "secret"
def compute_token(realm, user, delay, secret):
    limit = get_timestamp(dt.datetime.utcnow() + dt.timedelta(minutes=delay))
    data = f"{realm}:{user}:{limit}"
    sig = compute_signature(data, secret)
    return f"{data}:{sig}"


# create a new token for user depending on the configuration
def create_token(user):
    return compute_token(REALM, user, DELAY, SECRET)


# tell whether token is ok: return validated user or None
# token form: "realm:calvin:20380119031407:<signature>"
def get_token_auth(token):
    realm, user, limit, sig = token.split(':', 3)
    # check realm
    if realm != REALM:
        log.info(f"LOGIN (token): unexpected realm {realm}")
        raise AuthException(f"unexpected realm: {realm}", 401)
    # check signature
    ref = compute_signature(f"{realm}:{user}:{limit}", SECRET)
    if ref != sig:
        log.info("LOGIN (token): invalid signature")
        raise AuthException("invalid auth token signature", 401)
    # check limit with a grace time
    now = get_timestamp(dt.datetime.utcnow() - dt.timedelta(minutes=GRACE))
    if now > limit:
        log.info("LOGIN (token): token {token} has expired")
        raise AuthException("expired auth token", 401)
    # all is well
    log.info(f"LOGIN (token): {user}")
    return user


# return authenticated user or throw exception
def get_user():

    global USER
    USER = None

    if AUTH is None:
        raise AuthException("FlaskSimpleAuth module not initialized", 500)

    if AUTH == "httpd":

        log.info(f"LOGIN (httpd): {request.remote_user}")
        USER = request.remote_user

    elif AUTH in ("fake", "param", "basic", "token", "password"):

        # check for token
        if SECRET is not None and SECRET != "":
            params = request.values if request.json is None else request.json
            token = params.get(NAME, None)
            if token is not None:
                USER = get_token_auth(token)

        # else try other schemes
        if USER is None:
            if AUTH == "param":
                USER = get_param_auth()
            elif AUTH == "basic":
                USER = get_basic_auth()
            elif AUTH == "fake":
                USER = get_fake_auth()
            elif AUTH == "password":
                try:
                    USER = get_basic_auth()
                except AuthException:  # try param
                    USER = get_param_auth()
            else:
                raise AuthException("auth token is required", 401)

        assert USER is not None  # else an exception would have been raised
        return USER

    else:

        raise AuthException(f"unexpected authentication type: {AUTH}", 500)


#
# authorize decorator
#
class authorize:

    def __init__(self, groups: Union[List[str], List[int], str, int] = None):
        assert user_in_group is not None, \
            "user_in_group callback needed for authorize"
        if isinstance(groups, str):
            groups = [groups]
        elif isinstance(groups, int):
            groups = [groups]
        self.groups = groups

    def __call__(self, fun):
        def wrapper(*args, **kwargs):
            global USER
            if USER is None:
                # no current user, try to get one?
                if LAZY:
                    try:
                        USER = get_user()
                    except AuthException:
                        return "", 401
                else:
                    return "", 401
            for g in self.groups:
                if user_in_group(USER, g):
                    return fun(*args, **kwargs)
            # else no matching group
            return "", 403
        # work around flask unwitty reliance on the function name
        wrapper.__name__ = fun.__name__
        return wrapper
