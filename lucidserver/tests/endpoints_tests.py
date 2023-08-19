import sys
sys.path.append('.')

from unittest.mock import patch
from lucidserver.app import app
from lucidserver.endpoints.main import *
import pytest
import json

# Placeholder for test user email
test_user_email = "test@example.com"

# Sample JWT token for testing
test_token = f"Bearer test_token_for_{test_user_email}"

# Sample dream args for testing
dream_args = {
    "title": "Test Dream",
    "date": "2021-10-10",
    "entry": "A dream about testing",
    "id_token": "sample_token"
}

# Ensure that the dream with id 1 exists in the mocked data
mocked_dream = {
    "id": 1,
    "metadata": {
        "entry": "test_entry",
        "title": "Test Dream",
        "date": "2021-10-10",
        "useremail": "test@example.com",
        "analysis": "test_analysis",
        "image": "test_image",
    }
}


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# Test create dream endpoint
@patch("lucidserver.endpoints.main.create_dream", return_value={"id": 1})
@patch("lucidserver.endpoints.main.extract_user_email_from_token", return_value=test_user_email)
@patch("lucidserver.endpoints.main.get_dream", return_value=mocked_dream)
def test_create_dream_endpoint(mock_get_dream, mock_extract_user_email_from_token, mock_create_dream, client):
    headers = {"Authorization": test_token}
    response = client.post("/api/dreams", json=dream_args, headers=headers)
    assert response.status_code == 200
    assert response.json["id"] == 1


# Test get dreams endpoint
@patch("lucidserver.endpoints.main.get_dreams", return_value=[{"id": 1}])
@patch("lucidserver.endpoints.main.extract_user_email_from_token", return_value=test_user_email)
@patch("lucidserver.endpoints.main.get_dream", return_value=mocked_dream)
def test_get_dreams_endpoint(mock_get_dream, mock_extract_user_email_from_token, mock_get_dreams, client):
    headers = {"Authorization": test_token}
    response = client.get("/api/dreams", headers=headers)
    assert response.status_code == 200
    assert response.json[0]["id"] == 1


# Test update dream endpoint
@patch("lucidserver.endpoints.main.update_dream_analysis_and_image", return_value={"id": 1, "analysis": "updated_analysis"})
@patch("lucidserver.endpoints.main.extract_user_email_from_token", return_value=test_user_email)
@patch("lucidserver.endpoints.main.get_dream", return_value=mocked_dream)
def test_update_dream_endpoint(mock_get_dream, mock_extract_user_email_from_token, mock_update_dream, client):
    headers = {"Authorization": test_token}
    response = client.put(
        "/api/dreams/1", json={"analysis": "updated_analysis"}, headers=headers)
    assert response.status_code == 200
    assert response.json["analysis"] == "updated_analysis"


# Test get dream endpoint
@patch("lucidserver.endpoints.main.extract_user_email_from_token", return_value=test_user_email)
@patch("lucidserver.endpoints.main.get_dream", return_value=mocked_dream)
def test_get_dream_endpoint(mock_get_dream, mock_extract_user_email_from_token, client):
    headers = {"Authorization": test_token}
    response = client.get("/api/dreams/1", headers=headers)
    assert response.status_code == 200
    assert response.json["metadata"]["title"] == "Test Dream"


# Test get dream analysis endpoint
@patch("lucidserver.endpoints.main.get_dream_analysis", return_value={"analysis": "test_analysis"})
@patch("lucidserver.endpoints.main.extract_user_email_from_token", return_value=test_user_email)
@patch("lucidserver.endpoints.main.get_dream", return_value=mocked_dream)
def test_get_dream_analysis_endpoint(mock_get_dream, mock_extract_user_email_from_token, mock_get_dream_analysis, client):
    headers = {"Authorization": test_token}
    response = client.get("/api/dreams/1/analysis", headers=headers)
    assert response.status_code == 200
    assert response.json["analysis"] == "test_analysis"


# Test get dream image endpoint
@patch("lucidserver.endpoints.main.get_dream_image", return_value="test_image")
@patch("lucidserver.endpoints.main.extract_user_email_from_token", return_value=test_user_email)
@patch("lucidserver.endpoints.main.get_dream", return_value=mocked_dream)
def test_get_dream_image_endpoint(mock_get_dream, mock_extract_user_email_from_token, mock_get_dream_image, client):
    headers = {"Authorization": test_token}
    response = client.get("/api/dreams/1/image", headers=headers)
    assert response.status_code == 200
    assert response.json["image"] == "test_image"


# Test search dreams endpoint
@patch("lucidserver.endpoints.main.search_dreams", return_value=[{"id": 1}])
@patch("lucidserver.endpoints.main.extract_user_email_from_token", return_value=test_user_email)
@patch("lucidserver.endpoints.main.get_dream", return_value=mocked_dream)
def test_search_dreams_endpoint(mock_get_dream, mock_extract_user_email_from_token, mock_search_dreams, client):
    headers = {"Authorization": test_token}
    response = client.post("/api/dreams/search",
                           json={"query": "test_query"}, headers=headers)
    assert response.status_code == 200
    assert response.json[0]["id"] == 1