import json
import pytest


@pytest.mark.usefixtures("test_client", "test_basic")
class TestRBAC:

    def test_get_rbac_settings(self, test_client):
        response = test_client.get(
            "/api/auth/v1/rbac", headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    def test_validate(self, test_client):
        response = test_client.post(f"/api/auth/v1/rbac/validate",
                                    headers={"Authorization": f"Bearer {pytest.test_token}"},
                                    data=json.dumps({
                                        "method": "get",
                                        "endpoint": "/api/auth/v1/test"
                                    }))
        assert response.status_code == 200
