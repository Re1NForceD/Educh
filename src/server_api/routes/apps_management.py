from flask import Blueprint, jsonify, current_app, request
import logging
import base64
import uuid
from werkzeug.exceptions import BadRequest, Unauthorized

logger = logging.getLogger()

k_c_apps = dict() # session key = course_id
c_k_apps = dict() # course_id = session key


ep_app = Blueprint("app", __name__)
ep_app_verified = Blueprint("app_verified", __name__, url_prefix="/app")
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

  session_key = uuid.uuid4()
  k_c_apps[session_key] = course_id # session key = course_id
  c_k_apps[course_id] = session_key # course_id = session key

  return jsonify({"id": course_id, "name": course_name, "session_key": session_key}), 200


@ep_app_verified.before_request
def check_auth():
  logger.info(f"k_c_apps: {k_c_apps}, c_k_apps: {c_k_apps}")
  try:
    session_key = uuid.UUID(request.headers.get("Session-Key", ""))
    if session_key not in k_c_apps:
      raise Exception("unknown session key")
  except Exception as e:
    logger.error(f"got exception: {e}")
    raise Unauthorized("unknown app")
  

@ep_app_verified.route("/test", methods=["GET"])
def app_test():
  logger.info("app_test ep")
  return "", 204
