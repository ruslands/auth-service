import json
import pytest


@pytest.mark.usefixtures("test_client", "test_basic", "test_create_role")
class TestRole:

    def test_get_roles_list(self, test_client):
        response = test_client.get("/api/auth/v1/role/list?page=1&size=100",
                                   headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    def test_get_role_by_id(self, test_client):
        response = test_client.get(
            f"/api/auth/v1/role/{pytest.test_role_id}", headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    def test_update_role(self, test_client):
        response = test_client.patch(f"/api/auth/v1/role/{pytest.test_role_id}",
                                     headers={"Authorization": f"Bearer {pytest.test_token}"},
                                     data=json.dumps({"name": "test_role_updated"}))
        assert response.status_code == 200

    def test_delete_role(self, test_client):
        response = test_client.delete(
            f"/api/auth/v1/role/{pytest.test_role_id}", headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200
        delattr(pytest, "test_role_id")
