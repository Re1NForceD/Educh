from course_classes import *
from app_logic_api import *

from .home_views import update_home_views, get_manage_events_modal
from .course_loop import clear_next_event

from slack_bolt import Ack
from slack_sdk import WebClient
import json
import copy


events_in_process: dict[str, list[str, Event, Event]] = {} # [user_id, [view_id, Event]]

def get_event_in_process(user_id: str):
  return events_in_process.get(user_id)

def pop_event_in_process(user_id: str):
  data = events_in_process.get(user_id)
  events_in_process.pop(user_id)
  return data

def add_event_in_process(user_id: str, view_id: str, event: Event, orig: Event=None):
  events_in_process[user_id] = [view_id, event, orig]

async def handle_add_event(client: WebClient, ack: Ack, body, logger):
  await ack()
  resp = await client.views_push(
      trigger_id=body["trigger_id"],
      view=get_setup_event_modal()
  )
  add_event_in_process(body["user"]["id"], resp["view"]["id"], None)

async def handle_edit_event(context, client: WebClient, ack: Ack, body, logger):
  await ack()
  user_id = body["user"]["id"]
  event_id = int(body["actions"][0]["value"])
  logic: AppLogic = context["logic"]

  event_copy: Event = copy.deepcopy(logic.course.get_event(event_id))
  resp = await client.views_push(
      trigger_id=body["trigger_id"],
      view=get_setup_event_modal(event_copy)
  )
  add_event_in_process(user_id, resp["view"]["id"], event_copy)

async def handle_remove_event(context, client, ack: Ack, body, logger):
  await ack()
  user_id = body["user"]["id"]
  event_id = int(body["actions"][0]["value"])
  logic: AppLogic = context["logic"]

  event_orig: Event = logic.course.remove_event(event_id)
 
  logic.remove_events([event_orig])
  clear_next_event()

  await update_home_views(logic, client)
  await client.views_update(
      view_id=body["view"]["id"],
      view=get_manage_events_modal(logic)
  )

async def event_type_options(ack):
  await ack({"options": get_event_type_model()})

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
  
  if event is not None:
    blocks[0]["element"]["initial_value"] = event.name
    # blocks[1]["element"]["initial_option"] = get_event_type_option(event.type)
    # if event.start_time is not None:
    blocks[2]["element"]["initial_date_time"] = int(datetime.datetime.timestamp(event.start_time))
    blocks[3]["element"]["initial_value"] = json.loads(event.info)

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
    return get_setup_event_modal_details_fields_class(event)
  elif event.type == E_TEST:
    return get_setup_event_modal_details_fields_test(event)
  elif event.type == E_ASSIGNMENT:
    return get_setup_event_modal_details_fields_assignment()
  
def get_setup_event_modal_details_fields_resources() -> list:
  return [
  ]
  
def get_setup_event_modal_details_fields_class(event: ClassEvent) -> list:
  blocks = [
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
      "block_id": "event_url_select",
      "element": {
        "type": "url_text_input",
        "action_id": "event_url",
        "placeholder": {
          "type": "plain_text",
          "text": "Enter url to class"
        },
      },
      "label": {
        "type": "plain_text",
        "text": "Class URL",
      }
    },
  ]

  if event.duration_m is not None:
    blocks[0]["element"]["initial_value"] = f"{event.duration_m}"

  if event.url is not None:
    blocks[1]["element"]["initial_value"] = f"{event.url}"

  return blocks
  
def get_setup_event_modal_details_fields_test(event: TestEvent) -> list:
  blocks = [
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
        "max_value": "300",
      },
      "label": {
        "type": "plain_text",
        "text": "Event duration (minutes)"
      }
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "Add test",
          },
          "style": "primary",
          "action_id": "click_add_test"
        }
      ]
    },
    {
      "type": "divider",
    }
  ]

  if event.duration_m is not None:
    blocks[0]["element"]["initial_value"] = f"{event.duration_m}"

  if len(event.configs) == 0:
    blocks.append({
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"*_No tests yet_*"
      }
    })
    return blocks
  
  for test in event.configs.values():
    blocks += get_test_fields(test)

  return blocks
  
def get_setup_event_modal_details_fields_assignment() -> list:
  return [
  ]

async def handle_remove_test(client: WebClient, ack: Ack, body, logger):
    await ack()
    user_id = body["user"]["id"]
    test_hash = body["actions"][0]["value"]
    event_data = get_event_in_process(user_id)
    event: TestEvent = event_data[1]
    event.remove_config(test_hash)
    await client.views_update(
        view_id=event_data[0],
        view=get_setup_event_modal(event)
    )

