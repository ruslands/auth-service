import json
import pytest


@pytest.mark.usefixtures("test_client", "test_basic", "test_create_role", "test_create_resource")
class TestPermission:

    def test_create_permission(self, test_client):
        response = test_client.post("/api/auth/v1/permission",
                                    headers={"Authorization": f"Bearer {pytest.test_token}"},
                                    data=json.dumps({
                                        "resource_id": pytest.test_resource_id,
                                        "role_id": pytest.test_role_id,
                                        "name": "test",
                                        "description": "get all test"
                                    }))
        assert response.status_code == 200
        pytest.test_permission_id = response.json()["data"]["id"]

    def test_get_permissions_list(self, test_client):
        response = test_client.get("/api/auth/v1/permission/list?page=1&size=100",
                                   headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    def test_get_permission_by_id(self, test_client):
        response = test_client.get(f"/api/auth/v1/permission/{pytest.test_permission_id}", headers={
                                   "Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    def test_update_permission(self, test_client):
        response = test_client.patch(f"/api/auth/v1/permission/{pytest.test_permission_id}", 
        headers={"Authorization": f"Bearer {pytest.test_token}"},
        data=json.dumps({"name": "test_test"}))
        assert response.status_code == 200

    def test_delete_permission(self, test_client):
        response = test_client.delete(f"/api/auth/v1/permission/{pytest.test_permission_id}", headers={
                                      "Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200
        delattr(pytest, "test_permission_id")
