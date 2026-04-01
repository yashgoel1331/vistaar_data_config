"""Flask app bootstrap for modular routes/services config backend."""

from __future__ import annotations

from flask import Flask
from flask_cors import CORS

from Utils.db import init_db
from Utils.config_loader import load_configs_to_memory
from Utils.routes.aliases_routes import init_aliases_routes
from Utils.routes.config_routes import init_config_routes
from Utils.services.config_api_service import ConfigAPIService

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

init_db()
load_configs_to_memory()

service = ConfigAPIService()
app.register_blueprint(init_config_routes(service))
app.register_blueprint(init_aliases_routes(service))

if __name__ == "__main__":
    app.run(debug=True)
