import json
import pytest


@pytest.mark.usefixtures("test_client")
class Test:
    url = "api/auth/v1/resource"


    @pytest.mark.asyncio
    async def test_create(self, test_client):
        response = test_client.post(
            self.url,
            headers={
                "Authorization": f"Bearer {pytest.test_token}"},
            data=json.dumps({
                "endpoint": "/api/auth/v1/test",
                "method": "get",
                "description": "get all test",
                "rbac_enable": True,
                "visibility_group_enable": False
            }))
        if response.status_code == 409:
            response = test_client.get(
                f"{self.url}/list?page=1&size=100",
                headers={"Authorization": f"Bearer {pytest.test_token}"})
            for resource in response.json()["data"]["items"]:
                if resource["endpoint"] == "/api/auth/v1/test":
                    pytest.test_resource_id = resource["id"]
                    break
        else:
            assert response.status_code == 200
            pytest.test_resource_id = response.json()["data"]["id"]

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
            f"{self.url}/{pytest.test_resource_id}",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update(self, test_client):
        response = test_client.patch(
            f"{self.url}/{pytest.test_resource_id}",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
            data=json.dumps(
                {"endpoint": "/api/auth/v1/test_test", "method": "post"}),
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete(self, test_client):
        response = test_client.delete(
            f"{self.url}/{pytest.test_resource_id}",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
        )
        assert response.status_code == 200
        # delattr(pytest, "test_resource_id")
