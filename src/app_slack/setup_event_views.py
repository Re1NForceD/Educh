from course_classes import *
from app_logic_api import *

from slack_bolt import Ack
import json


def handle_add_course(client, ack: Ack, body, logger):
  ack()
  client.views_open(
      trigger_id=body["trigger_id"],
      view=get_setup_event_modal()
  )

def event_type_options(ack):
  ack({"options": get_event_type_model()})

def get_event_type_option(type: int):
  return {
    "text": {
      "type": "plain_text",
      "text": event_types_str[type],
      "emoji": True
    },
    "value": event_types_to_code[type]
  }

def get_event_type_model():
  model = []
  for type in event_types:
    model.append(get_event_type_option(type))
  return model

def get_event_type_field(event: Event):
  if event is None:
    return {
      "type": "input",
      "block_id": "event_type_select",
      "element": {
        "type": "external_select",
        "action_id": "event_type",
        "min_query_length": 0,
        "placeholder": {
          "type": "plain_text",
          "text": "Select an event type"
        },
      },
      "label": {
        "type": "plain_text",
        "text": "Event type"
      }
    }
  else:
    return {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"*Event type:* _{event_types_str[event.type]}_"
      }
    }

def get_setup_event_modal(event: Event=None):
  modal = {
    "type": "modal",
    "callback_id": "view_event_setup",
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
  }

  blocks = [
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
    get_event_type_field(event),
    {
      "type": "input",
      "block_id": "event_datetime_select",
      "element": {
        "type": "datetimepicker",
        "action_id": "event_datetime",
      },
      "label": {
        "type": "plain_text",
        "text": "Event date",
      }
    },
  ]
  
  if event is not None:
    blocks[0]["element"]["initial_value"] = event.name
    # blocks[1]["element"]["initial_option"] = get_event_type_option(event.type)
    if event.start_time is not None:
      blocks[2]["element"]["initial_date_time"] = int(datetime.datetime.timestamp(event.start_time))
    
    blocks += get_setup_event_modal_details_fields(event)

  if event is not None:
    modal["private_metadata"] = event_types_to_code[event.type]

  modal["blocks"] = blocks

  return modal

def get_setup_event_modal_details_fields(event: Event) -> list:
  if event is None:
    return []
  elif event.type == E_RESOURCES:
    return get_setup_event_modal_details_fields_resources()
  elif event.type == E_CLASS:
    return get_setup_event_modal_details_fields_class()
  elif event.type == E_TEST:
    return get_setup_event_modal_details_fields_test()
  
def get_setup_event_modal_details_fields_resources() -> list:
  return [
    {
      "type": "input",
      "block_id": "event_info_select",
      "element": {
        "type": "rich_text_input",
        "action_id": "event_info",
        "placeholder": {
          "type": "plain_text",
          "text": "Enter info you want share on this event"
        },
      },
      "label": {
        "type": "plain_text",
        "text": "Event information to share"
      }
    },
  ]
  
def get_setup_event_modal_details_fields_class() -> list:
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
    {
      "type": "input",
      "block_id": "event_info_select",
      "element": {
        "type": "rich_text_input",
        "action_id": "event_info",
        "placeholder": {
          "type": "plain_text",
          "text": "Enter info you want share on this event"
        },
      },
      "label": {
        "type": "plain_text",
        "text": "Event information to share"
      }
    },
  ]
  
def get_setup_event_modal_details_fields_test() -> list:
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
    {
      "type": "input",
      "block_id": "event_info_select",
      "element": {
        "type": "rich_text_input",
        "action_id": "event_info",
        "placeholder": {
          "type": "plain_text",
          "text": "Enter info you want share on this event"
        },
      },
      "label": {
        "type": "plain_text",
        "text": "Event information to share"
      }
    },
  ]


# view processing
def modal_event_setup_callback(context, ack: Ack, body, client, logger):
  modal_values = body["view"]["state"]["values"]
  is_first_setup_view = len(body["view"].get("private_metadata")) == 0
  
  event_name = modal_values["event_name_input"]["event_name"]["value"]
  event_type_code = modal_values["event_type_select"]["event_type"]["selected_option"]["value"] if is_first_setup_view else body["view"].get("private_metadata")
  event_type = event_types_from_code[event_type_code]
  event_datetime_stamp = modal_values["event_datetime_select"]["event_datetime"]["selected_date_time"]
  event_datetime = datetime.datetime.fromtimestamp(event_datetime_stamp)
  
  logger.info(f"got basic event data: {event_name}, {event_type_code} - {event_type}, {event_datetime_stamp} - {event_datetime}")

  event = get_event(0, event_type, event_name, event_datetime)

  # logger.info(f"sfjsdfshd {body} - [{body['view'].get('private_metadata')}]")
  if is_first_setup_view:
    ack(response_action="update", view=get_setup_event_modal(event))
    return
  else:
    ack(response_action="clear")
  # ack(response_action="errors", errors={"event_name_input":"You are loh"})
  
  # set event details and add event
  logic: AppLogic = context["logic"]
  set_event_details(event, modal_values)
  add_new_event(event, logic)

def add_new_event(event: Event, logic: AppLogic):
  logic.update_events([event])

def set_event_details(event: Event, modal_values: dict):
  if event.type == E_RESOURCES:
    set_event_details_resources(event, modal_values)
  elif event.type == E_CLASS:
    set_event_details_class(event, modal_values)
  elif event.type == E_TEST:
    set_event_details_test(event, modal_values)

def set_event_details_resources(event: ResourcesEvent, modal_values: dict):
  event_info = modal_values["event_info_select"]["event_info"]["rich_text_value"]
  event_info_str = json.dumps(event_info)

  logger.info(f"got resources details: {event_info_str}")

  event.info = event_info_str

def set_event_details_class(event: ClassEvent, modal_values: dict):
  event_duration = int(modal_values["event_duration_select"]["event_duration"]["value"])
  event_info = modal_values["event_info_select"]["event_info"]["rich_text_value"]
  event_info_str = json.dumps(event_info)

  logger.info(f"got class details: {event_duration}, {event_info_str}")

  event.info = event_info_str
  event.duration_m = event_duration

def set_event_details_test(event: TestEvent, modal_values: dict):
  event_duration = int(modal_values["event_duration_select"]["event_duration"]["value"])
  event_info = modal_values["event_info_select"]["event_info"]["rich_text_value"]
  event_info_str = json.dumps(event_info)

  logger.info(f"got test details: {event_duration}, {event_info_str}")
  
