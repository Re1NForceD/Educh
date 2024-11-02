from course_classes import *
from app_logic_api import *

def update_home_views(logic: AppLogic, client):
  for user in logic.course.users.values():
    if user.is_teacher():
      client.views_publish(
          user_id=user.platform_id,
          view=get_home_view(user, logic)
      )

def get_home_view(user: User, logic: AppLogic):
  blocks = []

  is_teacher = user.is_teacher()
  is_need_setup_events = logic.is_need_setup_events()
  logger.info(f"setup home view params: {is_teacher}, {is_need_setup_events}")
  
  blocks = []
  if is_teacher: # TODO
    blocks = get_events_setup_blocks(user, logic)
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

def get_events_setup_blocks(user: User, logic: AppLogic):
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
    *get_events_list(logic),
  ]

def get_events_list(logic: AppLogic):
  blocks = [
    {
      "type": "section",
      "text": {
        "type": "plain_text",
        "text": f"Events in course now: {len(logic.course.events)}"
      }
    },
  ]

  if not logic.is_need_setup_events():
    blocks[0]["accessory"] = {
      "type": "button",
      "style": "primary",
      "text": {
        "type": "plain_text",
        "text": "Continue course setup",
      },
      "action_id": "click_event_setup_finished"
    }

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
