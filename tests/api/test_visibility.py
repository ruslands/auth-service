import json
import random
import string
import pytest


@pytest.mark.usefixtures("test_client")
class Test:
    url = "/api/auth/v1/visibility_group"

    @classmethod
    def create_object(cls):
        return {
            "prefix": f"test/{''.join(random.choices(string.ascii_letters + string.digits, k=10))}",
            "opportunity": ["user"],
        }

    @pytest.mark.asyncio
    async def test_create_visibility_group(self, test_client):
        data = self.create_object()
        response = test_client.post(self.url, headers={"Authorization": f"Bearer {pytest.test_token}"}, json=data)
        assert response.status_code == 200
        pytest.test_visibility_group_id = response.json()["data"]["id"]

    @pytest.mark.asyncio
    async def test_get_list(self, test_client):
        response = test_client.get(
            f"{self.url}/list?page=1&size=100",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
        )
        assert response.status_code == 200

    # @pytest.mark.asyncio
    # async def test_validate(self, test_client):
    #     response = test_client.get(
    #         f"{self.url}/validate/opportunity",
    #         headers={"Authorization": f"Bearer {pytest.test_token}"},
    #     )
    #     assert response.status_code == 200
    # У Юзера нет висибилити группы

    @pytest.mark.asyncio
    async def test_get(self, test_client):
        response = test_client.get(
            f"{self.url}/{pytest.test_visibility_group_id}",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update(self, test_client):
        response = test_client.patch(
            f"{self.url}/{pytest.test_visibility_group_id}",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
            data=json.dumps({"prefix": "test/sub_test_test",
                            "opportunity": ["user"]}))
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete(self, test_client):
        response = test_client.delete(f"{self.url}/{pytest.test_visibility_group_id}", headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_settings(self, test_client):
        response = test_client.get(f"{self.url}/settings", headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200
