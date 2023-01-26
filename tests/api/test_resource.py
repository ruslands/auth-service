import json
import pytest

@pytest.mark.usefixtures("test_client", "test_basic", "test_create_resource")
class TestResource:

    def test_get_resources_list(self, test_client):
        response = test_client.get("/api/auth/v1/resource/list?page=1&size=100", headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    def test_get_resource_by_id(self, test_client):
        response = test_client.get(f"/api/auth/v1/resource/{pytest.test_resource_id}", headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    def test_update_resource(self, test_client):
        response = test_client.patch(f"/api/auth/v1/resource/{pytest.test_resource_id}", 
        headers={"Authorization": f"Bearer {pytest.test_token}"},
        data=json.dumps({
            "endpoint": "/api/auth/v1/test_test",
            "method": "post"}))
        assert response.status_code == 200

    def test_delete_resource(self, test_client):
        response = test_client.delete(f"/api/auth/v1/resource/{pytest.test_resource_id}", headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200
        delattr(pytest, "test_resource_id")