import json
import pytest
import string
import random


@pytest.mark.usefixtures("test_client")
class Test:
    url = "api/auth/v1/role"

    @classmethod
    def create_object(cls):
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
        data = self.create_object()
        response = test_client.post(
            self.url,
            json=data,
            headers={"Authorization": f"Bearer {pytest.test_token}"},
        )
        assert response.status_code == 200
        pytest.test_role_id = response.json()["data"]["id"]

    @pytest.mark.asyncio
    async def test_get_list(self, test_client):
        response = test_client.get(
            f"{self.url}/list?page=1&size=100",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get(self, test_client):
        response = test_client.get(
            f"{self.url}/{pytest.test_role_id}",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update(self, test_client):
        response = test_client.patch(
            f"{self.url}/{pytest.test_role_id}",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
            data=json.dumps({"title": "test_role_updated"}),
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete(self, test_client):
        response = test_client.delete(
            f"{self.url}/{pytest.test_role_id}",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
        )
        assert response.status_code == 200
