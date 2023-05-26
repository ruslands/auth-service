import json
import pytest
import string
import random
from tests.api.test_role import Test as TestRole
from tests.api.test_team import Test as TestTeam


@pytest.mark.usefixtures("test_client")
class Test:
    url = "/api/auth/v1/user"
    role = TestRole()
    team = TestTeam()

    @classmethod
    def create_object(cls):
        return {
            "first_name": ''.join(random.choices(string.ascii_letters + string.digits, k=10)),
            "last_name": ''.join(random.choices(string.ascii_letters + string.digits, k=10)),
            "full_name": ''.join(random.choices(string.ascii_letters + string.digits, k=10)),
            "email": f"{''.join(random.choices(string.ascii_letters + string.digits, k=10))}@hostname.com",
        }

    @pytest.mark.asyncio
    async def test_get_my_data(self, test_client):
        response = test_client.get(self.url, headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create(self, test_client):
        data = self.create_object()
        await self.role.test_create(test_client)
        await self.team.test_create(test_client)
        response = test_client.post(self.url, headers={"Authorization": f"Bearer {pytest.test_token}"}, json=data)
        assert response.status_code == 200
        pytest.test_user_id = response.json()["data"]["id"]

    @pytest.mark.asyncio
    async def test_get_list(self, test_client):
        response = test_client.get(f"{self.url}/list?page=1&size=100", headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get(self, test_client):
        response = test_client.get(f"{self.url}/{pytest.test_user_id}", headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update(self, test_client):
        response = test_client.patch(
            f"{self.url}/{pytest.test_user_id}",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
            data=json.dumps(
                {
                    "is_active": True,
                    "is_staff": False,
                    "is_superuser": False,
                    "allow_basic_login": False,
                }
            ),
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_role(self, test_client):
        # add role
        response = test_client.patch(
            f"{self.url}/{pytest.test_user_id}/role/{pytest.test_role_id}",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
        )
        assert response.status_code == 200
        # remove role
        response = test_client.patch(
            f"{self.url}/{pytest.test_user_id}/role/{pytest.test_role_id}",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_team(self, test_client):
        # add to team
        response = test_client.patch(
            f"{self.url}/{pytest.test_user_id}/team/{pytest.test_team_id}",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
        )
        assert response.status_code == 200
        # remove from team
        response = test_client.patch(
            f"{self.url}/{pytest.test_user_id}/team/{pytest.test_team_id}",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete(self, test_client):
        response = test_client.delete(
            f"{self.url}/{pytest.test_user_id}",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
        )
        assert response.status_code == 200
