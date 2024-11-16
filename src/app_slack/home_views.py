from slack_sdk import WebClient
from slack_bolt import Ack

from course_classes import *
from app_logic_api import *

async def update_home_techers_user(logic: AppLogic, user_id: str, client: WebClient):
  for user in logic.course.users.values():
    if user.platform_id == user_id or user.is_teacher():
      try:
        await client.views_publish(
            user_id=user.platform_id,
            view=get_home_view(user, logic)
        )
      except Exception as e:
        logger.error(f"Error publishing home tab: {e}")

async def update_home_views(logic: AppLogic, client):
  for user in logic.course.users.values():
    await client.views_publish(
        user_id=user.platform_id,
        view=get_home_view(user, logic)
    )

def get_home_view(user: User, logic: AppLogic):
  blocks = []
  if user.is_teacher(): # TODO: more home views & rewrite to modals
    blocks = get_teacher_blocks(user, logic)
  elif user.is_learner():
    blocks = get_default_blocks(user, logic)
  else:
    blocks = get_default_blocks(user, logic)
  
  return {
      "type": "home",
      "callback_id": "home_view",
      "blocks": blocks,
  }

def get_default_blocks(user: User, logic: AppLogic):
  return [
      {
          "type": "section",
          "text": {
              "type": "plain_text",
              "text": f"*Welcome to your _App's Home tab_* :tada: {user.platform_id}!"
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

def get_teacher_blocks(user: User, logic: AppLogic):
  blocks = [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": f"{logic.course.name} :books:"
      }
    },
    *get_course_status_blocks(logic),
		{
			"type": "divider"
		},
    *get_events_section_blocks(logic),
		{
			"type": "divider"
		},
    *get_users_section_blocks(logic),
		{
			"type": "divider"
		},
    *get_submitions_section_blocks(logic),
  ]

  return blocks

def get_course_status_str(logic: AppLogic):
  if not logic.is_can_start_course():
    return "Please add needed events!"
  elif not logic.is_in_process():
    return "You can start course now!"
  else:
    return "Course works!"

def get_course_status_blocks(logic: AppLogic):
  blocks = [
    {
      "type": "section",
      "text": {
        "type": "plain_text",
        "text": get_course_status_str(logic)
      },
    },
  ]

  if not logic.is_in_process() and logic.is_can_start_course():
    blocks[0]["accessory"] = {
      "type": "button",
      "style": "primary",
      "text": {
        "type": "plain_text",
        "text": "Start course",
      },
      "action_id": "click_start_course"
    }

  return blocks

def get_events_section_blocks(logic: AppLogic):
  return [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"Events in course now: *{len(logic.course.events)}*"
      },
      "accessory": {
        "type": "button",
        "style": "primary",
        "text": {
          "type": "plain_text",
          "text": "Manage events",
        },
        "action_id": "manage_events"
      }
    },
  ]

def get_users_section_blocks(logic: AppLogic):
  teachers_c = 0
  learners_c = 0
  for user in logic.course.users.values():
    if user.is_teacher():
      teachers_c += 1
    elif user.is_learner():
      learners_c += 1
      
  return [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"Users on course: *Teachers:* {teachers_c}, *Learners:* {learners_c}"
      },
      "accessory": {
        "type": "button",
        "style": "primary",
        "text": {
          "type": "plain_text",
          "text": "Manage users",
        },
        "action_id": "manage_users"
      }
    },
  ]

def get_submitions_section_blocks(logic: AppLogic):
  return [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"Submitions: not graded - *{logic.course.get_all_ungraded_submitions()}*"
      },
      "accessory": {
        "type": "button",
        "style": "primary",
        "text": {
          "type": "plain_text",
          "text": "Manage submitions",
        },
        "action_id": "manage_submitions"
      }
    },
  ]

async def handle_manage_events(context, client: WebClient, ack: Ack, body, logger):
  await ack()
  logic: AppLogic = context["logic"]

  resp = await client.views_open(
      trigger_id=body["trigger_id"],
      view=get_manage_events_modal(logic)
  )

