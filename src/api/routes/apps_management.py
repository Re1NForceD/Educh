from flask import Blueprint, jsonify, current_app, request
import logging
import base64
from werkzeug.exceptions import BadRequest, Unauthorized

logger = logging.getLogger()

verified_apps = dict() # session key = course_id


ep_app = Blueprint("app", __name__)
ep_app_verified = Blueprint("app", __name__, url_prefix="/app")
ep_app.register_blueprint(ep_app_verified)

@ep_app.route("/verify", methods=["PUT"])
def verify():
  if "auth_key" not in request.json:
    raise BadRequest("not found field: auth_key") 
  
  # mock_key = base64.b64encode("1+dGVzdF9jb3Vyc2U=".encode('utf-8'), altchars=b"()")  
  course_id_str, auth_key = base64.b64decode(request.json["auth_key"].encode('utf-8'), altchars=b"()").decode('utf-8').split("+")
  course_id = int(course_id_str)

  logic = current_app.config['logic']

  course_name = logic.verify_app(course_id, auth_key)

  if not course_name:
    raise Unauthorized("invalid app creds")

  logger.info(f"app for course {course_id_str} is verified")
  # TODO: generate session key for app
  return jsonify({"status": "success", "name": course_name}), 200


@ep_app_verified.before_request
def check_auth():
  logger.info(f"check auth with {request.json}")
  return {"status": "mocked"}, 204
  

@ep_app_verified.route("/test", methods=["GET"])
def app_test():
  logger.info("app_test ep")
