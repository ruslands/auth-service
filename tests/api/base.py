import urllib.parse
from typing import TypeVar, Generic

import pytest
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)


class TestBase(Generic[ModelType]):
    # The URL path where requests will be sent
    _url: str

    # The attribute name (str) for pytest
    # Example: "test_object_id" would imply pytest.test_object_id
    _id_attr_name: str

    @classmethod
    def create_object(cls) -> dict:
        raise NotImplementedError("Subclasses should implement this method")

    @classmethod
    def update_object(cls) -> dict:
        raise NotImplementedError("Subclasses should implement this method")

    @property
    def url(self):
        url = getattr(self, "_url", None)

        if not url:
            raise NotImplementedError("'_url' attribute should be defined")

        if not isinstance(url, str):
            raise ValueError("'_url' attribute should be 'str' type")

        return url

    @property
    def id_attr_name(self):
        id_attr_name = getattr(self, "_id_attr_name", None)

        if not id_attr_name:
            raise NotImplementedError("'_id_attr_name' attribute should be defined")

        if not isinstance(id_attr_name, str):
            raise ValueError("'_id_attr_name' attribute should be 'str' type")

        return id_attr_name

    @property
    def id_attr_value(self):
        return getattr(pytest, self.id_attr_name)

    @property
    def _headers(self):
        return {
            "Authorization": f"Bearer {pytest.test_token}"
        }

    @property
    def _default_params(self):
        return {
            "page": 1,
            "size": 100,
        }

    async def test_create(self, test_client, data=None) -> dict:
        if data is None:
            data = self.create_object()
        response = test_client.post(
            self.url,
            json=data,
            headers=self._headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        object_id = response_data["data"]["id"]
        setattr(pytest, self.id_attr_name, object_id)
        return response.json()

    async def test_get_list(self, test_client, params=None) -> dict:
        if params is None:
            params = self._default_params
        params_string = urllib.parse.urlencode(params)

        response = test_client.get(
            f"{self.url}/list?{params_string}",
            headers=self._headers,
        )
        assert response.status_code == 200
        return response.json()

    async def test_get(self, test_client, object_id=None) -> dict:
        if object_id is None:
            object_id = self.id_attr_value
        response = test_client.get(
            f"{self.url}/{object_id}",
            headers=self._headers,
        )
        assert response.status_code == 200
        return response.json()

    async def test_update(self, test_client, object_id=None, updated_data=None) -> dict:
        if object_id is None:
            object_id = self.id_attr_value
        if updated_data is None:
            updated_data = self.update_object()
        response = test_client.patch(
            f"{self.url}/{object_id}",
            headers=self._headers,
            json=updated_data,
        )
        assert response.status_code == 200
        return response.json()

    async def test_delete(self, test_client, object_id=None) -> None:
        if object_id is None:
            object_id = self.id_attr_value
        response = test_client.delete(
            f"{self.url}/{object_id}",
            headers=self._headers,
        )
        assert response.status_code == 200
