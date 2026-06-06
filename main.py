import logging
import os

from flask import Flask, jsonify, request, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
from user_agents import parse

# Configure structured logging for Cloud Run
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


@app.after_request
def set_security_headers(response):
    """Add security headers to every response."""
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' https://fonts.googleapis.com; "
        "font-src https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "script-src 'self';"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    return response


def _get_client_ip():
    """Get the client IP (ProxyFix correctly sets request.remote_addr)."""
    return request.remote_addr


def _parse_connection_info():
    """Parse the visitor's connection details from request headers."""
    user_ip = _get_client_ip()
    user_agent_string = request.headers.get("User-Agent", "")

    try:
        user_agent = parse(user_agent_string)
        browser = user_agent.browser.family or "Unknown"
        browser_version = user_agent.browser.version_string
        os_name = user_agent.os.family or "Unknown"
        os_version = user_agent.os.version_string
        device = user_agent.device.family or "Unknown"
    except Exception:
        logger.warning("Failed to parse User-Agent: %s", user_agent_string)
        browser = "Unknown"
        browser_version = ""
        os_name = "Unknown"
        os_version = ""
        device = "Unknown"

    return {
        "ip_address": user_ip,
        "browser": f"{browser} {browser_version}".strip(),
        "os_name": f"{os_name} {os_version}".strip(),
        "device": device,
    }


@app.route("/health")
def health():
    """Lightweight health check endpoint for Cloud Run probes."""
    return "ok", 200


@app.route("/")
def hello():
    """Render the connection identity page."""
    info = _parse_connection_info()
    logger.info("Request from %s — %s", info["ip_address"], info["browser"])
    return render_template("index.html", **info)


@app.route("/json")
def json_info():
    """Return connection identity as JSON — useful as a programmatic API."""
    info = _parse_connection_info()
    logger.info("API request from %s", info["ip_address"])
    return jsonify(info)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return (
        render_template(
            "index.html", ip_address="—", browser="—", os_name="—", device="—"
        ),
        404,
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle unexpected server errors."""
    logger.error("Internal server error: %s", error)
    return "Something went wrong", 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
