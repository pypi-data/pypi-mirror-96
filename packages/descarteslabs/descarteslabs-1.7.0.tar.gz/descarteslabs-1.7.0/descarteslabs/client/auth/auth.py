# Copyright 2018-2020 Descartes Labs.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import datetime
import errno
import json
import os
import random
import stat
import warnings
from hashlib import sha1

import requests
import six
import binascii
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from descarteslabs.client.exceptions import AuthError, OauthError
from descarteslabs.common.threading.local import ThreadLocalWrapper

DEFAULT_TOKEN_INFO_PATH = os.path.join(
    os.path.expanduser("~"), ".descarteslabs", "token_info.json"
)


def base64url_decode(input):
    """Helper method to base64url_decode a string.
    Args:
        input (str): A base64url_encoded string to decode.
    """
    rem = len(input) % 4
    if rem > 0:
        input += b"=" * (4 - rem)

    return base64.urlsafe_b64decode(input)


def makedirs_if_not_exists(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        except OSError as ex:
            if ex.errno == errno.EEXIST:
                pass
            else:
                raise


class Auth:
    """
    Authentication client used to authenticate with all Descartes Labs service APIs.
    """

    RETRY_CONFIG = Retry(
        total=5,
        backoff_factor=random.uniform(1, 10),
        method_whitelist=frozenset(["GET", "POST"]),
        status_forcelist=[429, 500, 502, 503, 504],
    )

    ADAPTER = ThreadLocalWrapper(lambda: HTTPAdapter(max_retries=Auth.RETRY_CONFIG))

    AUTHORIZATION_ERROR = (
        "No valid authentication info found{}. "
        "See https://docs.descarteslabs.com/authentication.html."
    )

    __attrs__ = [
        "domain",
        "scope",
        "leeway",
        "token_info_path",
        "client_id",
        "client_secret",
        "refresh_token",
        "_token",
        "_namespace",
        "RETRY_CONFIG",
    ]

    def __init__(
        self,
        domain="https://accounts.descarteslabs.com",
        scope=None,
        leeway=500,
        token_info_path=DEFAULT_TOKEN_INFO_PATH,
        client_id=None,
        client_secret=None,
        jwt_token=None,
        refresh_token=None,
        retries=None,
        _suppress_warning=False,
    ):
        """
        Helps retrieve JWT from a client id and refresh token for cli usage.

        :param str domain: The endpoint for auth0
        :type scope: list(str) or None
        :param scope: The JWT fields to be included
        :param int leeway: JWT expiration leeway
        :type token_info_path: str or None
        :param token_info_path: Path to a JSON file optionally holding auth information
        :type client_id: str or None
        :param client_id: JWT client id
        :type client_secret: str or None
        :param client_secret: JWT client secret
        :type jwt_token: str or None
        :param jwt_token: The JWT token, if we already have one
        :type refresh_token: str or None
        :param refresh_token: The refresh token
        """
        self.token_info_path = token_info_path

        token_info = {}
        if self.token_info_path:
            try:
                with open(self.token_info_path) as fp:
                    token_info = json.load(fp)
            except (IOError, ValueError):
                pass

        self.client_id = next(
            (
                x
                for x in (
                    client_id,
                    os.environ.get("DESCARTESLABS_CLIENT_ID"),
                    os.environ.get("CLIENT_ID"),
                    token_info.get("client_id"),
                )
                if x is not None
            ),
            None,
        )

        self.client_secret = next(
            (
                x
                for x in (
                    client_secret,
                    os.environ.get("DESCARTESLABS_CLIENT_SECRET"),
                    os.environ.get("CLIENT_SECRET"),
                    token_info.get("client_secret"),
                )
                if x is not None
            ),
            None,
        )

        self.refresh_token = next(
            (
                x
                for x in (
                    refresh_token,
                    os.environ.get("DESCARTESLABS_REFRESH_TOKEN"),
                    token_info.get("refresh_token"),
                )
                if x is not None
            ),
            None,
        )

        if self.client_secret != self.refresh_token:
            if self.client_secret is not None and self.refresh_token is not None:
                warnings.warn(
                    "Authentication token mismatch: "
                    "client_secret and refresh_token values must match for authentication to work correctly. "
                )

            if self.refresh_token is not None:
                self.client_secret = self.refresh_token
            elif self.client_secret is not None:
                self.refresh_token = self.client_secret

        self._token = next(
            (
                x
                for x in (
                    jwt_token,
                    os.environ.get("DESCARTESLABS_TOKEN"),
                    token_info.get("JWT_TOKEN"),
                    token_info.get("jwt_token"),
                )
                if x is not None
            ),
            None,
        )

        self.scope = next(
            (x for x in (scope, token_info.get("scope")) if x is not None), None
        )

        if token_info:
            # If the token was read from a path but environment variables were set, we may need
            # to reset the token.
            client_id_changed = token_info.get("client_id", None) != self.client_id
            client_secret_changed = (
                token_info.get("client_secret", None) != self.client_secret
            )
            refresh_token_changed = (
                token_info.get("refresh_token", None) != self.refresh_token
            )

            if client_id_changed or client_secret_changed or refresh_token_changed:
                self._token = None

        if not _suppress_warning and self.client_id is None and self._token is None:
            warnings.warn(self.AUTHORIZATION_ERROR.format(""))

        self._namespace = None
        if retries is None:
            self._adapter = self.ADAPTER
        else:
            self.RETRY_CONFIG = retries
            self._init_adapter()
        self._init_session()
        self.domain = domain
        self.leeway = leeway

    @classmethod
    def from_environment_or_token_json(cls, **kwargs):
        """
        Creates an Auth object from environment variables CLIENT_ID,
        CLIENT_SECRET, JWT_TOKEN if they are set, or else from a JSON
        file at the given path.

        :param str domain: The endpoint for auth0
        :type scope: list(str) or None
        :param scope: The JWT fields to be included
        :param int leeway: JWT expiration leeway
        :type token_info_path: str or None
        :param token_info_path: Path to a JSON file optionally holding auth information
        """
        return Auth(**kwargs)

    def _init_adapter(self):
        self._adapter = ThreadLocalWrapper(
            lambda: HTTPAdapter(max_retries=self.RETRY_CONFIG)
        )

    def _init_session(self):
        # Sessions can't be shared across threads or processes because the underlying
        # SSL connection pool can't be shared. We create them thread-local to avoid
        # intractable exceptions when users naively share clients e.g. when using
        # multiprocessing.
        self._session = ThreadLocalWrapper(self.build_session)

    @property
    def token(self):
        """
        Gets the token.

        :rtype: str
        :return: The JWT token string.

        :raises ~descarteslabs.client.exceptions.AuthError: Raised when
            incomplete information has been provided.
        :raises ~descarteslabs.client.exceptions.OauthError: Raised when
            a token cannot be obtained or refreshed.
        """
        if self._token is None:
            self._get_token()
        else:  # might have token but could be close to expiration
            exp = self.payload.get("exp")

            if exp is not None:
                now = (
                    datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
                ).total_seconds()
                if now + self.leeway > exp:
                    try:
                        self._get_token()
                    except AuthError as e:
                        # Unable to refresh, raise if now > exp
                        if now > exp:
                            raise e

        return self._token

    @property
    def payload(self):
        """
        Gets the token payload.

        :rtype: dict
        :return: Dictionary containing the fields specified by scope, which may include:

            .. highlight:: none

            ::

                name:           The name of the user.
                groups:         Groups to which the user belongs.
                org:            The organization to which the user belongs.
                email:          The email address of the user.
                email_verified: True if the user's email has been verified.
                sub:            The user identifier.
                exp:            The expiration time of the token, in seconds since
                                the start of the unix epoch.

        :raises ~descarteslabs.client.exceptions.AuthError: Raised when
            incomplete information has been provided.
        :raises ~descarteslabs.client.exceptions.OauthError: Raised when
            a token cannot be obtained or refreshed.
        """
        if self._token is None:
            self._get_token()

        if isinstance(self._token, six.text_type):
            token = self._token.encode("utf-8")
        else:
            token = self._token

        try:
            claims = token.split(b".")[1]
            return json.loads(base64url_decode(claims).decode("utf-8"))
        except (
            IndexError,
            UnicodeDecodeError,
            binascii.Error,
            json.JSONDecodeError,
        ) as e:
            raise AuthError("Unable to read token: {}".format(e))

    @property
    def session(self):
        """
        Gets the request session used to communicate with the OAuth server.

        :rtype: requests.Session
        :return: Session object
        """
        return self._session.get()

    def build_session(self):
        session = requests.Session()
        session.mount("https://", self.ADAPTER.get())
        return session

    def _get_token(self, timeout=100):
        if self.client_id is None:
            raise AuthError(self.AUTHORIZATION_ERROR.format(" (no client_id)"))

        if self.client_secret is None and self.refresh_token is None:
            raise AuthError(
                self.AUTHORIZATION_ERROR.format(" (no client_secret or refresh_token)")
            )

        if self.client_id in [
            "ZOBAi4UROl5gKZIpxxlwOEfx8KpqXf2c"
        ]:  # TODO(justin) remove legacy handling
            # TODO (justin) insert deprecation warning
            if self.scope is None:
                scope = ["openid", "name", "groups", "org", "email"]
            else:
                scope = self.scope
            params = {
                "scope": " ".join(scope),
                "client_id": self.client_id,
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "target": self.client_id,
                "api_type": "app",
                "refresh_token": self.refresh_token,
            }
        else:
            params = {
                "client_id": self.client_id,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            }

            if self.scope is not None:
                params["scope"] = " ".join(self.scope)

        r = self.session.post(self.domain + "/token", json=params, timeout=timeout)

        if r.status_code != 200:
            raise OauthError(
                "Could not retrieve token: {} ({})".format(r.text, r.status_code)
            )

        data = r.json()
        access_token = data.get("access_token")
        id_token = data.get("id_token")  # TODO(justin) remove legacy id_token usage

        if access_token is not None:
            self._token = access_token
        elif id_token is not None:
            self._token = id_token
        else:
            raise OauthError("Could not retrieve token")
        token_info = {}

        if self.token_info_path:
            try:
                with open(self.token_info_path) as fp:
                    token_info = json.load(fp)
            except (IOError, ValueError) as e:
                warnings.warn(
                    "Unable to read token_info from {} with error {}.".format(
                        self.token_info_path, str(e)
                    )
                )
                return

        token_info["jwt_token"] = self._token

        if self.token_info_path:
            token_info_directory = os.path.dirname(self.token_info_path)
            makedirs_if_not_exists(token_info_directory)

            try:
                with open(self.token_info_path, "w+") as fp:
                    json.dump(token_info, fp)

                os.chmod(self.token_info_path, stat.S_IRUSR | stat.S_IWUSR)
            except IOError as e:
                warnings.warn("Failed to save token: {}".format(e))

    @property
    def namespace(self):
        """
        Gets the user namespace.

        :rtype: str
        :return: The user namespace

        :raises ~descarteslabs.client.exceptions.AuthError: Raised when
            incomplete information has been provided.
        :raises ~descarteslabs.client.exceptions.OauthError: Raised when
            a token cannot be obtained or refreshed.
        """
        if self._namespace is None:
            self._namespace = sha1(self.payload["sub"].encode("utf-8")).hexdigest()
        return self._namespace

    def __getstate__(self):
        return dict((attr, getattr(self, attr)) for attr in self.__attrs__)

    def __setstate__(self, state):
        for name, value in state.items():
            setattr(self, name, value)

        self._init_adapter()
        self._init_session()


if __name__ == "__main__":
    auth = Auth()

    print(auth.token)
