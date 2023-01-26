import json
import pytest


@pytest.mark.usefixtures("test_client", "test_basic", "test_create_team")
class TestTeam:

    def test_get_teams_list(self, test_client):
        response = test_client.get("/api/auth/v1/team/list?page=1&size=100",
                                   headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    def test_get_team_by_id(self, test_client):
        response = test_client.get(
            f"/api/auth/v1/team/{pytest.test_team_id}", headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200

    def test_update_team(self, test_client):
        response = test_client.patch(f"/api/auth/v1/team/{pytest.test_team_id}",
                                     headers={"Authorization": f"Bearer {pytest.test_token}"},
                                     data=json.dumps({"name": "test team test"}))
        assert response.status_code == 200

    def test_delete_team(self, test_client):
        response = test_client.delete(
            f"/api/auth/v1/team/{pytest.test_team_id}", headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200
        delattr(pytest, "test_team_id")
