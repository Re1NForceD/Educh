from course_classes import *
from app_logic_api import *
from .setup_event_views import update_modal_event_setup_test_config, get_event_in_process

from slack_bolt import Ack
from slack_sdk import WebClient
import json


tests_in_process: dict[str, list[str, TestConfig]] = {} # [user_id, [view_id, TestConfig]]

def get_test_in_process(user_id: str):
  return tests_in_process.get(user_id)

def pop_test_in_process(user_id: str):
  data = tests_in_process.get(user_id)
  tests_in_process.pop(user_id)
  return data

def add_test_in_process(user_id: str, view_id: str, test: TestConfig):
  tests_in_process[user_id] = [view_id, test]

def handle_add_test(client: WebClient, ack: Ack, body, logger):
  ack()#response_action="push", view=get_setup_test_modal())
  client.views_push(
      trigger_id=body["trigger_id"],
      view=get_setup_test_modal()
  )

def handle_edit_test(client: WebClient, ack: Ack, body, logger):
    ack()
    user_id = body["user"]["id"]
    test_hash = body["actions"][0]["value"]
    event_data = get_event_in_process(user_id)
    event = event_data[1]
    logger.info(f"handle_edit_test {user_id} {event_types_to_code[event.type]} {test_hash}")

def handle_remove_test(client: WebClient, ack: Ack, body, logger):
    ack()
    user_id = body["user"]["id"]
    test_hash = body["actions"][0]["value"]
    event_data = get_event_in_process(user_id)
    event = event_data[1]
    logger.info(f"handle_remove_test {user_id} {event_types_to_code[event.type]} {test_hash}")

def test_type_options(ack):
  ack({"options": get_test_type_model()})

def get_test_type_option(type: int):
  return {
    "text": {
      "type": "plain_text",
      "text": test_types_str[type],
      "emoji": True
    },
    "value": test_types_to_code[type]
  }

def get_test_type_model():
  model = []
  for type in test_types:
    model.append(get_test_type_option(type))
  return model

def get_test_type_field(test: TestConfig):
  if test is None:
    return {
      "type": "input",
      "block_id": "test_type_select",
      "element": {
        "type": "external_select",
        "action_id": "test_type",
        "min_query_length": 0,
        "placeholder": {
          "type": "plain_text",
          "text": "Select an test type"
        },
      },
      "label": {
        "type": "plain_text",
        "text": "Test type"
      }
    }
  else:
    return {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"*Test type:* _{test_types_str[test.type]}_"
      }
    }

def get_setup_test_modal(test: TestConfig=None):
  modal = {
    "type": "modal",
    "callback_id": "view_test_setup",
    "title": {
      "type": "plain_text",
      "text": "Setup test"
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
    get_test_type_field(test),
  ]
  
  if test is not None:
    blocks += [{
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": get_test_description(test)
        }
      },
      {
        "type": "input",
        "block_id": "test_question_select",
        "element": {
          "type": "plain_text_input",
          "action_id": "test_question",
          "placeholder": {
            "type": "plain_text",
            "text": "Test question"
          },
          "min_length": 1,
        },
        "label": {
          "type": "plain_text",
          "text": "Enter test question"
        }
      },
      {
        "type": "divider"
      }
    ]
    
    blocks += get_setup_test_modal_details_fields(test)

  if test is not None:
    modal["private_metadata"] = test_types_to_code[test.type]

  modal["blocks"] = blocks

  return modal

def get_test_description(test: TestConfig):
  if test.type == T_SINGLE:
    return f"Add at least 3 variants, first must be correct. Variants will be shufled for learners."
  elif test.type == T_MULTI:
    return f"Add at least 5 variants, 2 - correct, 3 - incorrect. Variants will be shufled for learners."
  # elif test.type == T_COMPLIANCE:
    # return f""
  return ""

def get_setup_test_modal_details_fields(test: TestConfig) -> list:
  if test is None:
    return []
  elif test.type == T_SINGLE:
    return get_setup_test_modal_details_fields_single(test)
  elif test.type == T_MULTI:
    return get_setup_test_modal_details_fields_multi(test)
  # elif test.type == T_COMPLIANCE:
    # return get_setup_test_modal_details_fields_compliance(test)
  
def get_setup_test_modal_details_fields_single(test: TestConfigSignle) -> list:
  blocks = [
    {
      "type": "input",
      "block_id": "test_variant_select",
      "optional": True,
      "label": {
        "type": "plain_text",
        "text": "Enter test variant"
      },
      "element": {
        "type": "plain_text_input",
        "action_id": "test_variant",
        "placeholder": {
          "type": "plain_text",
          "text": "Test variant"
        },
        "min_length": 1,
      }
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "Add",
          },
          "action_id": "click_add_single_variant"
        },
      ]
    },
    {
      "type": "divider"
    },
  ]

  if len(test.anses) == 0:
    blocks.append({
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"*_No variants yet_*"
      }
    })
    return blocks
  
  for i in range(len(test.anses)):
    blocks.append({
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"- {test.anses[i]} {'(correct)' if i == 0 else ''}"
      },
      "accessory": {
        "type": "button",
        "style": "danger",
        "text": {
          "type": "plain_text",
          "text": "Remove",
        },
        "value": f"{i}",
        "action_id": "click_remove_single_variant"
      }
    })

  return blocks
  
