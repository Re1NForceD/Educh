from course_classes import *
from app_logic_api import *

def get_home_view(user: User, logic: AppLogic):
  blocks = []

  is_teacher = user.is_teacher()
  is_need_setup_events = logic.is_need_setup_events()
  logger.info(f"setup home view params: {is_teacher}, {is_need_setup_events}")

  if is_teacher: # TODO
    if is_need_setup_events:
      blocks = get_events_setup_blocks(user, logic)
    else:
      pass
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
