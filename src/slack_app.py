import app_slack
import app_logic_api

import os
import logging


if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)

  # TODO: form config from env
  app_config = {
    "SLACK_BOT_TOKEN": os.environ.get("SLACK_BOT_TOKEN"),
    "SLACK_APP_TOKEN": os.environ.get("SLACK_APP_TOKEN"),
  }
  logic_config = {
    "SERVER_ADDRESS": "http://localhost:9999",
    "AUTH_KEY": "MStkR1Z6ZEY5amIzVnljMlU9",
  }

  app_logic = app_logic_api.AppLogic(logic_config)
  slack_app = app_slack.init_slack_app(app_config, app_logic)
  slack_app.start()
  