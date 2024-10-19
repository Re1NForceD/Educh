from course_classes import *
from app_logic_api import *


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

def get_setup_event_modal_details(event_type: int):
  return {
    "type": "modal",
    "callback_id": "view_event_setup_details",
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
          "min_value": "0",
          "max_value": "300"
        },
        "label": {
          "type": "plain_text",
          "text": "Event duration"
        }
      },
    ]
  }

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
