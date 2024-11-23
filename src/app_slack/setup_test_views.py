from course_classes import *
from app_logic_api import *
from .home_views import update_home_teachers_user, get_submition_message_blocks
from .setup_event_views import update_modal_event_setup_test_config, get_event_in_process

from slack_bolt import Ack
from slack_sdk import WebClient
import json
import copy
import random


tests_in_process: dict[str, list[str, TestConfig, TestConfig]] = {} # [user_id, [view_id, TestConfig, orig TestConfig]]

def get_test_in_process(user_id: str):
  return tests_in_process.get(user_id)

def pop_test_in_process(user_id: str):
  return tests_in_process.pop(user_id, None)

def add_test_in_process(user_id: str, view_id: str, test: TestConfig, orig: TestConfig = None):
  tests_in_process[user_id] = [view_id, test, orig]

async def handle_add_test(client: WebClient, ack: Ack, body, logger):
  await ack()
  await client.views_push(
      trigger_id=body["trigger_id"],
      view=get_setup_test_modal()
  )

async def handle_edit_test(client: WebClient, ack: Ack, body, logger):
  await ack()
  user_id = body["user"]["id"]
  test_hash = body["actions"][0]["value"]
  event_data = get_event_in_process(user_id)
  event: TestEvent = event_data[1]
  test_orig: TestConfig = event.remove_config(test_hash)
  test_copy: TestConfig = copy.deepcopy(test_orig)
  resp = await client.views_push(
      trigger_id=body["trigger_id"],
      view=get_setup_test_modal(test_copy)
  )
  add_test_in_process(user_id, resp["view"]["id"], test_copy, test_orig)

async def modal_test_closed_callback(client: WebClient, ack: Ack, body, logger):
  await ack()
  user_id = body["user"]["id"]
  test_data = pop_test_in_process(user_id)
  if test_data is not None and test_data[2] is not None:
    await update_modal_event_setup_test_config(user_id, test_data[2], client)

async def test_type_options(ack):
  await ack({"options": get_test_type_model()})

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

def get_setup_test_modal(test: TestConfig=None, need_clean_up: bool = False):
  modal = {
    "type": "modal",
    "callback_id": "view_test_setup",
    "notify_on_close": True,
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

    blocks[-2]["element"]["initial_value"] = test.question
    
    blocks += get_setup_test_modal_details_fields(test, need_clean_up)

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

def get_setup_test_modal_details_fields(test: TestConfig, need_clean_up: bool = False) -> list:
  if test is None:
    return []
  elif test.type == T_SINGLE:
    return get_setup_test_modal_details_fields_single(test, need_clean_up)
  elif test.type == T_MULTI:
    return get_setup_test_modal_details_fields_multi(test, need_clean_up)
  # elif test.type == T_COMPLIANCE:
    # return get_setup_test_modal_details_fields_compliance(test)
  
def get_setup_test_modal_details_fields_single(test: TestConfigSignle, need_clean_up: bool = False) -> list:
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

  if need_clean_up:
    blocks[0]["element"]["initial_value"] = ""

  if len(test.variants) == 0:
    blocks.append({
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"*_No variants yet_*"
      }
    })
    return blocks
  
  for var_hash in test.variants:
    blocks.append({
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"- {test.variants[var_hash]} {'(correct)' if test.ans_hash == var_hash else ''}"
      },
      "accessory": {
        "type": "button",
        "style": "danger",
        "text": {
          "type": "plain_text",
          "text": "Remove",
        },
        "value": var_hash,
        "action_id": "click_remove_single_variant"
      }
    })

  return blocks
  
def get_setup_test_modal_details_fields_multi(test: TestConfigMulti, need_clean_up: bool = False) -> list:
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
            "text": "Add correct",
          },
          "action_id": "click_add_multiple_variant_correct"
        },
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "Add incorrect",
          },
          "action_id": "click_add_multiple_variant_incorrect"
        },
      ]
    },
    {
      "type": "divider"
    },
  ]

  if need_clean_up:
    blocks[0]["element"]["initial_value"] = ""

  if len(test.correct) == 0 and len(test.incorrect) == 0:
    blocks.append({
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"*_No variants yet_*"
      }
    })
    return blocks
  
  for var_hash in test.correct:
    blocks.append({
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"- {test.correct[var_hash]} (correct)"
      },
      "accessory": {
        "type": "button",
        "style": "danger",
        "text": {
          "type": "plain_text",
          "text": "Remove",
        },
        "value": var_hash,
        "action_id": "click_remove_multi_variant"
      }
    })
  
  for var_hash in test.incorrect:
    blocks.append({
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"- {test.incorrect[var_hash]}"
      },
      "accessory": {
        "type": "button",
        "style": "danger",
        "text": {
          "type": "plain_text",
          "text": "Remove",
        },
        "value": var_hash,
        "action_id": "click_remove_multi_variant"
      }
    })

  return blocks


