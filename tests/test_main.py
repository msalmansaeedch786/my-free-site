import pytest
from main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_homepage_loads(client):
    """Test that the homepage loads successfully and contains the expected title."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Connection Identity" in response.data


def test_user_agent_parsing(client):
    """Test that the user agent is parsed and displayed correctly."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = client.get("/", headers=headers)
    assert response.status_code == 200
    assert b"Chrome 120.0.0" in response.data
    assert b"Mac OS X 10.15.7" in response.data
