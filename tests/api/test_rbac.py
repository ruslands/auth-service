import json
import pytest


@pytest.mark.usefixtures("test_client")
class Test:
    url = "api/auth/v1/rbac"

    @pytest.mark.asyncio
    async def test_get(self, test_client):
        response = test_client.get(
            self.url,
            headers={"Authorization": f"Bearer {pytest.test_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_validate(self, test_client):
        response = test_client.post(
            f"{self.url}/validate",
            headers={"Authorization": f"Bearer {pytest.test_token}"},
            data=json.dumps(
                {"method": "get", "endpoint": "/api/auth/v1/test"}),
        )
        assert response.status_code == 200
