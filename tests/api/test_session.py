import pytest
from tests.api.test_auth import Test as TestAuth


@pytest.mark.usefixtures("test_client")
class Test:
    url = "api/auth/v1/sessions"
    auth = TestAuth()

    @pytest.mark.asyncio
    async def test_get_list(self, test_client):
        response = test_client.get(
            f"{self.url}/list?page=1&size=100",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
        )
        assert response.status_code == 200
        if len(response.json()["data"]) > 0:
            pytest.test_session_id = response.json()["data"]["items"][0]["id"]

    # @pytest.mark.asyncio
    # async def test_delete(self, test_client):
    #     response = test_client.delete(
    #         f"{self.url}/{pytest.test_session_id}",
    #         headers={"Authorization": f"Bearer {pytest.test_token}"},
    #     )
    #     assert response.status_code == 200
    #     await self.auth.test_basic(test_client=test_client)
        # delattr(pytest, "test_token")
