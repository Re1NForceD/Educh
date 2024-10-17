from .home_view import *


def update_home_tab(context, client, event, logger):
  try:
    logic = context['logic']
    user_id = event["user"]
    client.views_publish(
        user_id=user_id,
        view=get_home_view(user_id, logic)
    )
  except Exception as e:
    logger.error(f"Error publishing home tab: {e}")


def handle_add_course(client, ack, body, logger):
    ack()
    client.views_open(
        trigger_id=body["trigger_id"],
        view=get_setup_event_modal()
    )


def event_type_options(ack):
    ack({"options": get_event_type_model()})


def modal_event_setup_callback(ack, body, logger):
    ack()

    modal_values = body["view"]["state"]["values"]
    logger.info(modal_values)
    event_code = modal_values["event_type_select"]["event_type"]["selected_option"]["value"]
    logger.info(f"got type     {event_code} - {event_types_from_code[event_code]}")
    event_datetime = modal_values["event_datetime_select"]["event_datetime"]["selected_date_time"]
    logger.info(f"got datetime {event_datetime} - {datetime.datetime.fromtimestamp(event_datetime)}")
    event_duration = int(modal_values["event_duration_select"]["event_duration"]["value"])
    logger.info(f"got duration {event_duration}")
    # new_event = get_event(0, event_types_from_code[event_code], )


def add_custom_data(app, logic):
  def middleware(context, next):
    context["logic"] = logic
    next()

  return middleware


def register_app_events(app, logic):
  app.use(add_custom_data(app, logic))
  app.event("app_home_opened")(update_home_tab)
  app.action("click_add_event")(handle_add_course)
  app.view("view_event_setup")(modal_event_setup_callback)
  app.options("event_type")(event_type_options)