# view processing
async def handle_add_signle_variant(ack: Ack, body, client, logger):
  await ack()
  user_id = body["user"]["id"]
  modal_values = body["view"]["state"]["values"]

  test_data = get_test_in_process(user_id)
  test: TestConfigSignle = test_data[1]
  test.add_variant(modal_values["test_variant_select"]["test_variant"]["value"])
  
  await client.views_update(
      view_id=test_data[0],
      view=get_setup_test_modal(test, True)
  )

async def handle_remove_signle_variant(ack: Ack, body, client, logger):
  await ack()
  user_id = body["user"]["id"]

  test_data = get_test_in_process(user_id)
  test: TestConfigSignle = test_data[1]
  test.remove_variant(body["actions"][0]["value"])
  
  await client.views_update(
      view_id=test_data[0],
      view=get_setup_test_modal(test)
  )

async def handle_add_multi_variant_correct(ack: Ack, body, client, logger):
  await ack()
  user_id = body["user"]["id"]
  modal_values = body["view"]["state"]["values"]

  test_data = get_test_in_process(user_id)
  test: TestConfigMulti = test_data[1]
  test.add_correct(modal_values["test_variant_select"]["test_variant"]["value"])
  
  await client.views_update(
      view_id=test_data[0],
      view=get_setup_test_modal(test, True)
  )

async def handle_add_multi_variant_incorrect(ack: Ack, body, client, logger):
  await ack()
  user_id = body["user"]["id"]
  modal_values = body["view"]["state"]["values"]

  test_data = get_test_in_process(user_id)
  test: TestConfigMulti = test_data[1]
  test.add_incorrect(modal_values["test_variant_select"]["test_variant"]["value"])
  
  await client.views_update(
      view_id=test_data[0],
      view=get_setup_test_modal(test, True)
  )

async def handle_remove_multi_variant(ack: Ack, body, client, logger):
  await ack()
  user_id = body["user"]["id"]

  test_data = get_test_in_process(user_id)
  test: TestConfigMulti = test_data[1]
  test.remove_variant(body["actions"][0]["value"])
  
  await client.views_update(
      view_id=test_data[0],
      view=get_setup_test_modal(test)
  )

async def modal_test_setup_callback(context, ack: Ack, body, client, logger):
  user_id = body["user"]["id"]
  modal_values = body["view"]["state"]["values"]
  is_first_setup_view = len(body["view"].get("private_metadata")) == 0
  
  test_type_code = modal_values["test_type_select"]["test_type"]["selected_option"]["value"] if is_first_setup_view else body["view"].get("private_metadata")
  test_type = test_types_from_code[test_type_code]

  test: TestConfig = None

  if is_first_setup_view:
    test = init_test_config(test_type)
    await ack(response_action="update", view=get_setup_test_modal(test))
    add_test_in_process(user_id, body["view"]["id"], test)
    return
  else:
    test_data = get_test_in_process(user_id)
    test = test_data[1]

    # update test info from modal
    test.question = modal_values["test_question_select"]["test_question"]["value"]

    valid_error = test.validate()
    if valid_error:
      await ack(response_action="errors", errors={"test_question_select": valid_error})
      return
    
    await ack()
    pop_test_in_process(user_id)
  
  await update_modal_event_setup_test_config(body["user"]["id"], test, client)


async def handle_take_test(context, body, logger, client: WebClient, ack: Ack):
  logic: AppLogic = context["logic"]

  user_id: str = body["user"]["id"]
  if not logic.course.get_user(user_id).is_learner():
    await ack(response_action="errors", errors={"event_block": "You are not a learner"})
    logger.warning(f"{user_id} is not a learner to take test")
    return
  
  await ack()
  
  logger.info(body)
  event_id = int(body["actions"][0]["value"])
  event: Event = logic.course.get_event(event_id)

  if event.type != E_TEST:
    logger.error(f"try to take test from event {event_id} but it is not a test event")

  resp = await client.views_open(
      trigger_id=body["trigger_id"],
      view=get_test_modal(event)
  )

def get_test_modal(event: TestEvent):
  modal = {
    "type": "modal",
    "callback_id": "view_take_test",
    "title": {
      "type": "plain_text",
      "text": event.name
    },
    "submit": {
      "type": "plain_text",
      "text": "Submit"
    },
    "close": {
      "type": "plain_text",
      "text": "Cancel"
    },
    "private_metadata": f"{event.id}",
  }

  blocks = []
  for hash in random.sample(list(event.configs.keys()), len(event.configs)):
    blocks += get_test_config_blocks(hash, event.configs[hash])
    blocks.append({"type": "divider"})

  modal["blocks"] = blocks

  return modal

def get_test_config_blocks(hash: str, test: TestConfig):
  if test.type == T_SINGLE:
    return get_test_config_blocks_signle(hash, test)
  elif test.type == T_MULTI:
    return get_test_config_blocks_multi(hash, test)
  return []

