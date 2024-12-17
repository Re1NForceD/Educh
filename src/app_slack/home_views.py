from slack_sdk import WebClient
from slack_bolt import Ack

from course_classes import *
from app_logic_api import *

async def update_home_teachers_user(logic: AppLogic, user_id: str, client: WebClient):
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
    await update_home_view(user, logic, client)

async def update_home_view(user: User, logic: AppLogic, client):
    await client.views_publish(
        user_id=user.platform_id,
        view=get_home_view(user, logic)
    )

def get_home_view(user: User, logic: AppLogic):
  blocks = []
  if user.is_teacher(): # TODO: more home views & rewrite to modals
    blocks = get_teacher_blocks(user, logic)
  elif user.is_learner():
    blocks = get_learner_blocks(user, logic)
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
              "type": "mrkdwn",
              "text": f"*Welcome to your _Educh Home tab_* <@{user.platform_id}>!"
          }
      },
      {
          "type": "divider"
      },
      {
          "type": "section",
          "text": {
              "type": "plain_text",
              "text": "You are not a teacher, nor a learner."
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
    *get_submissions_section_blocks(logic),
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

def get_submissions_section_blocks(logic: AppLogic):
  return [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"Submissions: not graded - *{logic.course.get_all_ungraded_submissions()}*"
      },
      "accessory": {
        "type": "button",
        "style": "primary",
        "text": {
          "type": "plain_text",
          "text": "Manage submissions",
        },
        "action_id": "manage_submissions"
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
  blocks = [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"*Username:* {user.name}, *Role:* {user_roles_str[user.role]}"
      }
    },
  ]

  if user.is_learner() or (user.is_teacher() and user.role != U_MASTER):
    blocks.append({
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
        }
      ]
    })
  
  blocks.append(
    {
      "type": "divider",
    }
  )
  
  return blocks

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

  for user_id in users:
    user: User = logic.course.get_user(user_id)
    if user is not None:
      await update_home_view(user, logic, client)
    await client.chat_postMessage(channel=user.platform_id, text=f"You are a {user_roles_str[role]} now")

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
    await update_home_view(user, logic, client)
    resp = await client.views_update(
        view_id=body["view"]["id"],
        view=get_manage_users_modal(logic)
    )
    await client.chat_postMessage(channel=user.platform_id, text=f"You are a {user_roles_str[U_GUEST]} now")

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

async def handle_manage_submissions(context, client: WebClient, ack: Ack, body, logger):
  await ack()
  logic: AppLogic = context["logic"]

  resp = await client.views_open(
      trigger_id=body["trigger_id"],
      view=get_manage_submissions_modal(logic)
  )

def get_manage_submissions_modal(logic: AppLogic):
  return {
    "type": "modal",
    "callback_id": "view_manage_submissions",
    "title": {
      "type": "plain_text",
      "text": "Manage submissions"
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
          "text": f"Submissions: not graded - *{logic.course.get_all_ungraded_submissions()}*"
        },
        "accessory": {
          "type": "button",
          "style": "primary",
          "text": {
            "type": "plain_text",
            "text": "Add submission",
          },
          "action_id": "click_add_submission"
        }
      },
      {
        "type": "divider"
      },
      *get_submissions_list_blocks(logic),
    ]
  }
  
def get_submissions_list_blocks(logic: AppLogic):
  blocks = []

  if len(logic.course.submissions) == 0:
    blocks.append({
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"*No submissions*"
      }
    })
  else:
    for event_id, submissions in logic.course.submissions.items():
      blocks += get_event_submissions_fields(logic, event_id, submissions)
  
  return blocks

