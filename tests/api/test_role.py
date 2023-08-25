import random
import string

import pytest

from app.role.model import Role
from tests.api.base import TestCRUDBase


@pytest.mark.usefixtures("test_client")
class Test(TestCRUDBase[Role]):
    _url = "api/auth/v1/role"

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

    @pytest.mark.asyncio
    async def test_create(self, test_client):
        response_data = self._base_test_create(test_client)
        pytest.test_role_id = response_data["data"]["id"]

    @pytest.mark.asyncio
    async def test_get_list(self, test_client):
        _ = self._base_test_get_list(test_client)

    @pytest.mark.asyncio
    async def test_get(self, test_client):
        _ = self._base_test_get(test_client, pytest.test_role_id)

    @pytest.mark.asyncio
    async def test_update(self, test_client):
        _ = self._base_test_update(
            test_client,
            pytest.test_role_id,
            updated_data={
                "title": "".join(
                    random.choices(string.ascii_letters + string.digits, k=10)
                ),
            },
        )

    @pytest.mark.asyncio
    async def test_delete(self, test_client):
        self._base_test_delete(test_client, pytest.test_role_id)