def get_test_info(test: TestConfig):
  if test.type == T_SINGLE:
    return f"*Test type:* _{test_types_str[test.type]}_\n*Question:* {test.question}\n*Variants amount:* {len(test.variants)}"
  elif test.type == T_MULTI:
    return f"*Test type:* _{test_types_str[test.type]}_\n*Question:* {test.question}\n*Correct amount:* {len(test.correct)}; *Incorrect amount:* {len(test.incorrect)}"
  # elif test.type == T_COMPLIANCE:
    # return f"*Test type:* _{test_types_str[test.type]}_"
  return f"*Test type:* _{test_types_str[test.type]}_"

def get_test_fields(test: TestConfig):
  return [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": get_test_info(test)
      }
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "Edit",
          },
          "value": test.calc_hash(),
          "action_id": "click_edit_test"
        },
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "Remove",
          },
          "style": "danger",
          "value": test.calc_hash(),
          "action_id": "click_remove_test"
        },
      ]
    },
    {
      "type": "divider",
    },
  ]


# view processing
async def update_modal_event_setup_test_config(user_id: str, test: TestConfig, client: WebClient):
  if test is None:
    return
  
  event_data = get_event_in_process(user_id)
  event = event_data[1]
  if event is None:
    raise Exception(f"no event for user {user_id}")
  
  if event.type != E_TEST:
    raise Exception(f"event for user {user_id} is of type: {event_types_to_code(event.type)}")
  
  test_event: TestEvent = event
  test_event.add_config(test)

  await client.views_update(
      view_id=event_data[0],
      view=get_setup_event_modal(event)
  )

async def modal_event_setup_callback(context, ack: Ack, body, client, logger):
  user_id = body["user"]["id"]
  modal_values = body["view"]["state"]["values"]
  is_first_setup_view = len(body["view"].get("private_metadata")) == 0
  
  event_name = modal_values["event_name_input"]["event_name"]["value"]
  event_type_code = modal_values["event_type_select"]["event_type"]["selected_option"]["value"] if is_first_setup_view else body["view"].get("private_metadata")
  event_type = event_types_from_code[event_type_code]
  event_datetime_stamp = modal_values["event_datetime_select"]["event_datetime"]["selected_date_time"]
  event_datetime = datetime.datetime.fromtimestamp(event_datetime_stamp)
  event_info = modal_values["event_info_select"]["event_info"]["rich_text_value"]
  event_info_str = json.dumps(event_info)
  
  logger.info(f"got basic event data: {event_name}, {event_type_code} - {event_type}, {event_datetime_stamp} - {event_datetime}")

  event: Event = None

  if is_first_setup_view:
    event = get_event(0, event_type, event_name, event_datetime, event_info_str)
    if event.type == E_RESOURCES or event.type == E_ASSIGNMENT:
      await ack()
    else:
      await ack(response_action="update", view=get_setup_event_modal(event))
      add_event_in_process(user_id, body["view"]["id"], event)
      return
  else:
    # TODO: validate event here
    # ack(response_action="errors", errors={"event_name_input":"You are loh"})
    await ack()
    event_data = pop_event_in_process(user_id)
    event = event_data[1]

    # update event info from modal
    event.name = event_name
    event.start_time = event_datetime
    event.info = event_info_str
  
  # set event details and add event
  logic: AppLogic = context["logic"]
  set_event_details(event, modal_values)
  
  await add_new_event(event, logic, client)
  await client.views_update(
      view_id=body["view"]["previous_view_id"],
      view=get_manage_events_modal(logic)
  )

async def add_new_event(event: Event, logic: AppLogic, client: WebClient):
  logic.update_events([event])
  clear_next_event()
  if event.is_not_added():
    await new_events_added(logic, [event], client)

async def new_events_added(logic: AppLogic, new_events: list[Event], client: WebClient):
  # await notify_new_events(logic, new_events, client) # TODO
  await update_home_views(logic, client)

def set_event_details(event: Event, modal_values: dict):
  if event.type == E_RESOURCES:
    set_event_details_resources(event, modal_values)
  elif event.type == E_CLASS:
    set_event_details_class(event, modal_values)
  elif event.type == E_TEST:
    set_event_details_test(event, modal_values)
  elif event.type == E_ASSIGNMENT:
    set_event_details_assignment(event, modal_values)

def set_event_details_resources(event: ResourcesEvent, modal_values: dict):
  logger.info(f"got resources details: ")

def set_event_details_class(event: ClassEvent, modal_values: dict):
  event_duration = int(modal_values["event_duration_select"]["event_duration"]["value"])
  event_url = modal_values["event_url_select"]["event_url"]["value"]

  logger.info(f"got class details: {event_duration}, {event_url}")

  event.duration_m = event_duration
  event.url = event_url

def set_event_details_test(event: TestEvent, modal_values: dict):
  event_duration = int(modal_values["event_duration_select"]["event_duration"]["value"])

  logger.info(f"got test details: {event_duration}")
  
  event.duration_m = event_duration

def set_event_details_assignment(event: ResourcesEvent, modal_values: dict):
  logger.info(f"got assignment details: ")