def get_event_submissions_fields(logic: AppLogic, event_id: int, submissions: dict):
  event: Event = logic.course.get_event(event_id)
  if event is None:
    return []
  
  not_graded_c = 0
  for submission in submissions.values():
    if submission.get("result", None) is None:
      not_graded_c += 1
  
  return [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"*Event:* {event.name}, *Submissions:* {len(submissions)}, *Not graded:* {not_graded_c}"
      },
      "accessory": {
        "type": "button",
        "style": "primary",
        "text": {
          "type": "plain_text",
          "text": "Show submissions",
        },
        "value": f"{event_id}",
        "action_id": "click_show_submissions_per_event"
      }
    },
    {
      "type": "divider"
    },
  ]

async def handle_add_submission(client: WebClient, ack: Ack, body, logger):
  await ack()
  resp = await client.views_push(
      trigger_id=body["trigger_id"],
      view=get_add_submission_modal()
  )

def get_add_submission_modal():
  return {
    "type": "modal",
    "callback_id": "view_add_submission",
    "title": {
      "type": "plain_text",
      "text": f"Add manual submission"
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
        "block_id": "submission_info_input",
        "label": {
          "type": "plain_text",
          "text": "Submission description:"
        },
        "element": {
          "type": "plain_text_input",
          "action_id": "submission_info",
          "min_length": 5,
          "max_length": 255,
          "placeholder": {
            "type": "plain_text",
            "text": "Enter submission info"
          },
        },
      },
      {
        "type": "input",
        "block_id": "submission_result_input",
        "element": {
          "type": "number_input",
          "is_decimal_allowed": False,
          "action_id": "submission_result",
          "placeholder": {
            "type": "plain_text",
            "text": "Enter submission grade"
          },
          "min_value": "0",
          "max_value": "100"
        },
        "label": {
          "type": "plain_text",
          "text": "Submission grade:"
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

async def modal_add_submission_callback(ack: Ack, context, body, client: WebClient): # TODO: it can write existed submissions, rewrite to arrays
  await ack()
  logic: AppLogic = context["logic"]
  modal_values = body["view"]["state"]["values"]

  submitter_id: str = body["user"]["id"]
  event_id: int = int(modal_values["event_select"]["event"]["selected_option"]["value"])
  user_id: str = modal_values["user_select"]["learners"]["selected_option"]["value"]
  submission_info: str = modal_values["submission_info_input"]["submission_info"]["value"]
  result: int = int(modal_values["submission_result_input"]["submission_result"]["value"])

  submission_id = logic.event_submission(event_id, user_id, {"info": submission_info}, submitter_id, result)
  if submission_id is None:
    await ack(response_action="errors", errors={"user_select": "Can't make submission for this user"})
    return
  
  await ack()
  await client.views_update(
      view_id=body["view"]["previous_view_id"],
      view=get_manage_submissions_modal(logic)
  )

  if logic.course.submissions_by_id[submission_id][2].get("result", None) is not None:
    await client.chat_postMessage(channel=user_id, blocks=get_submission_message_blocks(logic, submission_id))

  await update_home_view(logic.course.get_user(user_id), logic, client)

async def handle_show_submissions_per_event(client: WebClient, ack: Ack, body, logger, context):
  await ack()
  logic: AppLogic = context["logic"]
  event_id: int = int(body["actions"][0]["value"])
  resp = await client.views_push(
      trigger_id=body["trigger_id"],
      view=get_submissions_per_event_modal(logic, event_id)
  )

def get_submissions_per_event_modal(logic: AppLogic, event_id: int):
  event: Event = logic.course.get_event(event_id)
  if event is None or logic.course.submissions.get(event_id, None) is None:
    return {}
  
  not_graded: dict[str, dict] = {}
  graded: dict[str, dict] = {}
  for user_id, submission in logic.course.submissions[event_id].items():
    if submission.get("result", None) is None:
      not_graded.update({user_id: submission})
    else:
      graded.update({user_id: submission})
  
  return {
    "type": "modal",
    "callback_id": "view_submissions_per_event",
    "private_metadata": f"{event_id}",
    "title": {
      "type": "plain_text",
      "text": f"Submissions per event"
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
          "text": f"Not graded submissions - *{len(not_graded)}*"
        },
      },
      *get_users_submissions_block(logic, None, not_graded),
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": f"Graded submissions - *{len(graded)}*"
        },
      },
      *get_users_submissions_block(logic, None, graded),
    ]
  }

