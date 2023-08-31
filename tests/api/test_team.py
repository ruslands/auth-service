import random
import string
import pytest

from base.test import TestBase


class Test(TestBase):
    def __init__(self):
        super().__init__("api/auth/v1/team")

    @classmethod
    def create_object(cls):
        return {
            "title": ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        }

    @pytest.mark.asyncio
    async def test_create(self, test_client):
        data = self.create_object()
        await super().test_create(test_client, data=data)

    @pytest.mark.asyncio
    async def test_get_list(self, test_client):
        await super().test_get_list(test_client)

    @pytest.mark.asyncio
    async def test_get(self, test_client):
        await super().test_get(test_client)

    @pytest.mark.asyncio
    async def test_update(self, test_client):
        data = self.create_object()
        await super().test_update(test_client, data=data)

    @pytest.mark.asyncio
    async def test_delete(self, test_client):
        await super().test_delete(test_client)
