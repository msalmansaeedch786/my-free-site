import pytest
from main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ──────────────────────────────────────────────
# Homepage Tests
# ──────────────────────────────────────────────


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


# ──────────────────────────────────────────────
# Health Check Tests
# ──────────────────────────────────────────────


def test_health_endpoint(client):
    """Test that the /health endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.data == b"ok"


# ──────────────────────────────────────────────
# JSON API Tests
# ──────────────────────────────────────────────


def test_json_endpoint(client):
    """Test that the /json endpoint returns valid JSON with all fields."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    }
    response = client.get("/json", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "ip_address" in data
    assert "browser" in data
    assert "os_name" in data
    assert "device" in data
    assert "Chrome" in data["browser"]
    assert "Windows" in data["os_name"]


def test_json_content_type(client):
    """Test that /json returns application/json content type."""
    response = client.get("/json")
    assert response.content_type == "application/json"


# ──────────────────────────────────────────────
# IP Parsing Tests
# ──────────────────────────────────────────────


def test_x_forwarded_for_single_ip(client):
    """Test that X-Forwarded-For with a single IP is parsed correctly."""
    headers = {"X-Forwarded-For": "203.0.113.50"}
    response = client.get("/json", headers=headers)
    data = response.get_json()
    assert data["ip_address"] == "203.0.113.50"


def test_x_forwarded_for_multiple_ips(client):
    """Test that ProxyFix correctly extracts the last appended IP (from the trusted proxy)."""
    headers = {"X-Forwarded-For": "203.0.113.50, 70.41.3.18, 150.172.238.178"}
    response = client.get("/json", headers=headers)
    data = response.get_json()
    assert data["ip_address"] == "150.172.238.178"


def test_no_forwarded_for_header(client):
    """Test fallback to remote_addr when X-Forwarded-For is absent."""
    response = client.get("/json")
    data = response.get_json()
    # Flask test client uses 127.0.0.1 by default
    assert data["ip_address"] == "127.0.0.1"


# ──────────────────────────────────────────────
# Edge Cases: User-Agent Parsing
# ──────────────────────────────────────────────


def test_empty_user_agent(client):
    """Test that an empty User-Agent string results in 'Unknown' values."""
    headers = {"User-Agent": ""}
    response = client.get("/json", headers=headers)
    data = response.get_json()
    assert response.status_code == 200
    assert data["browser"] == "Other"
    assert data["device"] == "Other"


def test_bot_user_agent(client):
    """Test that a bot User-Agent is parsed without errors."""
    headers = {"User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"}
    response = client.get("/json", headers=headers)
    data = response.get_json()
    assert response.status_code == 200
    assert "Googlebot" in data["browser"]


def test_malformed_user_agent(client):
    """Test that a completely malformed User-Agent doesn't crash the app."""
    headers = {"User-Agent": "x" * 5000}
    response = client.get("/json", headers=headers)
    assert response.status_code == 200


def test_unicode_user_agent(client):
    """Test that unicode characters in User-Agent are handled gracefully."""
    headers = {"User-Agent": "Mozilla/5.0 (🤖 RoboAgent/1.0)"}
    response = client.get("/json", headers=headers)
    assert response.status_code == 200


# ──────────────────────────────────────────────
# Security Header Tests
# ──────────────────────────────────────────────


def test_csp_header_present(client):
    """Test that Content-Security-Policy header is set."""
    response = client.get("/")
    assert "Content-Security-Policy" in response.headers
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]


def test_hsts_header_present(client):
    """Test that Strict-Transport-Security header is set."""
    response = client.get("/")
    assert (
        response.headers.get("Strict-Transport-Security")
        == "max-age=31536000; includeSubDomains"
    )


def test_x_content_type_options(client):
    """Test that X-Content-Type-Options header is set to nosniff."""
    response = client.get("/")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"


def test_x_frame_options(client):
    """Test that X-Frame-Options header is set to DENY."""
    response = client.get("/")
    assert response.headers.get("X-Frame-Options") == "DENY"


def test_security_headers_on_all_routes(client):
    """Test that security headers are present on all routes."""
    for route in ["/", "/health", "/json"]:
        response = client.get(route)
        assert "X-Content-Type-Options" in response.headers, f"Missing on {route}"


# ──────────────────────────────────────────────
# 404 Test
# ──────────────────────────────────────────────


def test_404_page(client):
    """Test that non-existent routes return 404."""
    response = client.get("/nonexistent")
    assert response.status_code == 404
