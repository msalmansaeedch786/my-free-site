from flask import Flask, request, render_template
import os
from user_agents import parse

app = Flask(__name__)

@app.route('/')
def hello():
    # Cloud Run passes the real user IP in the X-Forwarded-For header
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent_string = request.headers.get('User-Agent', '')
    user_agent = parse(user_agent_string)
    
    browser = user_agent.browser.family
    browser_version = user_agent.browser.version_string
    os_name = user_agent.os.family
    os_version = user_agent.os.version_string
    device = user_agent.device.family
    
    # Clean up empty strings
    if not browser: browser = "Unknown"
    if not os_name: os_name = "Unknown"
    if not device: device = "Unknown"

    return render_template(
        'index.html',
        ip_address=user_ip,
        browser=f"{browser} {browser_version}".strip(),
        os_name=f"{os_name} {os_version}".strip(),
        device=device
    )

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