def get_users_submissions_block(logic: AppLogic, event: Event, submissions: dict[str, dict]):
  blocks = []
  if len(submissions) == 0:
    blocks.append({
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": f"*No submissions*"
        },
    })
  else:
    for user_id, submission in submissions.items():
      user: User = logic.course.get_user(user_id)
      blocks += get_submission_blocks(logic, event, user, submission)
    
  return blocks

def get_submission_blocks(logic: AppLogic, event: Event, user: User, submission_data: dict):
  submission = submission_data["submission"]
  graded_by = submission_data.get('submitter_id', None)
  result = submission_data.get("result", None)
  id = submission_data.get("id", None)

  return [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"{'Event: *{}*, '.format(event.name) if event is not None else ''}<@{user.platform_id}>{', has files' if submission.get('files', None) is not None else ''}{', grade: *{}*'.format(result) if result is not None else ''}{' by <@{}>'.format(graded_by) if graded_by is not None and result is not None else ''}"
      },
      "accessory": {
          "type": "button",
          "style": "primary",
          "text": {
            "type": "plain_text",
            "text": "See submission",
          },
          "value": f"{id}",
          "action_id": "click_see_submission"
      }
    },
  ]

async def handle_see_submission(client: WebClient, ack: Ack, body, context, logger):
  await ack()
  logic: AppLogic = context["logic"]
  viewer_id = body["user"]["id"]
  viewer: User = logic.course.get_user(viewer_id)
  # event_id: int = int(body["view"]["private_metadata"])

  submission_id: str = int(body["actions"][0]["value"])
  submission = logic.course.submissions_by_id.get(submission_id, None)
  user: User = logic.course.get_user(submission[1])
  if user is None:
    return
  
  if body.get("view", None) is not None and body["view"]["type"] == "modal":
    await client.views_push(
        trigger_id=body["trigger_id"],
        view=get_see_submission_modal(logic, viewer, user, submission[2])
    )
  else:
    await client.views_open(
        trigger_id=body["trigger_id"],
        view=get_see_submission_modal(logic, viewer, user, submission[2])
    )

def get_see_submission_modal(logic: AppLogic, viewer: User, user: User, submission_data):
  submission_id = submission_data["id"]
  result = submission_data["result"]
  modal = {
    "type": "modal",
    "callback_id": "view_see_submission",
    "private_metadata": f"{submission_id}",
    "title": {
      "type": "plain_text",
      "text": f"User's submission"
    },
    "close": {
      "type": "plain_text",
      "text": "Close"
    },
    "blocks": get_user_submission_blocks(user, submission_data)
  }

  if result is None and viewer.is_teacher() and viewer != user:
    modal["submit"] = {
      "type": "plain_text",
      "text": "Submit"
    }

    modal["blocks"] += [
      {
        "type": "input",
        "block_id": "submission_result_input",
        "element": {
          "type": "number_input",
          "is_decimal_allowed": False,
          "action_id": "submission_result",
          "placeholder": {
            "type": "plain_text",
            "text": "Enter submission grade"
          },
          "min_value": "0",
          "max_value": "100"
        },
        "label": {
          "type": "plain_text",
          "text": "Submission grade:"
        }
      }
    ]

  return modal

def get_user_submission_blocks(user: User, submission: dict):
  submission_data = submission["submission"]
  result = submission["result"]
  date = submission.get("date", "*no date*")
  submitter_id = submission.get("submitter_id", None)
  blocks = [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"It is <@{user.platform_id}>'s submission from {date}"
      },
    }
  ]

  info = submission_data.get("info", None)
  if info is not None:
    blocks += [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": f"Submission info: {info}"
        },
      }
    ]

  files = submission_data.get("files", [])
  if len(files) != 0:
    for file in files:
      blocks.append({
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": f"File submission: <{file['permalink']}|{decode_unicode_string(file['name'])}>",
        }
      })

  if result is not None:
    blocks.append({
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"Grade: *{result}*{' by <@{}>'.format(submitter_id) if submitter_id is not None else ''}",
      }
    })

  return blocks

