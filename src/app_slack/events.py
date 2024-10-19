from slack_sdk import WebClient

from .home_views import *
from .setup_event_views import *

from app_logic_api import *


def member_join(context, event, client, logger):
  logger.info(f"member_join {event}")
  track_user(event["user"]["id"], context["logic"], client)

def app_home_opened(context, event, client, logger):
  track_user(event["user"], context["logic"], client)

def track_user(user_id: str, logic: AppLogic, client: WebClient):
  try:
    if not logic.course.is_user_id_exists(user_id):
      res = client.users_identity(user=user_id)
      user_identity = res["user"]
      user = User(user_identity["id"] ,user_identity["name"], U_GUEST)
      if logic.course.add_user(user):
        logic.update_users()
        client.views_publish(
            user_id=user.platform_id,
            view=get_home_view(user, logic)
        )
  except Exception as e:
    logger.error(f"Error handle home tab: {e}")


def handle_add_course(client, ack, body, logger):
  ack()
  client.views_open(
      trigger_id=body["trigger_id"],
      view=get_setup_event_modal_base()
  )


def event_type_options(ack):
  ack({"options": get_event_type_model()})


def modal_event_setup_base_callback(ack, body, client, logger):
  ack()

  modal_values = body["view"]["state"]["values"]
  event_name = modal_values["event_name_input"]["event_name"]["value"]
  event_code = modal_values["event_type_select"]["event_type"]["selected_option"]["value"]
  event_code_value = event_types_from_code[event_code]
  event_datetime = modal_values["event_datetime_select"]["event_datetime"]["selected_date_time"]
  
  logger.info(f"got basic event data: {event_name}, {event_code} - {event_code_value}, {event_datetime} - {datetime.datetime.fromtimestamp(event_datetime)}")
  
  client.views_open(
      trigger_id=body["trigger_id"],
      view=get_setup_event_modal_details(event_code_value)
  )

def modal_event_setup_details_callback(ack, body, logger):
  ack()

  modal_values = body["view"]["state"]["values"]

  event_duration = int(modal_values["event_duration_select"]["event_duration"]["value"])
  
  logger.info(f"got event details: {event_duration}")
  # event_code = modal_values["event_type_select"]["event_type"]["selected_option"]["value"]
  # logger.info(f"got type     {event_code} - {event_types_from_code[event_code]}")
  # event_datetime = modal_values["event_datetime_select"]["event_datetime"]["selected_date_time"]
  # logger.info(f"got datetime {event_datetime} - {datetime.datetime.fromtimestamp(event_datetime)}")


def add_custom_data(app, logic):
  def middleware(context, next):
    context["logic"] = logic
    next()

  return middleware


def handle_message_event(body, logger):
  logger.info(body)


def register_app_events(app, logic):
  app.use(add_custom_data(app, logic))
  
  app.event("team_join")(member_join)
  app.event("app_home_opened")(app_home_opened)
  app.event("message")(handle_message_event)

  app.action("click_add_event")(handle_add_course)
  
  app.view("view_event_setup_base")(modal_event_setup_base_callback)
  app.view("view_event_setup_details")(modal_event_setup_details_callback)
  
  app.options("event_type")(event_type_options)