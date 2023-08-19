# app.py

from flask import Flask
from lucidserver.endpoints import register_endpoints
from agentlogger import print_header

app = Flask(__name__)

print_header("LUCID JOURNAL", font="slant", color="cyan")

# Register the endpoints with the app
register_endpoints(app)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)