def get_manage_events_modal(logic: AppLogic):
  return {
    "type": "modal",
    "callback_id": "view_manage_events",
    "title": {
      "type": "plain_text",
      "text": "Manage events"
    },
    "close": {
      "type": "plain_text",
      "text": "Close"
    },
    "blocks": [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": f"Events in course now: *{len(logic.course.events)}*"
        },
        "accessory": {
          "type": "button",
          "style": "primary",
          "text": {
            "type": "plain_text",
            "text": "Add event",
          },
          "action_id": "click_add_event"
        }
      },
      {
        "type": "divider"
      },
      *get_events_list_blocks(logic),
    ]
  }
  
def get_events_list_blocks(logic: AppLogic):
  blocks = []
  for event in logic.course.events.values():
    blocks += get_event_fields(event)
  return blocks

def get_event_fields(event: Event) -> list:
  return [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"*Event type:* {event_types_str[event.type]}, *Event name:* {event.name}, *Date:* {event.start_time}"
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
          "value": f"{event.id}",
          "action_id": "click_edit_event"
        },
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "Remove",
          },
          "style": "danger",
          "value": f"{event.id}",
          "action_id": "click_remove_event"
        },
      ]
    },
    {
      "type": "divider",
    },
  ]

async def handle_manage_users(context, client: WebClient, ack: Ack, body, logger):
  await ack()
  logic: AppLogic = context["logic"]

  resp = await client.views_open(
      trigger_id=body["trigger_id"],
      view=get_manage_users_modal(logic)
  )

def get_manage_users_modal(logic: AppLogic):
  teachers: list[User] = []
  learners: list[User] = []
  for user in logic.course.users.values():
    if user.is_teacher():
      teachers.append(user)
    elif user.is_learner():
      learners.append(user)

  return {
    "type": "modal",
    "callback_id": "view_manage_users",
    "title": {
      "type": "plain_text",
      "text": "Manage users"
    },
    "close": {
      "type": "plain_text",
      "text": "Close"
    },
    "blocks": [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
        "text": f"Users on course: *Teachers:* {len(teachers)}, *Learners:* {len(learners)}"
        },
      },
      {
        "type": "divider"
      },
      *get_users_list_blocks(logic, teachers, learners),
    ]
  }
  
def get_users_list_blocks(logic: AppLogic, teachers: list[User], learners: list[User]):
  blocks = [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"*Teachers:* {len(teachers)}"
      },
      "accessory": {
        "type": "button",
        "style": "primary",
        "text": {
          "type": "plain_text",
          "text": "Add teacher",
        },
        "value": f"{user_roles_to_code[U_TEACHER]}",
        "action_id": "click_add_user"
      }
    },
  ]

  for user in teachers:
    blocks += get_user_fields(user)

  blocks += [
    {
      "type": "divider"
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"*Learners:* {len(learners)}"
      },
      "accessory": {
        "type": "button",
        "style": "primary",
        "text": {
          "type": "plain_text",
          "text": "Add learner",
        },
        "value": f"{user_roles_to_code[U_LEARNER]}",
        "action_id": "click_add_user"
      }
    },
  ]

  for user in learners:
    blocks += get_user_fields(user)
  
  return blocks

def get_user_fields(user: User):
  return [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"*Username:* {user.name}, *Role:* {user_roles_str[user.role]}"
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
          "value": f"{user.platform_id}",
          "action_id": "click_edit_user"
        },
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "Remove",
          },
          "style": "danger",
          "value": f"{user.platform_id}",
          "action_id": "click_remove_user"
        },
      ]
    },
    {
      "type": "divider",
    },
  ]

async def handle_add_user(client: WebClient, ack: Ack, body, logger):
  await ack()
  role: int = user_roles_from_code[body["actions"][0]["value"]]
  resp = await client.views_push(
      trigger_id=body["trigger_id"],
      view=get_add_user_modal(role)
  )