def get_test_config_blocks_signle(hash: str, test: TestConfigSignle):
  return [
    {
      "type": "input",
      "block_id": hash,
      "label": {
        "type": "plain_text",
        "text": test.question,
      },
      "element": {
        "type": "radio_buttons",
        "action_id": "signle_test_ans",
        "options": [get_test_option(opt_hash, test.variants[opt_hash]) for opt_hash in random.sample(list(test.variants.keys()), len(test.variants))]
      },
    },
  ]

def get_test_option(hash: str, opt: str):
  return {
    "value": hash,
    "text": {
      "type": "plain_text",
      "text": opt
    }
  }

def get_test_config_blocks_multi(hash: str, test: TestConfigMulti):
  variants = {**test.correct, **test.incorrect}
  return [
    {
      "type": "input",
      "block_id": hash,
      "label": {
        "type": "plain_text",
        "text": test.question,
      },
      "element": {
        "type": "checkboxes",
        "action_id": "multi_test_ans",
        "options": [get_test_option(opt_hash, variants[opt_hash]) for opt_hash in random.sample(list(variants.keys()), len(variants))]
      },
    },
  ]

async def modal_take_test_callback(context, body, logger, client: WebClient, ack: Ack):  
  logic: AppLogic = context["logic"]
  user_id = body["user"]["id"]
  event_id = int(body["view"]["private_metadata"])
  
  answers: dict[str, list[str]] = {}
  modal_values = body["view"]["state"]["values"]
  for hash, value in modal_values.items():
    if "signle_test_ans" in value:
      answers[hash] = {"var_hash":value["signle_test_ans"]["selected_option"]["value"]}
    elif "multi_test_ans" in value:
      answers[hash] = {"vars_hash": [opt["value"] for opt in value["multi_test_ans"]["selected_options"]]}

  submition_id = await handle_user_submission(logic, event_id, user_id, answers, client)
  if submition_id is None:
    await ack(response_action="errors", errors={"signle_test_ans": "You can not submit test", "multi_test_ans": "You can not submit test"})
    return

  await ack()

async def handle_submit_assignment(context, body, logger, client: WebClient, ack: Ack):
  logic: AppLogic = context["logic"]

  user_id: str = body["user"]["id"]
  if not logic.course.get_user(user_id).is_learner():
    await ack(response_action="errors", errors={"event_block": "You are not a learner"})
    logger.warning(f"{user_id} is not a learner to submit assignment")
    return
  
  await ack()

  logger.info(body)
  event_id = int(body["actions"][0]["value"])
  event: Event = logic.course.get_event(event_id)

  if event.type != E_ASSIGNMENT:
    logger.error(f"try to start submition from event {event_id} but it is not an assignment event")

  resp = await client.views_open(
      trigger_id=body["trigger_id"],
      view=get_submit_assignment_modal(event)
  )

def get_submit_assignment_modal(event: AssignmentEvent):
  modal = {
    "type": "modal",
    "callback_id": "view_submit_assignment",
    "title": {
      "type": "plain_text",
      "text": event.name
    },
    "submit": {
      "type": "plain_text",
      "text": "Submit"
    },
    "close": {
      "type": "plain_text",
      "text": "Cancel"
    },
    "private_metadata": f"{event.id}",
    "blocks": [
      {
        "type": "input",
        "block_id": "file_submission",
        "label": {
          "type": "plain_text",
          "text": "Submit assignment"
        },
        "element": {
          "type": "file_input",
          "action_id": "submitted_assignment",
          "filetypes": [
            "doc",
            "docx",
            "pdf",
            "jpg",
            "png",
            "gzip",
          ],
          "max_files": 1
        }
      },
    ]
  }

  return modal

async def modal_submit_assignment_callback(context, body, logger, client: WebClient, ack: Ack):
  await ack()
  
  logic: AppLogic = context["logic"]
  user_id = body["user"]["id"]
  event_id = int(body["view"]["private_metadata"])
  modal_values = body["view"]["state"]["values"]

  if await handle_user_submission(logic, event_id, user_id, {"files": modal_values["file_submission"]["submitted_assignment"]["files"]}, client) is None:
    await ack(response_action="errors", errors={"file_submission": "Can't make submition"})
    return

  await ack()

async def handle_user_submission(logic: AppLogic, event_id: int, user_id: str, submition, client: WebClient):
  submition_id = logic.event_submition(event_id, user_id, submition)
  if submition_id is None:
    return None
  
  await update_home_teachers_user(logic, user_id, client)
  await notify_teachers(logic, submition_id, client)
  
  if logic.course.submitions_by_id[submition_id][2].get("result", None) is not None:
    await client.chat_postMessage(channel=user_id, blocks=get_submition_message_blocks(logic, submition_id))
  
  return submition_id

async def notify_teachers(logic: AppLogic, submition_id: int, client: WebClient):
  for user in logic.course.users.values():
    if user.is_teacher():
      await client.chat_postMessage(channel=user.platform_id, blocks=get_submition_message_blocks(logic, submition_id))

async def handle_enter_class(context, body, logger, client: WebClient, ack: Ack):
  await ack()
  logger.info(f"user {body['user']['id']} go to class")
  # TODO: track enter class
