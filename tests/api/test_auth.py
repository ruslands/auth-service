import json
import pytest

hostname = "hostname"

@pytest.mark.usefixtures("test_client", "test_basic")
class TestAuth:

    def test_refresh(self, test_client):
        response = test_client.post(f"/api/auth/v1/auth/refresh-token",
                                    data=json.dumps({"refresh_token": pytest.test_refresh_token}))
        assert response.status_code == 201
        pytest.test_token = response.json()["data"]["access_token"]

    def test_google(self, test_client):
        response = test_client.get("/api/auth/v1/auth/google?redirect_enable=false",
                                   headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 303

    def test_token(self, test_client):
        response = test_client.get(f"/api/auth/v1/auth/token",
                                   headers={"Authorization": f"Bearer {pytest.test_token}"},
                                   params={
                                       "code": "4/0ARtbsJpwaSlWbCdZ9ynf639_518UYHVL88ZK9o4zPTU_OvBEwTPxR3VXTaD_IJCoDwEDoQ",
                                       "scope": "email%20profile%20openid%20https://www.googleapis.com/auth/userinfo.email%20https://www.googleapis.com/auth/userinfo.profile",
                                       "authuser": "0",
                                       "hd": hostname,
                                       "prompt": "consent",
                                   })
        assert response.status_code == 400

    def test_logout(self, test_client):
        response = test_client.get(f"/api/auth/v1/auth/logout",
                                   headers={"Authorization": f"Bearer {pytest.test_token}"})
        assert response.status_code == 200
        delattr(pytest, "test_token")