def get_add_user_modal(role: int):
  return {
    "type": "modal",
    "callback_id": "view_add_users",
    "private_metadata": user_roles_to_code[role],
    "title": {
      "type": "plain_text",
      "text": f"Add {'learners' if role == U_LEARNER else 'teachers'}"
    },
    "submit": {
      "type": "plain_text",
      "text": "Submit"
    },
    "close": {
      "type": "plain_text",
      "text": "Close"
    },
    "blocks": [
      {
        "type": "input",
        "block_id": "users_select",
        "label": {
          "type": "plain_text",
          "text": "Select users to add:"
        },
        "element": {
          "type": "multi_external_select",
          "action_id": "users",
          "min_query_length": 0,
          "placeholder": {
            "type": "plain_text",
            "text": "Select users"
          },
        },
      }
    ]
  }

async def users_options(ack, context, body):
  logic: AppLogic = context["logic"]
  role: int = user_roles_from_code[body["view"]["private_metadata"]]
  await ack({"options": get_users_model(role, logic)})

def get_users_model(role: int, logic: AppLogic):
  model = []
  for user in logic.course.users.values():
    if user.role < role:
      model.append(get_user_option(user))
  return model

async def learners_options(ack, context, body):
  logic: AppLogic = context["logic"]
  await ack({"options": get_learners_model(logic)})

def get_learners_model(logic: AppLogic):
  model = []
  for user in logic.course.users.values():
    if user.is_learner():
      model.append(get_user_option(user))
  return model

def get_user_option(user: User):
  return {
    "text": {
      "type": "plain_text",
      "text": f"{user.name} - {user_roles_str[user.role]}",
      "emoji": True
    },
    "value": user.platform_id
  }

async def modal_add_users_callback(ack: Ack, context, body, client: WebClient):
  await ack()
  logic: AppLogic = context["logic"]
  role: int = user_roles_from_code[body["view"]["private_metadata"]]
  
  users: list[str] = []
  for option in body["view"]["state"]["values"]["users_select"]["users"]["selected_options"]:
    users.append(option["value"])
  
  logic.update_users_role(role, users)
  logic.update_users()
  await client.views_update(
      view_id=body["view"]["previous_view_id"],
      view=get_manage_users_modal(logic)
  )

async def handle_remove_user(client: WebClient, ack: Ack, body, logger, context):
  await ack()
  logic: AppLogic = context["logic"]
  user_id = body["actions"][0]["value"]
  
  user: User = logic.course.get_user(user_id)
  if user is not None and user.role != U_MASTER:
    logic.update_users_role(U_GUEST, [user_id])
    logic.update_users()
    resp = await client.views_update(
        view_id=body["view"]["id"],
        view=get_manage_users_modal(logic)
    )

async def handle_edit_user(client: WebClient, ack: Ack, body, logger, context):
  await ack()
  logic: AppLogic = context["logic"]
  user_id = body["actions"][0]["value"]
  resp = await client.views_push(
      trigger_id=body["trigger_id"],
      view=get_edit_user_modal(logic.course.get_user(user_id))
  )

async def modal_edit_user_callback(ack: Ack, context, body, client: WebClient):
  await ack()
  logic: AppLogic = context["logic"]
  user_id: str = body["view"]["private_metadata"]
  
  username: str = body["view"]["state"]["values"]["user_name_input"]["user_name"]["value"]

  user: User = logic.course.get_user(user_id)
  if user is not None and user.name != username:
    user.name = username
    logic.update_users()
    await client.views_update(
        view_id=body["view"]["previous_view_id"],
        view=get_manage_users_modal(logic)
    )

def get_edit_user_modal(user: User):
  return {
    "type": "modal",
    "callback_id": "view_edit_user",
    "private_metadata": user.platform_id,
    "title": {
      "type": "plain_text",
      "text": f"Edit user {user.name}"
    },
    "submit": {
      "type": "plain_text",
      "text": "Submit"
    },
    "close": {
      "type": "plain_text",
      "text": "Close"
    },
    "blocks": [
      {
        "type": "input",
        "block_id": "user_name_input",
        "element": {
          "type": "plain_text_input",
          "action_id": "user_name",
          "min_length": 5,
          "max_length": 255,
          "initial_value": user.name,
          "placeholder": {
            "type": "plain_text",
            "text": "Enter username"
          },
        },
        "label": {
          "type": "plain_text",
          "text": "User name",
        },
      },
    ]
  }

