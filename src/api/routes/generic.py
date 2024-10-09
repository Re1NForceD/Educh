from flask import Blueprint, jsonify, current_app, json
from werkzeug.exceptions import HTTPException
import logging
from api.routes.apps_management import ep_app

logger = logging.getLogger()

ep_base = Blueprint("base", __name__)
ep_base.register_blueprint(ep_app)

def handle_http_exception(e):
    response = e.get_response()
    response.content_type = "application/json"
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    return response

def handle_other_exception(e):
    return e # TODO: remove after testing
    response = json.dumps({
        "description": (e.args if current_app.config["CONFIGURATION"] == "debug" else "internal error"),
    })
    return response, 500

@ep_base.errorhandler(Exception)
def handle_exception(e):
  if isinstance(e, HTTPException):
    return handle_http_exception(e)

  return handle_other_exception(e)


@ep_base.route("/health", methods=["GET"])
def health():
  raise Exception("shish")
  return ""
