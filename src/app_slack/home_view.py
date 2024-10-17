import datetime
from course_classes import *
from app_logic_api import *

def get_home_view(user_id: str, logic: AppLogic):
  is_teacher = logic.is_teacher_user(user_id)
  is_need_setup_events = logic.is_need_setup_events()
  return {
      "type": "home",
      "callback_id": "home_view",
      "blocks": get_events_setup_blocks(user_id, logic) if is_teacher and is_need_setup_events else get_default_blocks(user_id, logic)
  }

def get_default_blocks(user_id: str, logic: AppLogic):
  return [
      {
          "type": "section",
          "text": {
              "type": "plain_text",
              "text": f"*Welcome to your _App's Home tab_* :tada: {user_id}!"
          }
      },
      {
          "type": "divider"
      },
      {
          "type": "section",
          "text": {
              "type": "plain_text",
              "text": "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app."
          }
      }
  ]

def get_events_setup_blocks(user_id: str, logic: AppLogic):
  return [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "Need to setup course :books:"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "plain_text",
        "text": "Please add needed course events"
      }
    },
		{
			"type": "divider"
		},
    *get_event_setup_section(),
		{
			"type": "divider"
		},
    *get_events_list(),
		{
			"type": "divider"
		},
    *get_submit_events(),
  ]

def get_setup_event_modal():
  return {
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
    "blocks": [
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
      }
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

def get_event_setup_section():
  return [
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Add event",
					},
					"value": "click_add_event",
					"action_id": "click_add_event"
				}
			]
		},
  ]

def get_events_list():
  return [
    {
      "type": "section",
      "text": {
        "type": "plain_text",
        "text": "Please add needed course events"
      }
    },
  ]

def get_submit_events():
  return [
    {
      "type": "section",
      "text": {
        "type": "plain_text",
        "text": "Please add needed course events"
      }
    },
  ]
