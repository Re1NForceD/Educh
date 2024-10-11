import app_slack

import os
import logging


if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)

  # TODO: form config from env
  app_config = {
    "SLACK_BOT_TOKEN": os.environ.get("SLACK_BOT_TOKEN"),
    "SLACK_APP_TOKEN": os.environ.get("SLACK_APP_TOKEN")
  }

  slack_app = app_slack.init_slack_app(app_config)
  slack_app.start()

  # app_logic = app_logic(app_config)
  # slack_module = slack_module(app_logic)
  