import json
import pytest
from datetime import datetime

hostname = "hostname"


@pytest.mark.usefixtures("test_client")
class Test:
    url = "api/auth/v1/auth"

    @pytest.mark.asyncio
    async def test_basic(self, test_client):
        if pytest.expires_at < int(datetime.timestamp(datetime.now())):
            response = test_client.post(
                f"{self.url}/basic", data={
                    "username": pytest.test_username,
                    "password": pytest.test_password
                })
            assert response.status_code == 201
            pytest.test_refresh_token = response.json()[
                "data"]["refresh_token"]
            pytest.test_token = response.json()["data"]["access_token"]
            pytest.expires_at = response.json()["data"]["expires_at"]

    @pytest.mark.asyncio
    async def test_refresh(self, test_client):
        response = test_client.post(
            f"{self.url}/refresh-token",
            data=json.dumps({"refresh_token": pytest.test_refresh_token}),
        )
        assert response.status_code == 201
        pytest.test_token = response.json()["data"]["access_token"]

    @pytest.mark.asyncio
    async def test_google(self, test_client):
        response = test_client.get(
            f"{self.url}/google?redirect_enable=false",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
        )
        assert response.status_code == 303

    # @pytest.mark.asyncio
    # async def test_keycloak(self, test_client):
    #     response = test_client.get(
    #         f"{self.url}/keycloak?redirect_enable=false",
    #         headers={"Authorization": f"Bearer {pytest.test_token}"},
    #     )
    #     assert response.status_code == 303

    # @pytest.mark.asyncio
    # async def test_logout(self, test_client):
    #     await self.test_refresh(test_client)
    #     response = test_client.get(
    #         "/api/auth/v1/auth/logout",
    #         headers={"Authorization": f"Bearer {pytest.test_token}"},
    #     )
    #     await self.test_basic(test_client=test_client)
    #     await self.test_refresh(test_client=test_client)
    #     assert response.status_code == 200

        # delattr(pytest, "test_token")
