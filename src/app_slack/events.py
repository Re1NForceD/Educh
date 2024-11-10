from slack_sdk import WebClient

from .course_loop import start_course_loop
from .home_views import *
from .setup_event_views import *
from .setup_test_views import handle_add_test, handle_edit_test, handle_add_signle_variant, handle_remove_signle_variant, handle_add_multi_variant_correct, handle_add_multi_variant_incorrect, handle_remove_multi_variant, test_type_options, modal_test_setup_callback, modal_test_closed_callback, handle_take_test, modal_take_test_callback, handle_submit_assignment, modal_submit_assignment_callback

from app_logic_api import *


async def member_join(context, event, client: WebClient, logger):
  logger.info(f"member_join {event}")
  await track_user(event["user"]["id"], context["logic"], client)


async def app_home_opened(context, event, client: WebClient, logger):
  await track_user(event["user"], context["logic"], client)


async def track_user(user_id: str, logic: AppLogic, client: WebClient):
  try:
    if not logic.course.is_user_id_exists(user_id):
      res = await client.users_identity(user=user_id)
      user_identity = res["user"]
      user = User(user_identity["id"] ,user_identity["name"], U_GUEST)
      if logic.course.add_user(user):
        logic.update_users()
        await client.views_publish(
            user_id=user.platform_id,
            view=get_home_view(user, logic)
        )
  except Exception as e:
    logger.error(f"Error handle home tab: {e}")


async def handle_message_event(body, logger):
  logger.info(body)


def register_app_events(app, logic):
  @app.use
  async def middleware(context, next):
    context["logic"] = logic
    await next()
  
  @app.action("click_start_course")
  async def handle_start_course(context, body, logger, client: WebClient, ack: Ack):
    await ack()
    logic.start_course()
    start_course_loop(logic, client)

  app.action("click_take_test")(handle_take_test)
  app.view("view_take_test")(modal_take_test_callback)
  app.action("click_submit_assignment")(handle_submit_assignment)
  app.view("view_submit_assignment")(modal_submit_assignment_callback)

  app.event("team_join")(member_join)
  app.event("app_home_opened")(app_home_opened)
  app.event("message")(handle_message_event)

  app.action("click_add_event")(handle_add_course)
  app.view("view_event_setup")(modal_event_setup_callback)
  app.options("event_type")(event_type_options)
  app.action("click_edit_event")(handle_edit_event)
  app.view_closed("view_event_setup")(modal_event_closed_callback)
  app.action("click_remove_event")(handle_remove_event)

  app.action("click_add_test")(handle_add_test)
  app.view("view_test_setup")(modal_test_setup_callback)
  app.view_closed("view_test_setup")(modal_test_closed_callback)
  app.options("test_type")(test_type_options)
  app.action("click_remove_test")(handle_remove_test)
  app.action("click_edit_test")(handle_edit_test)
  app.action("click_add_single_variant")(handle_add_signle_variant)
  app.action("click_remove_single_variant")(handle_remove_signle_variant)
  app.action("click_add_multiple_variant_correct")(handle_add_multi_variant_correct)
  app.action("click_add_multiple_variant_incorrect")(handle_add_multi_variant_incorrect)
  app.action("click_remove_multi_variant")(handle_remove_multi_variant)
