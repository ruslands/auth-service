import pytest

from app.resource.model import Resource
from tests.api.base import TestCRUDBase


@pytest.mark.usefixtures("test_client")
class Test(TestCRUDBase[Resource]):
    _url = "api/auth/v1/resource"

    @classmethod
    def create_object(cls):
        return {
            "endpoint": "/api/auth/v1/test",
            "method": "get",
            "description": "get all test",
            "rbac_enable": True,
            "visibility_group_enable": False
        }

    @pytest.mark.asyncio
    async def test_create(self, test_client):
        try:
            response_data = self._base_test_create(test_client)
            pytest.test_resource_id = response_data["data"]["id"]
        except AssertionError:
            response_data = self._base_test_get_list(test_client)
            for resource in response_data["data"]["items"]:
                if resource["endpoint"] == self.create_object()["endpoint"]:
                    pytest.test_resource_id = resource["id"]
                    break
        assert getattr(pytest, "test_resource_id", False)

    @pytest.mark.asyncio
    async def test_get_list(self, test_client):
        _ = self._base_test_get_list(test_client)

    @pytest.mark.asyncio
    async def test_get(self, test_client):
        _ = self._base_test_get(test_client, pytest.test_resource_id)

    @pytest.mark.asyncio
    async def test_update(self, test_client):
        _ = self._base_test_update(
            test_client,
            pytest.test_resource_id,
            updated_data={
                "endpoint": "/api/auth/v1/test_test",
                "method": "post",
            },
        )

    @pytest.mark.asyncio
    async def test_delete(self, test_client):
        self._base_test_delete(test_client, pytest.test_resource_id)
        _ = self._base_test_create(test_client)
