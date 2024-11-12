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
        "text": f"Users on Course: *Teachers:* {teachers_c}, *Learners:* {learners_c}"
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
    "callback_id": "view_event_setup",
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
  ) # TODO update modals on users updates

async def handle_manage_submitions(context, client: WebClient, ack: Ack, body, logger):
  await ack()
  logic: AppLogic = context["logic"]

  resp = await client.views_open(
      trigger_id=body["trigger_id"],
      view=get_manage_submitions_modal(logic)
  ) # TODO update modals on submition updates
