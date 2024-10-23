from slack_sdk import WebClient

from .home_views import *
from .setup_event_views import *
from .setup_test_views import handle_add_test, handle_edit_test, handle_add_signle_variant, handle_remove_signle_variant, test_type_options, modal_test_setup_callback

from app_logic_api import *


def add_custom_data(app, logic):
  def middleware(context, next):
    context["logic"] = logic
    next()

  return middleware


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


def handle_message_event(body, logger):
  logger.info(body)


def register_app_events(app, logic):
  app.use(add_custom_data(app, logic))
  
  app.event("team_join")(member_join)
  app.event("app_home_opened")(app_home_opened)
  app.event("message")(handle_message_event)

  app.action("click_add_event")(handle_add_course)
  app.view("view_event_setup")(modal_event_setup_callback)
  app.options("event_type")(event_type_options)

  app.action("click_add_test")(handle_add_test)
  app.view("view_test_setup")(modal_test_setup_callback)
  app.options("test_type")(test_type_options)
  app.action("click_remove_test")(handle_remove_test)
  app.action("click_edit_test")(handle_edit_test)
  app.action("click_add_single_variant")(handle_add_signle_variant)
  app.action("click_remove_single_variant")(handle_remove_signle_variant)
