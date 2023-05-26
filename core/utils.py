# # Native # #
import os
import six
import enum
import json
import struct
import base64
import traceback
from uuid import UUID
from typing import List, Type, Union, Dict, Any

# # Installed # #
from sqlmodel import SQLModel
from pydantic import BaseModel
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
from core.exceptions import NotFoundException, BadRequestException


__all__ = (
    "lambda_request",
    "is_valid_uuid",
    "jwk2pem",
    "ColumnAnnotation",
    "ApiListUtils",
)


class ColumnAnnotation:
    def __init__(
            self,
            column_name: str,
            key_name: str,
            column_type: str = "text",
            default_visibility: bool = False,
            is_filterable=True,
            is_editable: bool = False,
            **kwargs
    ):
        self.column_name = column_name
        self.key_name = key_name
        self.column_type = column_type
        self.default_visibility = default_visibility
        self.is_editable = is_editable
        self.is_filterable = is_filterable
        for key, value in kwargs.items():
            setattr(self, key, value)
        if self.column_type not in ["text", "image", "datetime", "url"]:
            raise Exception(
                "column_type must be one of ['text', 'image', 'datetime', 'url]")
        if not isinstance(self.default_visibility, bool):
            raise Exception("default_visibility must be a boolean")
        if not isinstance(self.is_editable, bool):
            raise Exception("is_editable must be a boolean")


class ApiListUtils:
    def __init__(
            self,
            iread: Type[SQLModel], ifilter: Type[BaseModel],
            mapping: Union[Dict[str, Dict], None] = None
    ):
        self.mapping = mapping
        self.iread = iread
        self.ifilter = ifilter

    async def filters(self, filters: Union[str, None] = None) -> Dict[str, Any]:
        filters_param = {}
        try:
            if filters is None:
                return {}
            filters = json.loads(filters)
            extend_filters = []
            for key, value in filters.items():
                if isinstance(value, str):
                    value = [value]
                table_field = key.split(".")
                if len(table_field) == 2:
                    # Нулевой индекс всегда таблица если есть точка
                    table = self.mapping.get(table_field[0])["model"]
                    possible_values = self.mapping.get(
                        table_field[0])["filter"].schema()['properties'].keys()
                    # Первый индекс всегда поле связанной таблицы
                    if not {table_field[1]}.issubset(set(possible_values)):
                        raise Exception(
                            f"Invalid filters. Possible values are: {possible_values}")
                    extend_filters.append({
                        "table": table,
                        "field": table_field[1],
                        "value": value
                    })
                if len(table_field) == 1:
                    possible_values = self.ifilter.schema()[
                        'properties'].keys()
                    if not {table_field[0]}.issubset(set(possible_values)):
                        raise Exception(
                            f"Invalid filters. Possible values are: {possible_values}")
                    filters_param["base"] = {key: value}
            filters_param["extend"] = extend_filters
            return filters_param
        except Exception as e:
            raise BadRequestException(detail=str(e))

    async def scope(self, scope: Union[str, None] = None) -> List[str]:
        possible_values = self.iread.schema()['properties'].keys()
        try:
            if scope is None:
                return []
            scope = json.loads(scope)
            scope = [scope] if isinstance(scope, str) else scope
            if len(scope) == 1:
                scope.append(scope[0])
            if not set(scope).issubset(set(possible_values)):
                raise Exception
            return scope
        except:
            raise BadRequestException(
                detail=f"Invalid scope. Possible values are: {possible_values}")


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
    private_numbers = RSAPrivateNumbers(
        p, q, d, dmp1, dmq1, iqmp, public_numbers)

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


class EnumMixin(enum.Enum):

    @classmethod
    def get_info(cls):
        return dict(map(lambda c: (c.name, c.value), cls))
