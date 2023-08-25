import urllib.parse
from typing import TypeVar, Generic

import pytest
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)


class TestCRUDBase(Generic[ModelType]):
    _url: str

    @classmethod
    def create_object(cls) -> dict:
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

    def _base_test_create(self, test_client, data=None) -> dict:
        if data is None:
            data = self.create_object()
        response = test_client.post(
            self.url,
            json=data,
            headers=self._headers,
        )
        assert response.status_code == 200
        return response.json()

    def _base_test_get_list(self, test_client, params=None) -> dict:
        if params is None:
            params = self._default_params
        params_string = urllib.parse.urlencode(params)

        response = test_client.get(
            f"{self.url}/list?{params_string}",
            headers=self._headers,
        )
        assert response.status_code == 200
        return response.json()

    def _base_test_get(self, test_client, pk) -> dict:
        response = test_client.get(
            f"{self.url}/{pk}",
            headers=self._headers,
        )
        assert response.status_code == 200
        return response.json()

    def _base_test_update(self, test_client, pk, updated_data) -> dict:
        response = test_client.patch(
            f"{self.url}/{pk}",
            headers=self._headers,
            json=updated_data,
        )
        assert response.status_code == 200
        return response.json()

    def _base_test_delete(self, test_client, pk) -> None:
        response = test_client.delete(
            f"{self.url}/{pk}",
            headers=self._headers,
        )
        assert response.status_code == 200
