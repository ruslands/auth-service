import json
import pytest


@pytest.mark.usefixtures("test_client", "test_basic", "test_create_role", "test_create_team")
class TestUser:

    def test_get_my_data(self, test_client):
        response = test_client.get(
            f"/api/auth/v1/user", headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    def test_create_user(self, test_client):
        response = test_client.post("/api/auth/v1/user",
                                    headers={"Authorization": f"Bearer {pytest.test_token}"},
                                    data=json.dumps({
                                        "first_name": "test",
                                        "last_name": "test",
                                        "full_name": "test test",
                                        "email": "test.test@hostname.com",
                                        "phone": "",
                                        "country": "",
                                        "city": "",
                                        "title": "",
                                        "region": ["poland"]
                                    }))
        assert response.status_code == 200
        pytest.test_user_id = response.json()["data"]["id"]

    def test_get_users_list(self, test_client):
        response = test_client.get("/api/auth/v1/user/list?page=1&size=100",
                                   headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    def test_get_user_by_id(self, test_client):
        response = test_client.get(
            f"/api/auth/v1/user/{pytest.test_user_id}", headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    def test_update_user(self, test_client):
        response = test_client.patch(f"/api/auth/v1/user/{pytest.test_user_id}",
                                     headers={"Authorization": f"Bearer {pytest.test_token}"},
                                     data=json.dumps({
                                         "is_active": True,
                                         "is_staff": False,
                                         "is_superuser": False,
                                         "allow_basic_login": False
                                     }))
        assert response.status_code == 200

    def test_update_user_role(self, test_client):
        # add role
        response = test_client.patch(f"/api/auth/v1/user/{pytest.test_user_id}/role/{pytest.test_role_id}", headers={
                                     "Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200
        # remove role
        response = test_client.patch(f"/api/auth/v1/user/{pytest.test_user_id}/role/{pytest.test_role_id}", headers={
                                     "Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    def test_update_user_team(self, test_client):
        # add to team
        response = test_client.patch(f"/api/auth/v1/user/{pytest.test_user_id}/team/{pytest.test_team_id}", headers={
                                     "Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200
        # remove from team
        response = test_client.patch(f"/api/auth/v1/user/{pytest.test_user_id}/team/{pytest.test_team_id}", headers={
                                     "Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    def test_delete_user_by_id(self, test_client):
        response = test_client.delete(
            f"/api/auth/v1/user/{pytest.test_user_id}", headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200