def get_setup_test_modal_details_fields_multi(test: TestConfig) -> list:
  return [
#     {
#       "type": "input",
#       "block_id": "event_duration_select",
#       "element": {
#         "type": "number_input",
#         "is_decimal_allowed": False,
#         "action_id": "event_duration",
#         "placeholder": {
#           "type": "plain_text",
#           "text": "Enter event duration in minutes"
#         },
#         "min_value": "10",
#         "max_value": "300"
#       },
#       "label": {
#         "type": "plain_text",
#         "text": "Event duration (minutes)"
#       }
#     },
#     {
#       "type": "input",
#       "block_id": "event_info_select",
#       "element": {
#         "type": "rich_text_input",
#         "action_id": "event_info",
#         "placeholder": {
#           "type": "plain_text",
#           "text": "Enter info you want share on this event"
#         },
#       },
#       "label": {
#         "type": "plain_text",
#         "text": "Event information to share"
#       }
#     },
  ]
  
def get_setup_test_modal_details_fields_test(test: TestConfig) -> list:
  return [
#     {
#       "type": "input",
#       "block_id": "event_duration_select",
#       "element": {
#         "type": "number_input",
#         "is_decimal_allowed": False,
#         "action_id": "event_duration",
#         "placeholder": {
#           "type": "plain_text",
#           "text": "Enter event duration in minutes"
#         },
#         "min_value": "10",
#         "max_value": "300"
#       },
#       "label": {
#         "type": "plain_text",
#         "text": "Event duration (minutes)"
#       }
#     },
#     {
#       "type": "input",
#       "block_id": "event_info_select",
#       "element": {
#         "type": "rich_text_input",
#         "action_id": "event_info",
#         "placeholder": {
#           "type": "plain_text",
#           "text": "Enter info you want share on this event"
#         },
#       },
#       "label": {
#         "type": "plain_text",
#         "text": "Event information to share"
#       }
#     },
#     {
#       "type": "actions",
#       "elements": [
#         {
#           "type": "button",
#           "text": {
#             "type": "plain_text",
#             "text": "Add test",
#           },
#           "value": "click_add_test",
#           "action_id": "click_add_test"
#         }
#       ]
#     },
  ]


# view processing
def handle_add_signle_variant(ack: Ack, body, client, logger):
  ack()
  user_id = body["user"]["id"]
  modal_values = body["view"]["state"]["values"]

  test_data = get_test_in_process(user_id)
  test: TestConfigSignle = test_data[1]
  test.anses.append(modal_values["test_variant_select"]["test_variant"]["value"])
  
  client.views_update(
      view_id=test_data[0],
      view=get_setup_test_modal(test)
  )

def handle_remove_signle_variant(ack: Ack, body, client, logger):
  ack()
  user_id = body["user"]["id"]

  test_data = get_test_in_process(user_id)
  test: TestConfigSignle = test_data[1]
  test.anses.pop(int(body["actions"][0]["value"]))
  
  client.views_update(
      view_id=test_data[0],
      view=get_setup_test_modal(test)
  )

def modal_test_setup_callback(context, ack: Ack, body, client, logger):
  user_id = body["user"]["id"]
  modal_values = body["view"]["state"]["values"]
  is_first_setup_view = len(body["view"].get("private_metadata")) == 0
  
  test_type_code = modal_values["test_type_select"]["test_type"]["selected_option"]["value"] if is_first_setup_view else body["view"].get("private_metadata")
  test_type = test_types_from_code[test_type_code]

  test: TestConfig = None

  if is_first_setup_view:
    test = init_test_config(test_type)
    ack(response_action="update", view=get_setup_test_modal(test))
    add_test_in_process(user_id, body["view"]["id"], test)
    return
  else:
    test_data = get_test_in_process(user_id)
    test = test_data[1]

    # update test info from modal
    # event.name = event_name

    valid_error = test.validate()
    if valid_error:
      ack(response_action="errors", errors={"test_question_select": valid_error})
      return
    
    ack()
    pop_test_in_process(user_id)
    return
  
#   # set event details and add event
#   logic: AppLogic = context["logic"]
#   set_event_details(event, modal_values)

  update_modal_event_setup_test_config(body["user"]["id"], test, client)

# def set_event_details(event: Event, modal_values: dict):
#   if event.type == E_RESOURCES:
#     set_event_details_resources(event, modal_values)
#   elif event.type == E_CLASS:
#     set_event_details_class(event, modal_values)
#   elif event.type == E_TEST:
#     set_event_details_test(event, modal_values)

# def set_event_details_resources(event: ResourcesEvent, modal_values: dict):
#   event_info = modal_values["event_info_select"]["event_info"]["rich_text_value"]
#   event_info_str = json.dumps(event_info)

#   logger.info(f"got resources details: {event_info_str}")

#   event.info = event_info_str

# def set_event_details_class(event: ClassEvent, modal_values: dict):
#   event_duration = int(modal_values["event_duration_select"]["event_duration"]["value"])
#   event_info = modal_values["event_info_select"]["event_info"]["rich_text_value"]
#   event_info_str = json.dumps(event_info)

#   logger.info(f"got class details: {event_duration}, {event_info_str}")

#   event.info = event_info_str
#   event.duration_m = event_duration

# def set_event_details_test(event: TestEvent, modal_values: dict):
#   event_duration = int(modal_values["event_duration_select"]["event_duration"]["value"])
#   event_info = modal_values["event_info_select"]["event_info"]["rich_text_value"]
#   event_info_str = json.dumps(event_info)

#   logger.info(f"got test details: {event_duration}, {event_info_str}")
