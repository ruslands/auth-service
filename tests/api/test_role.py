import random
import string

import pytest

from app.role.model import Role
from tests.api.base import TestBase


@pytest.mark.usefixtures("test_client")
class Test(TestBase[Role]):
    _url = "api/auth/v1/role"
    _id_attr_name = "test_role_id"

    @classmethod
    def create_object(cls) -> dict:
        return {
            "title": "".join(
                random.choices(string.ascii_letters + string.digits, k=10)
            ),
            "description": "".join(
                random.choices(string.ascii_letters + string.digits, k=10)
            ),
            "default": False,
        }

    @classmethod
    def update_object(cls) -> dict:
        return {
            "title": "".join(
                random.choices(string.ascii_letters + string.digits, k=10)
            ),
        }

    @pytest.mark.asyncio
    async def test_create(self, test_client):
        await super().test_create(test_client)

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
