import os
import json
import pytest
from datetime import datetime
from fastapi.testclient import TestClient

if "AWS_KODIT_AUTH_SECRETS_MANAGER_ARN" not in os.environ and "AWS_JWT_AUTH_SECRETS_MANAGER_ARN" not in os.environ:
    os.environ['AWS_KODIT_AUTH_SECRETS_MANAGER_ARN'] = "arn:aws:secretsmanager:eu-central-1:131469615986:secret:KoditAuthSecret-dev-FpWzXN"
    os.environ['AWS_JWT_AUTH_SECRETS_MANAGER_ARN'] = "arn:aws:secretsmanager:eu-central-1:131469615986:secret:JwtAuthSecret-dev-ODz358"

from app.main import app

pytest.test_username = "ruslan.konovalov@kodit.io"
pytest.test_password = "WBYGtuUhhFbyxpi"
pytest.expires_at = 0


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_basic(test_client):
    if not hasattr(pytest, "test_token") or pytest.expires_at < int(datetime.timestamp(datetime.now())):
        response = test_client.post(
            "/api/auth/v1/auth/basic", data={"username": pytest.test_username, "password": pytest.test_password})
        assert response.status_code == 201
        pytest.test_refresh_token = response.json()["data"]["refresh_token"]
        pytest.test_token = response.json()["data"]["access_token"]
        pytest.expires_at = response.json()["data"]["expires_at"]


@pytest.fixture
def test_create_visibility_group(test_client):
    if not hasattr(pytest, "test_visibility_group_id"):
        response = test_client.post("/api/auth/v1/visibility_group",
                                    headers={"Authorization": f"Bearer {pytest.test_token}"},
                                    data=json.dumps({
                                        "prefix": "test/sub_test",
                                        "opportunity": ["user"]
                                    }))
        if response.status_code == 409:
            response = test_client.get("/api/auth/v1/visibility_group/list?page=1&size=100",
                                       headers={"Authorization": f"Bearer {pytest.test_token}"})
            for visibility_group in response.json()["data"]["items"]:
                if visibility_group["prefix"] in ["test/sub_test"]:
                    pytest.test_visibility_group_id = visibility_group["id"]
                    break
        else:
            assert response.status_code == 200
            pytest.test_visibility_group_id = response.json()["data"]["id"]


@pytest.fixture
def test_create_role(test_client):
    if not hasattr(pytest, "test_role_id"):
        response = test_client.post("/api/auth/v1/role", headers={"Authorization": f"Bearer {pytest.test_token}"},
                                    json={
                                        "name": "test_role",
                                        "description": "test_role_description",
                                        "default": False,
        })
        if response.status_code == 409:
            response = test_client.get("/api/auth/v1/role/list?page=1&size=100",
                                       headers={"Authorization": f"Bearer {pytest.test_token}"})
            for role in response.json()["data"]["items"]:
                if role["name"] in ["test_role", "test_role_updated"]:
                    pytest.test_role_id = role["id"]
                    break
        else:
            assert response.status_code == 200
            pytest.test_role_id = response.json()["data"]["id"]


@pytest.fixture
def test_create_resource(test_client):
    if not hasattr(pytest, "test_resource_id"):
        response = test_client.post("/api/auth/v1/resource",
                                    headers={"Authorization": f"Bearer {pytest.test_token}"},
                                    data=json.dumps({
                                        "endpoint": "/api/auth/v1/test",
                                        "method": "get",
                                        "description": "get all test",
                                        "rbac_enable": True,
                                        "visibility_group_enable": False
                                    }))
        if response.status_code == 409:
            response = test_client.get("/api/auth/v1/resource/list?page=1&size=100",
                                       headers={"Authorization": f"Bearer {pytest.test_token}"})
            for resource in response.json()["data"]["items"]:
                if resource["endpoint"] == "/api/auth/v1/test":
                    pytest.test_resource_id = resource["id"]
                    break
        else:
            assert response.status_code == 200
            pytest.test_resource_id = response.json()["data"]["id"]


@pytest.fixture
def test_create_team(test_client):
    if not hasattr(pytest, "test_team_id"):
        response = test_client.post("/api/auth/v1/team",
                                    headers={"Authorization": f"Bearer {pytest.test_token}"},
                                    data=json.dumps({"name": "test_team"}))
        if response.status_code == 409:
            response = test_client.get("/api/auth/v1/team/list?page=1&size=100",
                                       headers={"Authorization": f"Bearer {pytest.test_token}"})
            for team in response.json()["data"]["items"]:
                if team["name"] == "test_team":
                    pytest.test_team_id = team["id"]
                    break
        else:
            assert response.status_code == 200
            pytest.test_team_id = response.json()["data"]["id"]
