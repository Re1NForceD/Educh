def update_home_tab(client, event, logger):
  try:
    # views.publish is the method that your app uses to push a view to the Home tab
    client.views_publish(
        # the user that opened your app's app home
        user_id=event["user"],
        # the view object that appears in the app home
        view={
            "type": "home",
            "callback_id": "home_view",

            # body of the view
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Welcome to your _App's Home tab_* :tada:"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app."
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Click me!"
                            },
                            "action_id": "button_click"
                        }
                    ]
                }
            ]
        }
    )

  except Exception as e:
    logger.error(f"Error publishing home tab: {e}")


def handle_button_click(ack, client, body, logger):
  ack()
  logger.info(body)
  client.chat_postMessage(
      channel=body["user"]["id"],
      text=f"<@{body['user']['id']}> clicked the button"
  )


def register_app_events(app):
  app.event("app_home_opened")(update_home_tab)
  app.action("button_click")(handle_button_click)