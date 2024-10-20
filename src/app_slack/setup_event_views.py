from course_classes import *
from app_logic_api import *

from slack_bolt import Ack


def handle_add_course(client, ack: Ack, body, logger):
  ack()
  client.views_open(
      trigger_id=body["trigger_id"],
      view=get_setup_event_modal_base()
  )

def event_type_options(ack):
  ack({"options": get_event_type_model()})

def get_event_type_model():
  model = []
  for type in event_types:
    model.append({
      "text": {
        "type": "plain_text",
        "text": event_types_str[type],
        "emoji": True
      },
      "value": event_types_to_code[type]
    })
  return model

def get_setup_event_modal_base():
  return {
    "type": "modal",
    "callback_id": "view_event_setup_base",
    "title": {
      "type": "plain_text",
      "text": "Setup event"
    },
    "submit": {
      "type": "plain_text",
      "text": "Submit"
    },
    "close": {
      "type": "plain_text",
      "text": "Cancel"
    },
    "blocks": [
      {
        "type": "input",
        "block_id": "event_name_input",
        "element": {
          "type": "plain_text_input",
          "action_id": "event_name",
          "min_length": 5,
          "max_length": 255,
          "placeholder": {
            "type": "plain_text",
            "text": "Enter an event name"
          },
        },
        "label": {
          "type": "plain_text",
          "text": "Event name",
        },
      },
      {
        "type": "input",
        "block_id": "event_type_select",
        "element": {
          "type": "external_select",
          "action_id": "event_type",
          "placeholder": {
            "type": "plain_text",
            "text": "Select an event type"
          },
          "min_query_length": 0
        },
        "label": {
          "type": "plain_text",
          "text": "Event type"
        }
      },
      {
        "type": "input",
        "block_id": "event_datetime_select",
        "element": {
          "type": "datetimepicker",
          "action_id": "event_datetime"
        },
        "label": {
          "type": "plain_text",
          "text": "Event date",
        }
      },
    ]
  }

def get_setup_event_modal_details(event: Event):
  return {
    "type": "modal",
    "callback_id": "view_event_setup_details",
    "private_metadata": event_types_to_code[event.type],
    "title": {
      "type": "plain_text",
      "text": "Setup event details"
    },
    "submit": {
      "type": "plain_text",
      "text": "Submit"
    },
    "close": {
      "type": "plain_text",
      "text": "Cancel"
    },
    "blocks": [
      *get_setup_event_modal_details_fields(event),
    ]
  }

def get_setup_event_modal_details_fields(event: Event) -> list:
  if event.type == E_RESOURCES:
    return get_setup_event_modal_details_fields_resources()
  elif event.type == E_CLASS:
    return get_setup_event_modal_details_fields_class()
  elif event.type == E_TEST:
    return get_setup_event_modal_details_fields_test()
  
def get_setup_event_modal_details_fields_resources() -> list:
  return [
    {
      "type": "input",
      "block_id": "event_duration_select",
      "element": {
        "type": "number_input",
        "is_decimal_allowed": False,
        "action_id": "event_duration",
        "placeholder": {
          "type": "plain_text",
          "text": "Enter event duration in minutes"
        },
        "min_value": "10",
        "max_value": "300"
      },
      "label": {
        "type": "plain_text",
        "text": "Event duration (minutes)"
      }
    },
  ]
  
def get_setup_event_modal_details_fields_class() -> list:
  return []
  
def get_setup_event_modal_details_fields_test() -> list:
  return []


# view processing
events_in_process: dict[str, Event] = {}

def modal_event_setup_base_callback(ack: Ack, body, client, logger):
  user_id = body["user"]["id"]
  modal_values = body["view"]["state"]["values"]
  
  event_name = modal_values["event_name_input"]["event_name"]["value"]
  event_type_code = modal_values["event_type_select"]["event_type"]["selected_option"]["value"]
  event_type = event_types_from_code[event_type_code]
  event_datetime_stamp = modal_values["event_datetime_select"]["event_datetime"]["selected_date_time"]
  event_datetime = datetime.datetime.fromtimestamp(event_datetime_stamp)
  
  logger.info(f"got basic event data: {event_name}, {event_type_code} - {event_type}, {event_datetime_stamp} - {event_datetime}")

  event = get_event(0, event_name, event_type, event_datetime)
  events_in_process[user_id] = event
  
  # ack()#response_action="errors", errors={"event_name_input":"You are loh"})
  ack(response_action="update", view=get_setup_event_modal_details(event))

def modal_event_setup_details_callback(context, ack: Ack, body, logger):
  user_id = body["user"]["id"]
  event = events_in_process[user_id]
  event_type = event_types_from_code[body["view"]["private_metadata"]]
  modal_values = body["view"]["state"]["values"]
  logic: AppLogic = context["logic"]

  if event.type is not event_type:
    ack(response_action="errors", errors={"error_block": "Something went wrong :("})
    return
  
  ack(response_action="clear")
  
  events_in_process.pop(user_id)
  set_event_details(event, modal_values)
  add_new_event(event, logic)

def add_new_event(event: Event, logic: AppLogic):
  pass

def set_event_details(event: Event, modal_values: dict):
  if event.type == E_RESOURCES:
    set_event_details_resources(event, modal_values)
  elif event.type == E_CLASS:
    set_event_details_class(event, modal_values)
  elif event.type == E_TEST:
    set_event_details_test(event, modal_values)

def set_event_details_resources(event: Event, modal_values: dict):
  event_duration = int(modal_values["event_duration_select"]["event_duration"]["value"])
  logger.info(f"got resources details: {event_duration}")

def set_event_details_class(event: Event, modal_values: dict):
  pass

def set_event_details_test(event: Event, modal_values: dict):
  pass
