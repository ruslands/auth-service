import json
import pytest
from tests.api.test_role import Test as TestRole
from tests.api.test_resource import Test as TestResource


@pytest.mark.usefixtures("test_client")
class Test:
    url = "api/auth/v1/permission"
    role = TestRole()
    resource = TestResource()

    @pytest.mark.asyncio
    async def test_create(self, test_client):
        await self.role.test_create(test_client=test_client)
        await self.resource.test_create(test_client=test_client)
        response = test_client.post(
            self.url,
            headers={"Authorization": f"Bearer {pytest.test_token}"},
            data=json.dumps(
                {
                    "resource_id": pytest.test_resource_id,
                    "role_id": pytest.test_role_id,
                    "title": "test",
                    "description": "get all test",
                }
            ),
        )
        assert response.status_code == 200
        pytest.test_id = response.json()["data"]["id"]

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
            f"{self.url}/{pytest.test_id}",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update(self, test_client):
        response = test_client.patch(
            f"{self.url}/{pytest.test_id}",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
            data=json.dumps({"title": "test_test"}),
        )
        assert response.status_code == 200

    def test_delete_permission(self, test_client):
        response = test_client.delete(
            f"{self.url}/{pytest.test_id}",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
        )
        assert response.status_code == 200
        # delattr(pytest, "test_id")