async def handle_manage_submitions(context, client: WebClient, ack: Ack, body, logger):
  await ack()
  logic: AppLogic = context["logic"]

  resp = await client.views_open(
      trigger_id=body["trigger_id"],
      view=get_manage_submitions_modal(logic)
  )

def get_manage_submitions_modal(logic: AppLogic):
  return {
    "type": "modal",
    "callback_id": "view_manage_submitions",
    "title": {
      "type": "plain_text",
      "text": "Manage submitions"
    },
    "close": {
      "type": "plain_text",
      "text": "Close"
    },
    "blocks": [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": f"Submitions: not graded - *{logic.course.get_all_ungraded_submitions()}*"
        },
        "accessory": {
          "type": "button",
          "style": "primary",
          "text": {
            "type": "plain_text",
            "text": "Add submition",
          },
          "action_id": "click_add_submition"
        }
      },
      {
        "type": "divider"
      },
      *get_submitions_list_blocks(logic),
    ]
  }
  
def get_submitions_list_blocks(logic: AppLogic):
  blocks = []

  if len(logic.course.submitions) == 0:
    blocks.append({
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"*No submitions*"
      }
    })
  else:
    for event_id, submitions in logic.course.submitions.items():
      blocks += get_event_submitions_fields(logic, event_id, submitions)
  
  return blocks

def get_event_submitions_fields(logic: AppLogic, event_id: int, submitions: dict):
  event: Event = logic.course.get_event(event_id)
  if event is None:
    return []
  
  not_graded_c = 0
  for submition in submitions.values():
    if submition.get("result", None) is None:
      not_graded_c += 1
  
  return [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"*Event:* {event.name}, *Submitions:* {len(submitions)}, *Not graded:* {not_graded_c}"
      },
      "accessory": {
        "type": "button",
        "style": "primary",
        "text": {
          "type": "plain_text",
          "text": "Show submitions",
        },
        "value": f"{event_id}",
        "action_id": "click_show_submitions_per_event"
      }
    },
    {
      "type": "divider"
    },
  ]


async def handle_add_submition(client: WebClient, ack: Ack, body, logger):
  await ack()
  resp = await client.views_push(
      trigger_id=body["trigger_id"],
      view=get_add_submition_modal()
  )

def get_add_submition_modal():
  return {
    "type": "modal",
    "callback_id": "view_add_submition",
    "title": {
      "type": "plain_text",
      "text": f"Add manual submition"
    },
    "submit": {
      "type": "plain_text",
      "text": "Submit"
    },
    "close": {
      "type": "plain_text",
      "text": "Close"
    },
    "blocks": [
      {
        "type": "input",
        "block_id": "event_select",
        "label": {
          "type": "plain_text",
          "text": "Select event to submit:"
        },
        "element": {
          "type": "external_select",
          "action_id": "event",
          "min_query_length": 0,
          "placeholder": {
            "type": "plain_text",
            "text": "Select event"
          },
        },
      },
      {
        "type": "input",
        "block_id": "user_select",
        "label": {
          "type": "plain_text",
          "text": "Select user:"
        },
        "element": {
          "type": "external_select",
          "action_id": "learners",
          "min_query_length": 0,
          "placeholder": {
            "type": "plain_text",
            "text": "Select user"
          },
        },
      },
      {
        "type": "input",
        "block_id": "submition_info_input",
        "label": {
          "type": "plain_text",
          "text": "Submition description:"
        },
        "element": {
          "type": "plain_text_input",
          "action_id": "submition_info",
          "min_length": 5,
          "max_length": 255,
          "placeholder": {
            "type": "plain_text",
            "text": "Enter submition info"
          },
        },
      },
      {
        "type": "input",
        "block_id": "submition_result_input",
        "element": {
          "type": "number_input",
          "is_decimal_allowed": False,
          "action_id": "submition_result",
          "placeholder": {
            "type": "plain_text",
            "text": "Enter submition grade"
          },
          "min_value": "0",
          "max_value": "100"
        },
        "label": {
          "type": "plain_text",
          "text": "Submition grade:"
        }
      },
    ]
  }

