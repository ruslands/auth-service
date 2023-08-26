import random
import string

import pytest

from app.team.model import Team
from tests.api.base import TestBase


@pytest.mark.usefixtures("test_client")
class Test(TestBase[Team]):
    _url = "api/auth/v1/team"
    _id_attr_name = "test_team_id"

    @classmethod
    def create_object(cls):
        return {
            "title": "".join(
                random.choices(string.ascii_letters + string.digits, k=10)
            ),
        }

    @classmethod
    def update_object(cls):
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
        await super().test_create(test_client)
