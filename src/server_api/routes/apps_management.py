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
    users.append(User(data=user_data))

  logic.update_users(course, users)

  course = logic.get_course_data(g.course_id)
  return {"course_data": course.to_dict()}, 200


@ep_app_verified.route("/update_essensials", methods=["PUT"])
def app_update_essensials():
  logic: Logic = current_app.config['logic']
  
  if "channel_id" not in request.json and "started_at" not in request.json:
    raise BadRequest("no needed fields to update")

  logic.update_essensials(g.course_id, request.json["channel_id"], datetime_from_str(request.json["started_at"]))

  return {}, 200


@ep_app_verified.route("/set_events_published", methods=["PUT"])
def app_set_events_published():
  logic: Logic = current_app.config['logic']
  
  if "event_ids" not in request.json:
    raise BadRequest("no event_ids to set published")

  logic.set_events_published(g.course_id, request.json["event_ids"])

  return {}, 200


@ep_app_verified.route("/update_events", methods=["PUT"])
def app_update_events():
  logic: Logic = current_app.config['logic']
  course = logic.get_course_data(g.course_id)
  
  if "events" not in request.json:
    raise BadRequest("not found field: events")
  
  events_list = request.json["events"]

  if len(events_list) == 0:
    raise BadRequest("empty field: events")

  events_new: list[Event] = []
  events_update: list[Event] = []
  for event_data in events_list:
    event = get_event_from_dict(event_data)
    if event.id == 0:
      events_new.append(event)
    else:
      events_update.append(event)

  logic.add_events(g.course_id, events_new)
  logic.update_events(g.course_id, events_update)

  course = logic.get_course_data(g.course_id)
  return {"course_data": course.to_dict()}, 200


@ep_app_verified.route("/remove_events", methods=["DELETE"])
def app_remove_events():
  logic: Logic = current_app.config['logic']
  course = logic.get_course_data(g.course_id)
  
  if "events" not in request.json:
    raise BadRequest("not found field: events")
  
  events_list = request.json["events"]

  if len(events_list) == 0:
    raise BadRequest("empty field: events")

  events_to_remove: list[Event] = []
  for event_data in events_list:
    event = get_event_from_dict(event_data)
    if event.id == 0:
      continue
    else:
      events_to_remove.append(event)

  logic.remove_events(g.course_id, events_to_remove)

  course = logic.get_course_data(g.course_id)
  return {"course_data": course.to_dict()}, 200


@ep_app_verified.route("/put_event_submition", methods=["POST"])
def app_put_event_submition():
  logic: Logic = current_app.config['logic']
  course = logic.get_course_data(g.course_id)

  if "event_id" not in request.json:
    raise BadRequest("not found field: event_id")
  if "user_id" not in request.json:
    raise BadRequest("not found field: user_id")
  if "submition" not in request.json:
    raise BadRequest("not found field: submition")
  
  result = logic.put_event_submition(course, request.json["event_id"], request.json["user_id"], request.json["submition"], request.json.get("result", None))
  return {"result": result}, 200

