from flask import Blueprint, jsonify, current_app, request, g
import logging
import base64
import uuid
from werkzeug.exceptions import BadRequest, Unauthorized, Locked

from course_classes import *
from server_logic import *

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

  course = logic.get_course_data(course_id)

  return jsonify({"course_data": course.to_dict(), "session_key": session_key}), 200


@ep_app_verified.before_request
def check_auth():
  try:
    session_key = uuid.UUID(request.headers.get("Session-Key", ""))
    if session_key not in k_c_apps:
      raise BadRequest("unknown session key")
    g.course_id = k_c_apps[session_key]
  except Exception as e:
    logger.error(f"got exception: {e}")
    raise Unauthorized("unknown app")


@ep_app_verified.route("/update_users", methods=["POST"])
def app_update_users():
  logic: Logic = current_app.config['logic']
  course = logic.get_course_data(g.course_id)
  
  if "users" not in request.json:
    raise BadRequest("not found field: users")
  
  users_list = request.json["users"]

  if len(users_list) == 0:
    raise BadRequest("empty field: users")

  users = []
  for user_data in users_list:
    user = User(data=user_data)
    if not course.is_user_id_exists(user.platform_id): # TODO update existed users
      users.append(user)

  logic.update_users(g.course_id, users)

  course = logic.get_course_data(g.course_id)
  return {"course_data": course.to_dict()}, 200


@ep_app_verified.route("/update_essensials", methods=["PUT"])
def app_update_essensials():
  logic: Logic = current_app.config['logic']
  
  if "channel_id" not in request.json and "start_date" not in request.json:
    raise BadRequest("no needed fields to update")

  logic.update_essensials(g.course_id, request.json["channel_id"], datetime_from_str(request.json["start_date"]))

  return {}, 200
