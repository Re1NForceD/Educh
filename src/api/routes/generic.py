from flask import Blueprint, jsonify, current_app, json
from werkzeug.exceptions import HTTPException
import logging
from api.routes.apps_management import ep_app

logger = logging.getLogger()

ep_base = Blueprint("base", __name__)
ep_base.register_blueprint(ep_app)

def handle_http_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

@ep_base.errorhandler(Exception)
def handle_exception(e):
  logger.info("handle_exception")
  if isinstance(e, HTTPException):
      return handle_http_exception(e)

  if current_app.config["CONFIGURATION"] == "debug":
    return {"error": e}, 500
  else:
    return {"error": "internal error"}, 500


@ep_base.route("/health", methods=["GET"])
def health():
  return jsonify({"status": "healthy"})
