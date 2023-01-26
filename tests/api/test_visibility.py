import json
import pytest


@pytest.mark.usefixtures("test_client", "test_basic", "test_create_visibility_group")
class TestVisibilityGroup:

    def test_get_visibility_groups_list(self, test_client):
        response = test_client.get("/api/auth/v1/visibility_group/list?page=1&size=100",
                                   headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    def test_get_visibility_group_by_id(self, test_client):
        response = test_client.get(f"/api/auth/v1/visibility_group/{pytest.test_visibility_group_id}", headers={
            "Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    def test_update_visibility_group(self, test_client):
        response = test_client.patch(f"/api/auth/v1/visibility_group/{pytest.test_visibility_group_id}",
                                     headers={"Authorization": f"Bearer {pytest.test_token}"},
                                     data=json.dumps({
                                         "prefix": "test/sub_test_test",
                                         "opportunity": ["user"]
                                     }))
        assert response.status_code == 200

    def test_delete_visibility_group(self, test_client):
        response = test_client.delete(f"/api/auth/v1/visibility_group/{pytest.test_visibility_group_id}", headers={
            "Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    def test_get_visibility_group_settings(self, test_client):
        response = test_client.get(
            "/api/auth/v1/visibility_group/settings", headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    def test_validate(self, test_client):
        response = test_client.get(f"/api/auth/v1/visibility_group/validate/opportunity",
                                    headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200
