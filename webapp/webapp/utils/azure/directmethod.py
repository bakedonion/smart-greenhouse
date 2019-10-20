"""
This module implements direct method handlers for Azure IoT Hub. A handler takes care of authentication,
sending invocations and receiving their results, which are passed back to the caller.
"""

from base64 import b64encode, b64decode
from hashlib import sha256
from time import time
from urllib import parse
from hmac import HMAC
from typing import Mapping, Tuple
import requests
import json


class SimpleDirectMethodHandler:
    """
    This class is a simple handler for direct method invocation with python.

    The current azure-iot-sdk-python (v2) does not seem to support this feature out-of-the-box as of yet (2019-10-14)
    and v1's azure-iothub-service-client is only usable in very limited cases.

    Further information can be found here:
        https://github.com/Azure/azure-iot-sdk-python (v2 + current support for features)
        https://github.com/Azure/azure-iot-sdk-python/tree/v1-deprecated (v1 and its limitations)
    """

    def __init__(self, connection_string: str):
        """
        Initializes the DirectMethodHandler based on the IoT Hub connection string.

        ---

        Args:
            connection_string: The connection string for the IoTHub you wish to connect to.
        """
        self._token_hostname, self._token_key, self._policy_name = self._parse_connection_string(
            connection_string)
        self._current_sas_token = self._generate_sas_token(
            self._token_hostname, self._token_key, self._policy_name)

    def invoke_direct_method(self, url: str, method_name: str, response_timeout_in_secs: int = 30,
                             arguments: Mapping[str, any] = {}, **kwargs: Mapping[str, any]) -> str:
        """
        Invokes a direct method.

        ---

        Args:
            url: The request URI of the device.
            method_name: The method to invoke on the device.
            response_timeout_in_secs: Duration to wait for a response.
            arguments: The payload for the invoked method, as a dict.
            kwargs: The payload for the invoked method, as key=value pairs. Overrides values in arguments.

        Returns:
            The invocation response.
        """
        if self._sas_token_is_expired(self._current_sas_token):
            self._current_sas_token = self._generate_sas_token(
                self._token_hostname, self._token_key, self._policy_name)

        headers = {
            'ContentType': 'application/json',
            'Authorization': self._current_sas_token
        }

        arguments.update(kwargs)

        data = {
            'methodName': method_name,
            'responseTimeoutInSeconds': response_timeout_in_secs,
            'payload': arguments
        }

        req = requests.post(url=url, data=json.dumps(data), headers=headers)
        return json.loads(req.text)

    def _generate_sas_token(self, uri: str, key: str, policy_name: str, ttl_in_secs: int = 3600):
        """
        Generates a new SAS token.

        ---

        Args:
            uri: The request URI, for which to generate the token.
            key: The SharedAccesKey, with which to create the token.
            policy_name: The policy, for which to generate the token (must match the SharedAccessKey).
            ttl_in_secs: The lifespan of the token in seconds.

        Returns:
            The generated SAS token.
        """
        expires = int(time()) + ttl_in_secs
        sign_key = f'{parse.quote_plus(uri)}\n{expires}'
        signature = b64encode(
            HMAC(b64decode(key), sign_key.encode('utf-8'), sha256).digest())

        rawtoken = {
            'sr':  uri,
            'sig': signature,
            'se': str(expires)
        }

        if policy_name:
            rawtoken['skn'] = policy_name

        return 'SharedAccessSignature ' + parse.urlencode(rawtoken)

    def _sas_token_is_expired(self, sas_token: str) -> bool:
        """
        Validates, whether the given token is still valid, for at least 5 more minutes.

        ---

        Args:
            sas_token: The token to check.

        Returns:
            True if it is valid for at least five more minutes, else False.
        """
        _, _, query = sas_token.partition(' ')
        now = time()

        # token should be valid for at least 5 more minutes
        min_required_lifespan_in_secs = 300

        for param in query.split('&'):
            key, _, value = param.partition('=')
            key = key.lower()

            if key == 'se':
                return int(value) - now < min_required_lifespan_in_secs

        return False

    def _parse_connection_string(self, connection_string: str) -> Tuple[str, str, str]:
        """
        Parses the given conneciton string.

        ---

        Args:
            connection_string: The connection string to parse.

        Returns:
            The hostname, shared access key and policy name of the given connection string.

        Raises:
            ValueError if either of hostname, shared access key or policy name are missing.
        """
        token_hostname = None
        token_key = None
        policy_name = None

        for element in connection_string.split(';'):
            key, _, value = element.partition('=')
            key = key.lower()

            if key == 'hostname':
                token_hostname = value
            elif key == 'sharedaccesskeyname':
                policy_name = value
            elif key == 'sharedaccesskey':
                token_key = value

        if not all([token_hostname, token_key, policy_name]):
            raise ValueError("Invalid connection string")

        return token_hostname, token_key, policy_name

    @classmethod
    def create_from_connection_string(cls, connection_string: str) -> 'SimpleDirectMethodHandler':
        """
        Creates a new direct method handler based on the connection string.
        """
        return SimpleDirectMethodHandler(connection_string)
