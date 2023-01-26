import json
import pytest


@pytest.mark.usefixtures("test_client", "test_basic")
class TestSession:

    def test_get_sessions_list(self, test_client):
        response = test_client.get("/api/auth/v1/sessions/list?page=1&size=100",
                                   headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200
        if len(response.json()["data"]) > 0:
            pytest.test_session_id = response.json()["data"]["items"][0]["id"]

    def test_delete_session_by_id(self, test_client):
        response = test_client.delete(f"/api/auth/v1/sessions/{pytest.test_session_id}", headers={
                                      "Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200
        delattr(pytest, "test_token")