async def event_options(ack, context, body):
  logic: AppLogic = context["logic"]
  await ack({"options": get_events_model(logic)})

def get_events_model(logic: AppLogic):
  model = []
  for event in logic.course.events.values():
    model.append(get_event_option(event))
  return model

def get_event_option(event: Event):
  return {
    "text": {
      "type": "plain_text",
      "text": f"{event.name} - {event_types_str[event.type]}",
      "emoji": True
    },
    "value": f"{event.id}"
  }

async def modal_add_submition_callback(ack: Ack, context, body, client: WebClient): # TODO: it can write existed submitions, rewrite to arrays
  await ack()
  logic: AppLogic = context["logic"]
  modal_values = body["view"]["state"]["values"]

  submitter: str = body["user"]["id"]
  event_id: int = int(modal_values["event_select"]["event"]["selected_option"]["value"])
  user_id: str = modal_values["user_select"]["learners"]["selected_option"]["value"]
  submition_info: str = modal_values["submition_info_input"]["submition_info"]["value"]
  result: int = int(modal_values["submition_result_input"]["submition_result"]["value"])

  logic.event_submition(event_id, user_id, {"info": submition_info, "submitter": submitter}, result)
  
  await client.views_update(
      view_id=body["view"]["previous_view_id"],
      view=get_manage_submitions_modal(logic)
  )

async def handle_show_submitions_per_event(client: WebClient, ack: Ack, body, logger, context):
  await ack()
  logic: AppLogic = context["logic"]
  event_id: int = int(body["actions"][0]["value"])
  resp = await client.views_push(
      trigger_id=body["trigger_id"],
      view=get_submitions_per_event_modal(logic, event_id)
  )

def get_submitions_per_event_modal(logic: AppLogic, event_id: int):
  event: Event = logic.course.get_event(event_id)
  if event is None or logic.course.submitions.get(event_id, None) is None:
    return {}
  
  not_graded: dict[str, dict] = {}
  graded: dict[str, dict] = {}
  for user_id, submition in logic.course.submitions[event_id].items():
    if submition.get("result", None) is None:
      not_graded.update({user_id: submition})
    else:
      graded.update({user_id: submition})
  
  return {
    "type": "modal",
    "callback_id": "view_submitions_per_event",
    "private_metadata": f"{event_id}",
    "title": {
      "type": "plain_text",
      "text": f"Submitions per event"
    },
    "close": {
      "type": "plain_text",
      "text": "Close"
    },
    "blocks": [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": f"Event {event.name} - {event_types_str[event.type]}"
        },
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": f"Not graded submitions - *{len(not_graded)}*"
        },
      },
      *get_users_submitions_block(logic, not_graded),
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": f"Graded submitions - *{len(graded)}*"
        },
      },
      *get_users_submitions_block(logic, graded),
    ]
  }

def get_users_submitions_block(logic: AppLogic, submitions: dict[str, dict]):
  blocks = []
  if len(submitions) == 0:
    blocks.append({
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": f"*No submitions*"
        },
    })
  else:
    for user_id, submition in submitions.items():
      user: User = logic.course.get_user(user_id)
      blocks += get_submition_blocks(logic, user, submition)
    
  return blocks

def get_submition_blocks(logic: AppLogic, user: User, submition: dict):
  submited_by = "by user"
  if submition["submition"].get("submitter", None) is not None:
    submited_by = f"by {logic.course.get_user(submition['submition']['submitter']).name}"

  result = submition.get("result", None)

  return [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"{user.name}, {submited_by}{', grade: *{}*'.format(result) if result is not None else ''}{', have files' if submition.get('files', None) is not None else ''}"
      },
      "accessory": {
          "type": "button",
          "style": "primary",
          "text": {
            "type": "plain_text",
            "text": "See submition",
          },
          "value": user.platform_id,
          "action_id": "click_see_submition" # TODO: add handle
      }
    },
  ]
