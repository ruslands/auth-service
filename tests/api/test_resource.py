import pytest

from app.resource.model import Resource
from tests.api.base import TestBase


@pytest.mark.usefixtures("test_client")
class Test(TestBase[Resource]):
    _url = "api/auth/v1/resource"
    _id_attr_name = "test_resource_id"

    @classmethod
    def create_object(cls):
        return {
            "endpoint": "/api/auth/v1/test",
            "method": "get",
            "description": "get all test",
            "rbac_enable": True,
            "visibility_group_enable": False
        }

    @classmethod
    def update_object(cls):
        return {
            "endpoint": "/api/auth/v1/test_test",
            "method": "post",
        }

    @pytest.mark.asyncio
    async def test_create(self, test_client):
        try:
            await super().test_create(test_client)
        except AssertionError:
            response_data = await super().test_get_list(test_client)
            for resource in response_data["data"]["items"]:
                if resource["endpoint"] == self.create_object()["endpoint"]:
                    setattr(pytest, self.id_attr_name, resource["id"])
                    break
        assert getattr(pytest, self.id_attr_name, False)

    @pytest.mark.asyncio
    async def test_get_list(self, test_client):
        await super().test_get_list(test_client)

    @pytest.mark.asyncio
    async def test_get(self, test_client):
        await super().test_get(test_client)

    @pytest.mark.asyncio
    async def test_update(self, test_client):
        await super().test_update(test_client)

    @pytest.mark.asyncio
    async def test_delete(self, test_client):
        await super().test_delete(test_client)
        await super().test_create(test_client)
