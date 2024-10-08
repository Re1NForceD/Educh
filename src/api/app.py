import os
import logging
from flask import Flask
from flask_cors import CORS
from waitress import serve

from api.routes.generic import ep_base
from api.logs import log_request_info, list_registered_blueprints

logger = logging.getLogger()


class FlaskApp:
  def __init__(self, config):
    self.app = Flask(__name__, instance_relative_config=True)

    self._configure_app(config)
    self._setup_cors()
    self._ensure_instance_folder_exists()
    self._register_blueprints()

    logger.info("API initialized")

  def _configure_app(self, config):
    self.app.config.from_mapping(
        CONFIGURATION=os.getenv("EDUCH_CONFIGURATION", "debug").lower(),
        PORT=int(os.getenv("EDUCH_PORT", 9999)),
        SECRET_KEY=os.getenv("EDUCH_SECRET_KEY"),
    )

    self.app.config.from_mapping(config)

    logger.info(f"API config: {self.app.config}")

  def _setup_cors(self):
    CORS(
        self.app,
        supports_credentials=True,
        resources={
            r"/*": {
                "origins": "*",
                "allow_headers": [
                    "Content-Type",
                    "Authorization",
                    "Origin",
                    "X-Requested-With",
                    "Accept",
                ],
                "methods": [
                    "GET",
                    "POST",
                    "PUT",
                    "DELETE",
                    "PATCH",
                ],
            }
        },
    )
    logger.info("CORS enabled")

  def _ensure_instance_folder_exists(self):
    try:
      os.makedirs(self.app.instance_path)
    except OSError:
      pass

  def _register_blueprints(self):
    self.app.before_request(log_request_info)
    self.app.register_blueprint(ep_base)

    list_registered_blueprints(self.app)

  def get_app(self):
    return self.app

  def start(self):
    port = self.app.config["PORT"]

    if self.app.config["CONFIGURATION"] == "debug":
      logger.info("Running in debug mode")
      self.app.run(debug=True, port=port)
    else:
      logger.info("Running in production mode")
      serve(self.app, host="0.0.0.0", port=port)

  def set_logic(self, logic):
    self.logic = logic
    self.app.config['logic'] = logic