async def modal_see_submission_callback(ack: Ack, context, body, client: WebClient): # TODO: it can write existed submissions, rewrite to arrays
  logic: AppLogic = context["logic"]
  modal_values = body["view"]["state"]["values"]

  submitter_id: str = body["user"]["id"]
  submission_id: int = int(body["view"]["private_metadata"])
  result: int = int(modal_values["submission_result_input"]["submission_result"]["value"])

  updated = logic.grade_event_submission(submitter_id, submission_id, result)
  if not updated:
    await ack(response_action="errors", errors={"submission_result_input": "Can't grade this submission"})
    return

  await ack()
  user_id = logic.course.submissions_by_id[submission_id][1]
  await client.chat_postMessage(channel=user_id, blocks=get_submission_message_blocks(logic, submission_id))
  
  if body["view"]["previous_view_id"] is not None:
    await client.views_update(
      view_id=body["view"]["previous_view_id"],
      view=get_submissions_per_event_modal(logic, logic.course.submissions_by_id[submission_id][0])
    )
  
    await client.views_update(
      view_id=body["view"]["root_view_id"],
      view=get_manage_submissions_modal(logic)
    )

  await update_home_teachers_user(logic, user_id, client)

def get_submission_message_blocks(logic: AppLogic, submission_id: int):
  submission = logic.course.submissions_by_id.get(submission_id, None)
  if submission is None:
    return []
  
  event: Event = logic.course.get_event(submission[0])
  if event is None:
    return []
  
  user: User = logic.course.get_user(submission[1])
  if user is None:
    return []
  
  submission = submission[2]
  
  result = submission.get("result", None)
  submitter_id = submission.get("submitter_id", None)
  result_str = ""
  if result is not None:
    result_str = f"Grade: {result}, by <@{submitter_id}>"

  message_texts = []
  submission_data = submission["submission"]
  if submission_data.get("info", None) is not None:
    message_texts.append(f"info - {submission_data.get('info', None)}")
  if submission_data.get("files", None) is not None:
    message = ["files:"]
    for file in submission_data.get("files", None):
      message.append(f"<{file['permalink']}|file>")
    message_texts.append(" ".join(message))
  
  blocks = [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"<@{user.platform_id}> has submitted for event *{event.name}* - {event_types_str[event.type]}: {', '.join(message_texts)}\n{result_str}",
      },
    },
  ]

  if result is None:
    blocks.append({
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "style": "primary",
          "text": {
            "type": "plain_text",
            "text": "See submission",
          },
          "value": f"{submission_id}",
          "action_id": "click_see_submission"
        }
      ]
    })

  return blocks

def get_learner_blocks(user: User, logic: AppLogic):
  blocks = [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": f"{logic.course.name} :books:"
      }
    },
    {
      "type": "divider"
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"*Course state:* _{'running' if logic.is_in_process() else 'setuping'}_"
      }
    },
    *get_learner_submissions_section_blocks(user, logic),
  ]

  return blocks

def get_learner_submissions_section_blocks(user: User, logic: AppLogic):
  blocks = []
  user_submissions_c = 0
  for submission in logic.course.submissions_by_id.values():
    user_id = submission[1]
    event = logic.course.get_event(submission[0])
    if user.platform_id == user_id:
      user_submissions_c += 1
      blocks += get_submission_blocks(logic, event, user, submission[2])

  return [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "No submissions" if user_submissions_c == 0 else f"Submissions: {user_submissions_c}", # f"*Test type:* _{test_types_str[test.type]}_"
      }
    },
  ] + blocks
