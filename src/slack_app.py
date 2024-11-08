import app_slack
import app_logic_api

import os
import logging


async def main():
  logging.basicConfig(level=logging.DEBUG)
#   logger = logging.getLogger()
#   console_handler = logging.StreamHandler()
# # [2024-10-20 00:17:58] [DEBUG] [client.py:125] Message processing started (type: hello, envelope_id: None)
# # DEBUG:slack_bolt.App:Message processing started (type: hello, envelope_id: None)
#   formatter = logging.Formatter(
#       "[%(asctime)s] %(levelname)s:%(name)s: %(message)s",
#       datefmt="%Y-%m-%d %H:%M:%S",
#   )
#   console_handler.setFormatter(formatter)
#   logger.addHandler(console_handler)

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
  await slack_app.start()

if __name__ == "__main__":
  import asyncio
  asyncio.run(main())
  