# # Native # #
import os
import six
import json
import struct
import base64
import traceback
from uuid import UUID

# # Installed # #
import httpx
from cryptography.hazmat.primitives.asymmetric.rsa import (
    RSAPublicNumbers,
    RSAPrivateNumbers,
    rsa_crt_iqmp,
    rsa_crt_dmp1,
    rsa_crt_dmq1
)
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import NoEncryption

# # Package # #
from core.logger import logger
from core.exceptions import NotFoundException


__all__ = (
    "request",
    "lambda_request",
    "is_valid_uuid",
    "jwk2pem",
)


def request(method, url, **kwargs) -> dict:
    try:
        if method.lower() not in ["post", "get"]:
            logger.error('method not allowed')
            raise SystemExit("method not allowed")
        logger.debug(f"method - {method}; url - {url}; kwargs - {kwargs}")
        with httpx.Client() as client:
            if method == "post":
                r = client.post(url, **kwargs)
            elif method == "get":
                r = client.get(url, **kwargs)
                logger.debug(f"{r.url}")
        if r.status_code == 200:
            if r.text == '':
                return r
            return r.json()
        else:
            logger.error(f'api call error - {r.status_code}; {r.text}')
            raise SystemExit("api call error")
    except Exception as e:
        logger.error(f'api call error - {e}')
        raise SystemExit("api call error")


def lambda_request(lambda_client, function_name, payload, **kwargs) -> dict:
    try:
        response = lambda_client.invoke(
            FunctionName=os.environ[function_name],
            Payload=json.dumps(payload),
            InvocationType='RequestResponse'
        )
        response = json.loads(json.loads(response['Payload'].read())['body'])
        logger.debug(f"response: {response}")
        if not isinstance(response, dict):
            raise Exception(response)
        if response == {'error': 'Not Found'}:
            raise NotFoundException()
        return response
    except NotFoundException:
        logger.warning("Not found")
        return
    except Exception as e:
        logger.error(f'error while invoking {payload["path"]} - {e}')
        traceback.print_exc()
        return


def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.

     Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}

     Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.

     Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """

    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


def jwk2pem(jwk):
    def intarr2long(arr):
        return int(''.join(["%02x" % byte for byte in arr]), 16)

    def base64_to_long(data):
        if isinstance(data, six.text_type):
            data = data.encode("ascii")
        # urlsafe_b64decode will happily convert b64encoded data
        _d = base64.urlsafe_b64decode(bytes(data) + b'==')
        return intarr2long(struct.unpack('%sB' % len(_d), _d))

    e = base64_to_long(jwk['e'])
    n = base64_to_long(jwk['n'])
    p = base64_to_long(jwk['p'])
    q = base64_to_long(jwk['q'])
    d = base64_to_long(jwk['d'])
    dmp1 = rsa_crt_dmp1(d, p)
    dmq1 = rsa_crt_dmq1(d, q)
    iqmp = rsa_crt_iqmp(p, q)

    public_numbers = RSAPublicNumbers(e, n)
    private_numbers = RSAPrivateNumbers(p, q, d, dmp1, dmq1, iqmp, public_numbers)

    public_key = public_numbers.public_key(backend=default_backend())
    private_key = private_numbers.private_key(backend=default_backend())

    pem_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption()
    )
    return {"PEM_PUBLIC_KEY": pem_public_key, "PEM_PRIVATE_KEY": pem_private_key}
