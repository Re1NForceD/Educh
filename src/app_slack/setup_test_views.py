from course_classes import *
from app_logic_api import *
from .setup_event_views import update_modal_event_setup_test_config, get_event_in_process

from slack_bolt import Ack
from slack_sdk import WebClient
import json


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
    # get_test_type_field(test),
    # {
    #   "type": "input",
    #   "block_id": "test_question_select",
    #   "element": {
    #     "type": "rich_text_input",
    #     "action_id": "test_question",
    #     "placeholder": {
    #       "type": "plain_text",
    #       "text": "Question"
    #     },
    #   },
    #   "label": {
    #     "type": "plain_text",
    #     "text": "Enter question for your test"
    #   }
    # },
  ]
  
  # if test is not None:
  #   blocks[0]["element"]["initial_value"] = test.name
  #   # blocks[1]["element"]["initial_option"] = get_test_type_option(test.type)
  #   if test.start_time is not None:
  #     blocks[2]["element"]["initial_date_time"] = int(datetime.datetime.timestamp(test.start_time))
    
  #   blocks += get_setup_test_modal_details_fields(test)

  # if test is not None:
  #   modal["private_metadata"] = test_types_to_code[test.type]

  modal["blocks"] = blocks

  return modal

# def get_setup_event_modal_details_fields(event: Event) -> list:
#   if event is None:
#     return []
#   elif event.type == E_RESOURCES:
#     return get_setup_event_modal_details_fields_resources()
#   elif event.type == E_CLASS:
#     return get_setup_event_modal_details_fields_class()
#   elif event.type == E_TEST:
#     return get_setup_event_modal_details_fields_test(event)
  
# def get_setup_event_modal_details_fields_resources() -> list:
#   return [
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
#   ]
  
# def get_setup_event_modal_details_fields_class() -> list:
#   return [
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
#   ]
  
# def get_setup_event_modal_details_fields_test(event: Event) -> list:
#   return [
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
#   ]


# view processing
def modal_test_setup_callback(context, ack: Ack, body, client, logger):
  ack()
  modal_values = body["view"]["state"]["values"]
  logger.info(f"got values {body['view']}")

  test: TestConfig = TestConfigSignle("sdfsaf", ["1", "2", "3"])

  update_modal_event_setup_test_config(body["user"]["id"], test, client)
  
#   is_first_setup_view = len(body["view"].get("private_metadata")) == 0
  
#   event_name = modal_values["event_name_input"]["event_name"]["value"]
#   event_type_code = modal_values["event_type_select"]["event_type"]["selected_option"]["value"] if is_first_setup_view else body["view"].get("private_metadata")
#   event_type = event_types_from_code[event_type_code]
#   event_datetime_stamp = modal_values["event_datetime_select"]["event_datetime"]["selected_date_time"]
#   event_datetime = datetime.datetime.fromtimestamp(event_datetime_stamp)
  
#   logger.info(f"got basic event data: {event_name}, {event_type_code} - {event_type}, {event_datetime_stamp} - {event_datetime}")

#   event = get_event(0, event_type, event_name, event_datetime)

#   # logger.info(f"sfjsdfshd {body} - [{body['view'].get('private_metadata')}]")
#   if is_first_setup_view:
#     ack(response_action="update", view=get_setup_event_modal(event))
#     return
#   else:
#     ack(response_action="clear")
#   # ack(response_action="errors", errors={"event_name_input":"You are loh"})
  
#   # set event details and add event
#   logic: AppLogic = context["logic"]
#   set_event_details(event, modal_values)
#   add_new_event(event, logic)

# def add_new_event(event: Event, logic: AppLogic):
#   logic.update_events([event])

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
